import json
import re
from io import BytesIO
from typing import TypedDict, Optional

from PIL import Image
from langgraph.graph import StateGraph, START, END

from config import model
from utils.activity_prompts import (
    RAW_TEXT_EXTRACTION_PROMPT,
    DATE_EXTRACTION_PROMPT,
    TYPE_CLASSIFICATION_PROMPT,
    LOCATION_EXTRACTION_PROMPT,
    MOVIE_EXTRACTION_PROMPT,
    RESTAURANT_EXTRACTION_PROMPT,
    FOOD_ITEMS_EXTRACTION_PROMPT,
    PRICE_EXTRACTION_PROMPT,
    CUISINE_EXTRACTION_PROMPT,
    NORMALIZATION_PROMPT,
)

VALID_TYPES = {
    "Fancy", "Activity", "Drive", "Game", "Food", "Shopping",
    "Chilling", "Movie", "Nightlife", "Attraction", "Nature",
}


class ActivityState(TypedDict):
    image_bytes: bytes
    raw_text: Optional[str]
    date: Optional[str]
    types: list
    location: Optional[str]
    movie_name: Optional[str]
    restaurant_name: Optional[str]
    food_items: list
    total_price: Optional[float]
    cuisine: list
    notes: Optional[str]
    errors: list


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_json(text):
    """Strip markdown code fences and parse JSON. Returns parsed object or None."""
    if not text:
        return None
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _gemini(prompt_or_parts):
    """Call Gemini with text or [image, text]. Returns response text or None."""
    try:
        response = model.generate_content(prompt_or_parts)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


# ── Graph nodes ───────────────────────────────────────────────────────────────

def extract_raw(state: ActivityState) -> dict:
    img = Image.open(BytesIO(state["image_bytes"]))
    raw = _gemini([img, RAW_TEXT_EXTRACTION_PROMPT])
    return {"raw_text": raw or ""}


def extract_date(state: ActivityState) -> dict:
    raw = _gemini(DATE_EXTRACTION_PROMPT.format(raw_text=state["raw_text"]))
    result = _parse_json(raw)
    return {"date": (result or {}).get("date")}


def classify_type(state: ActivityState) -> dict:
    raw = _gemini(TYPE_CLASSIFICATION_PROMPT.format(raw_text=state["raw_text"]))
    result = _parse_json(raw)
    types = [t for t in (result or []) if isinstance(t, str) and t in VALID_TYPES]
    return {"types": types}


def extract_location(state: ActivityState) -> dict:
    raw = _gemini(LOCATION_EXTRACTION_PROMPT.format(raw_text=state["raw_text"]))
    result = _parse_json(raw)
    return {"location": (result or {}).get("location")}


def _route(state: ActivityState) -> str:
    types = state.get("types") or []
    if "Food" in types:
        return "food"
    if "Movie" in types:
        return "movie"
    return "other"


def extract_movie(state: ActivityState) -> dict:
    raw = _gemini(MOVIE_EXTRACTION_PROMPT.format(raw_text=state["raw_text"]))
    result = _parse_json(raw)
    return {"movie_name": (result or {}).get("movie_name")}


def extract_restaurant(state: ActivityState) -> dict:
    raw = _gemini(RESTAURANT_EXTRACTION_PROMPT.format(raw_text=state["raw_text"]))
    result = _parse_json(raw)
    return {"restaurant_name": (result or {}).get("restaurant_name")}


def extract_food_items(state: ActivityState) -> dict:
    raw = _gemini(FOOD_ITEMS_EXTRACTION_PROMPT.format(raw_text=state["raw_text"]))
    result = _parse_json(raw)
    items = result if isinstance(result, list) else []
    return {"food_items": items}


def extract_price_details(state: ActivityState) -> dict:
    raw = _gemini(PRICE_EXTRACTION_PROMPT.format(raw_text=state["raw_text"]))
    result = _parse_json(raw)
    total = (result or {}).get("total_price")
    try:
        total = float(total) if total is not None else None
    except (ValueError, TypeError):
        total = None
    return {"total_price": total}


def extract_cuisine(state: ActivityState) -> dict:
    restaurant = state.get("restaurant_name") or ""
    items_json = json.dumps(state.get("food_items") or [])
    raw = _gemini(CUISINE_EXTRACTION_PROMPT.format(
        restaurant_name=restaurant, food_items=items_json
    ))
    result = _parse_json(raw)
    cuisines = result if isinstance(result, list) else []
    return {"cuisine": cuisines}


def normalize_data(state: ActivityState) -> dict:
    snapshot = {k: v for k, v in state.items() if k != "image_bytes"}
    raw = _gemini(NORMALIZATION_PROMPT.format(state_json=json.dumps(snapshot, default=str)))
    result = _parse_json(raw)
    errors = (result or {}).get("errors", [])
    return {"errors": errors if isinstance(errors, list) else []}


# ── Graph construction ────────────────────────────────────────────────────────

def _build_graph():
    g = StateGraph(ActivityState)

    g.add_node("extract_raw", extract_raw)
    g.add_node("extract_date", extract_date)
    g.add_node("classify_type", classify_type)
    g.add_node("extract_location", extract_location)
    g.add_node("extract_movie", extract_movie)
    g.add_node("extract_restaurant", extract_restaurant)
    g.add_node("extract_food_items", extract_food_items)
    g.add_node("extract_price_details", extract_price_details)
    g.add_node("extract_cuisine", extract_cuisine)
    g.add_node("normalize_data", normalize_data)

    g.add_edge(START, "extract_raw")
    g.add_edge("extract_raw", "extract_date")
    g.add_edge("extract_date", "classify_type")
    g.add_edge("classify_type", "extract_location")
    g.add_conditional_edges(
        "extract_location",
        _route,
        {"food": "extract_restaurant", "movie": "extract_movie", "other": "normalize_data"},
    )
    g.add_edge("extract_restaurant", "extract_food_items")
    g.add_edge("extract_food_items", "extract_price_details")
    g.add_edge("extract_price_details", "extract_cuisine")
    g.add_edge("extract_cuisine", "normalize_data")
    g.add_edge("extract_movie", "normalize_data")
    g.add_edge("normalize_data", END)

    return g.compile()


_graph = None


def run_extraction(image_bytes: bytes) -> dict:
    """
    Run the LangGraph extraction pipeline on raw image bytes.
    Returns the final ActivityState dict. On failure, returns partial state with errors set.
    """
    global _graph
    if _graph is None:
        _graph = _build_graph()

    initial: ActivityState = {
        "image_bytes": image_bytes,
        "raw_text": None,
        "date": None,
        "types": [],
        "location": None,
        "movie_name": None,
        "restaurant_name": None,
        "food_items": [],
        "total_price": None,
        "cuisine": [],
        "notes": None,
        "errors": [],
    }
    try:
        return _graph.invoke(initial)
    except Exception as e:
        print(f"run_extraction error: {e}")
        initial["errors"] = [str(e)]
        return initial
