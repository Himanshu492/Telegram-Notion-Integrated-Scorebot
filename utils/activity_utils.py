import os
import requests
from datetime import datetime
from io import BytesIO

import dotenv
dotenv.load_dotenv()

from config import (
    PAGES_END_POINT, DATA_SOURCE_END_POINT, NOTION_BASE_URL,
    headers, TOKEN, BASE,
)

PLAYER_1 = os.getenv("PLAYER_1")
PLAYER_2 = os.getenv("PLAYER_2")

ACTIVITY_TYPES = [
    "Fancy", "Activity", "Drive", "Game", "Food", "Shopping",
    "Chilling", "Movie", "Nightlife", "Attraction", "Nature",
]
PERSON_OPTIONS = [PLAYER_2, PLAYER_1, "Both"]
FAVOURITE_OPTIONS = ["Yes", "No"]
TIME_OF_DAY_OPTIONS = ["Day", "Night", "Both"]


# ── Date / year helpers ───────────────────────────────────────────────────────

def parse_date_input(text):
    """Parse user date string to YYYY-MM-DD. Accepts DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY."""
    text = (text or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {text}")


def get_year_page_id(date_str):
    """Return the Year relation page ID for a YYYY-MM-DD date string."""
    from utils.database_utils import YEAR_2026_PAGE_ID
    try:
        int((date_str or "")[:4])
    except (ValueError, TypeError):
        return YEAR_2026_PAGE_ID
    return YEAR_2026_PAGE_ID


def validate_activity_data(data):
    """Return a list of missing required field names, or [] if all present."""
    required = {
        "Date Idea": "date_idea",
        "Date": "date",
        "Type": "type",
        "Person": "person",
        "Favourite": "favourite",
        "Time of Day": "time_of_day",
    }
    missing = []
    for label, key in required.items():
        val = data.get(key)
        if not val or (isinstance(val, list) and len(val) == 0):
            missing.append(label)
    return missing


# ── Photo upload helpers ──────────────────────────────────────────────────────

def upload_photo_to_notion(image_bytes, filename="photo.jpg"):
    """
    Upload image bytes to Notion's File Upload API.
    Returns the file_upload_id string, or None on failure.
    """
    url = f"{NOTION_BASE_URL}file_uploads"
    upload_headers = {
        "Notion-Version": headers["Notion-Version"],
        "Authorization": headers["Authorization"],
    }
    try:
        response = requests.post(
            url,
            headers=upload_headers,
            files={"file": (filename, image_bytes, "image/jpeg")},
        )
        response.raise_for_status()
        return response.json().get("id")
    except Exception as e:
        print(f"Notion file upload error: {e}")
        return None


def _download_telegram_photo(photos):
    """
    Download the highest-resolution photo from a Telegram photo array.
    Returns raw bytes. Raises on network error.
    """
    file_id = photos[-1]["file_id"]
    info = requests.get(f"{BASE}/getFile", params={"file_id": file_id})
    info.raise_for_status()
    file_path = info.json()["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    resp = requests.get(file_url, stream=True)
    resp.raise_for_status()
    buf = BytesIO()
    for chunk in resp.iter_content(chunk_size=8192):
        if chunk:
            buf.write(chunk)
    return buf.getvalue()


# ── Restaurant helpers ────────────────────────────────────────────────────────

def find_restaurant_by_name(name):
    """Query Restaurants database by Name. Return page_id or None."""
    from utils.database_utils import RESTAURANTS_DATA_SOURCE_ID
    url = f"{DATA_SOURCE_END_POINT}{RESTAURANTS_DATA_SOURCE_ID}/query"
    payload = {"filter": {"property": "Name", "title": {"equals": name}}}
    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return results[0]["id"] if results else None
    except Exception as e:
        print(f"Error finding restaurant '{name}': {e}")
        return None


def create_restaurant_page(name, cuisine=None, location=None, visited="Yes"):
    """Create a restaurant page. Returns page_id or None."""
    from utils.database_utils import RESTAURANTS_DATA_SOURCE_ID
    properties = {
        "Name": {"title": [{"text": {"content": name}}]},
        "Visited": {"select": {"name": visited}},
        "Favourite": {"select": {"name": "No"}},
    }
    if cuisine:
        properties["Cuisine"] = {"multi_select": [{"name": c} for c in cuisine]}
    if location:
        properties["Location"] = {"location": {"address": location}}

    try:
        resp = requests.post(PAGES_END_POINT, headers=headers, json={
            "parent": {"type": "data_source_id", "data_source_id": RESTAURANTS_DATA_SOURCE_ID},
            "properties": properties,
        })
        resp.raise_for_status()
        return resp.json().get("id")
    except Exception as e:
        print(f"Error creating restaurant '{name}': {e}")
        return None


def find_or_create_restaurant(name, cuisine=None, location=None):
    """Return existing restaurant page_id or create a new one."""
    page_id = find_restaurant_by_name(name)
    if page_id:
        return page_id
    return create_restaurant_page(name, cuisine, location, visited="Yes")


# ── Food Item helpers ─────────────────────────────────────────────────────────

def find_food_item_by_dish(dish_name):
    """Query Food Items database by Dish (title). Return page_id or None."""
    from utils.database_utils import FOOD_DATA_SOURCE_ID
    url = f"{DATA_SOURCE_END_POINT}{FOOD_DATA_SOURCE_ID}/query"
    payload = {"filter": {"property": "Dish", "title": {"equals": dish_name}}}
    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return results[0]["id"] if results else None
    except Exception as e:
        print(f"Error finding food item '{dish_name}': {e}")
        return None


def create_food_item_page(dish, date, person, cuisine=None, favourite="No", year_page_id=None):
    """Create a food item page. Returns page_id or None."""
    from utils.database_utils import FOOD_DATA_SOURCE_ID
    properties = {
        "Dish": {"title": [{"text": {"content": dish}}]},
        "Date": {"date": {"start": date}},
        "Person": {"select": {"name": person}},
        "Favourite": {"select": {"name": favourite}},
        "Type": {"select": {"name": "Dish"}},
    }
    if cuisine:
        properties["Cuisine"] = {"multi_select": [{"name": c} for c in cuisine]}
    if year_page_id:
        properties["Year"] = {"relation": [{"id": year_page_id}]}

    try:
        resp = requests.post(PAGES_END_POINT, headers=headers, json={
            "parent": {"type": "data_source_id", "data_source_id": FOOD_DATA_SOURCE_ID},
            "properties": properties,
        })
        resp.raise_for_status()
        return resp.json().get("id")
    except Exception as e:
        print(f"Error creating food item '{dish}': {e}")
        return None


def find_or_create_food_item(dish, date, person, cuisine=None, favourite="No", year_page_id=None):
    """Return existing food item page_id or create a new one."""
    page_id = find_food_item_by_dish(dish)
    if page_id:
        return page_id
    return create_food_item_page(dish, date, person, cuisine, favourite, year_page_id)


# ── Notion payload / creation ─────────────────────────────────────────────────

def build_activity_summary(data):
    """Return a formatted multi-line summary for the review step."""
    types_str = ", ".join(data.get("type") or []) or "—"
    year = (data.get("date") or "")[:4] or "—"
    lines = [
        "📋 Activity Summary",
        "─────────────────",
        f"Date Idea:   {data.get('date_idea') or '—'}",
        f"Date:        {data.get('date') or '—'}",
        f"Type:        {types_str}",
        f"Person:      {data.get('person') or '—'}",
        f"Favourite:   {data.get('favourite') or '—'}",
        f"Time of Day: {data.get('time_of_day') or '—'}",
        f"Status:      Done (auto)",
        f"Year:        {year} (auto)",
        "─────────────────",
    ]
    if data.get("location"):
        lines.append(f"Location:    {data['location']}")
    if data.get("movie_name"):
        lines.append(f"Movie:       {data['movie_name']}")
    if data.get("restaurant_name"):
        lines.append(f"Restaurant:  {data['restaurant_name']}")
    if data.get("food_items"):
        dishes = [item.get("dish", "?") for item in data["food_items"][:3]]
        suffix = f" +{len(data['food_items']) - 3} more" if len(data["food_items"]) > 3 else ""
        lines.append(f"Food Items:  {', '.join(dishes)}{suffix}")
    if data.get("total_price") is not None:
        lines.append(f"Total:       ${data['total_price']:.2f}")
    if data.get("cuisine"):
        lines.append(f"Cuisine:     {', '.join(data['cuisine'])}")
    lines.append(f"Photo:       {'✓' if data.get('photo_file_upload_id') else '—'}")
    lines.append(f"Notes:       {data.get('notes') or '—'}")
    return "\n".join(lines)


def build_dates_payload(data):
    """Build the Notion page creation payload for the Dates database."""
    from utils.database_utils import ACTIVITIES_DATA_SOURCE_ID
    date_idea = (
        data.get("date_idea")
        or f"{', '.join(data.get('type') or ['Activity'])} - {data.get('date', '')}"
    )
    year_page_id = data.get("year_page_id") or get_year_page_id(data.get("date"))

    properties = {
        "Date Idea": {"title": [{"text": {"content": date_idea}}]},
        "Date": {"date": {"start": data["date"]}},
        "Person": {"select": {"name": data["person"]}},
        "Favourite": {"select": {"name": data["favourite"]}},
        "Status": {"status": {"name": "Done"}},
        "Time of Day": {"select": {"name": data["time_of_day"]}},
        "Type": {"multi_select": [{"name": t} for t in (data.get("type") or [])]},
        "Year": {"relation": [{"id": year_page_id}]},
    }

    if data.get("photo_file_upload_id"):
        properties["Photo"] = {
            "files": [{
                "name": "Photo",
                "type": "file_upload",
                "file_upload": {"id": data["photo_file_upload_id"]},
            }]
        }
    if data.get("notes"):
        properties["Notes"] = {"rich_text": [{"text": {"content": data["notes"]}}]}
    if data.get("location"):
        properties["Location"] = {"location": {"address": data["location"]}}
    if data.get("movie_page_id"):
        properties["Movie"] = {"relation": [{"id": data["movie_page_id"]}]}
    if data.get("restaurant_page_id"):
        properties["Restaurants"] = {"relation": [{"id": data["restaurant_page_id"]}]}
    if data.get("food_item_page_ids"):
        properties["🍽️ Recipe Book"] = {
            "relation": [{"id": pid} for pid in data["food_item_page_ids"]]
        }

    return {
        "parent": {"type": "data_source_id", "data_source_id": ACTIVITIES_DATA_SOURCE_ID},
        "properties": properties,
    }


def create_dates_page(data):
    """
    Orchestrate relation resolution then create the Dates page.
    Mutates data{} with resolved page IDs. Returns page_id or None.
    """
    # 1. Year
    data["year_page_id"] = get_year_page_id(data.get("date"))

    # 2. Movie relation
    if "Movie" in (data.get("type") or []) and data.get("movie_name"):
        from utils.movie_utils import find_or_create_movie_page
        movie_pid = find_or_create_movie_page(data["movie_name"], data.get("person", "Both"))
        if movie_pid:
            data["movie_page_id"] = movie_pid
        else:
            print(f"Movie not resolved: {data['movie_name']} — relation skipped")

    # 3. Restaurant relation
    if "Food" in (data.get("type") or []) and data.get("restaurant_name"):
        rest_pid = find_or_create_restaurant(
            data["restaurant_name"],
            data.get("cuisine"),
            data.get("location"),
        )
        if rest_pid:
            data["restaurant_page_id"] = rest_pid

    # 4. Food item relations
    food_ids = []
    year_pid = data.get("year_page_id")
    for item in (data.get("food_items") or []):
        dish = (item.get("dish") or "").strip()
        if not dish:
            continue
        fid = find_or_create_food_item(
            dish=dish,
            date=data["date"],
            person=data.get("person", "Both"),
            cuisine=data.get("cuisine"),
            favourite=data.get("favourite", "No"),
            year_page_id=year_pid,
        )
        if fid:
            food_ids.append(fid)
    if food_ids:
        data["food_item_page_ids"] = food_ids

    # 5. Create the Dates page
    payload = build_dates_payload(data)
    try:
        resp = requests.post(PAGES_END_POINT, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json().get("id")
    except Exception as e:
        print(f"Error creating Dates page: {e}")
        return None


# ── Main step dispatcher ──────────────────────────────────────────────────────

def handle_add_activity_step(update, pending_entry, send_message_fn, send_keyboard_fn, remove_keyboard_fn):
    """
    Step dispatcher for /add_activity. Mutates pending_entry in place.
    Returns True to keep pending entry alive, False when done or cancelled.
    """
    message = update["message"]
    chat_id = message["chat"]["id"]
    thread_id = message.get("message_thread_id")
    message_id = message["message_id"]
    message_text = (message.get("text") or "").strip()
    step = pending_entry["step"]
    data = pending_entry["data"]

    def reply(text, force_reply=False):
        send_message_fn(chat_id, text, message_thread_id=thread_id,
                        reply_to_message_id=message_id, force_reply=force_reply)

    def kb(text, buttons, one_time=True):
        send_keyboard_fn(chat_id, text, buttons, message_thread_id=thread_id, one_time=one_time)

    def rm_kb(text):
        remove_keyboard_fn(chat_id, text, message_thread_id=thread_id)

    # ── choose_mode ──────────────────────────────────────────────────────────
    if step == "choose_mode":
        if message_text == "Manual Entry":
            data["mode"] = "manual"
            pending_entry["step"] = "ask_date_idea"
            send_message_fn(chat_id,
                            "What's the name/title for this activity? (e.g. Sushi dinner, Movie night)",
                            message_thread_id=thread_id, force_reply=True)
        elif message_text == "Receipt / Ticket Upload":
            data["mode"] = "receipt"
            data["type"] = []
            pending_entry["step"] = "wait_for_receipt"
            send_message_fn(chat_id, "Send a photo of your receipt or ticket.",
                            message_thread_id=thread_id, force_reply=True)
        elif message_text == "Cancel":
            rm_kb("Cancelled. No changes were made.")
            return False
        else:
            kb("How do you want to add this activity?",
               [["Manual Entry"], ["Receipt / Ticket Upload"], ["Cancel"]])
        return True

    # ── wait_for_receipt ─────────────────────────────────────────────────────
    if step == "wait_for_receipt":
        photos = message.get("photo")
        if not photos:
            send_message_fn(chat_id, "Please send a photo, not text.",
                            message_thread_id=thread_id, force_reply=True)
            return True

        send_message_fn(chat_id, "Got it! Extracting details...", message_thread_id=thread_id)

        try:
            image_bytes = _download_telegram_photo(photos)
        except Exception as e:
            print(f"Telegram photo download error: {e}")
            reply("Could not download the photo. Please try again.", force_reply=True)
            return True

        file_upload_id = upload_photo_to_notion(image_bytes)
        if file_upload_id:
            data["photo_file_upload_id"] = file_upload_id

        from utils.activity_graph import run_extraction
        extracted = run_extraction(image_bytes)

        data["date"] = data.get("date") or extracted.get("date")
        data["type"] = data.get("type") or extracted.get("types") or []
        data["location"] = data.get("location") or extracted.get("location")
        data["movie_name"] = extracted.get("movie_name")
        data["restaurant_name"] = extracted.get("restaurant_name")
        data["food_items"] = extracted.get("food_items") or []
        data["total_price"] = extracted.get("total_price")
        data["cuisine"] = extracted.get("cuisine") or []

        if not data.get("date_idea"):
            type_str = ", ".join(data["type"]) if data["type"] else "Activity"
            date_str = data.get("date") or ""
            data["date_idea"] = f"{type_str} - {date_str}" if date_str else type_str

        if extracted.get("errors"):
            send_message_fn(chat_id, "Extracted with some uncertainty — please review carefully.",
                            message_thread_id=thread_id)

        pending_entry["step"] = "ask_person"
        kb("Who went?", [[PLAYER_2], [PLAYER_1], ["Both"]])
        return True

    # ── ask_date_idea ─────────────────────────────────────────────────────────
    if step == "ask_date_idea":
        if not message_text:
            reply("Please type a name/title for this activity.", force_reply=True)
            return True
        data["date_idea"] = message_text
        pending_entry["step"] = "ask_date"
        send_message_fn(chat_id, "What date was this? (DD/MM/YYYY)",
                        message_thread_id=thread_id, force_reply=True)
        return True

    # ── ask_date ─────────────────────────────────────────────────────────────
    if step == "ask_date":
        try:
            data["date"] = parse_date_input(message_text)
        except ValueError:
            reply("Invalid date. Please use DD/MM/YYYY (e.g. 25/05/2026).", force_reply=True)
            return True
        pending_entry["step"] = "ask_type"
        data["type"] = []
        _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn)
        return True

    # ── ask_type ─────────────────────────────────────────────────────────────
    if step == "ask_type":
        if message_text == "Done ✓":
            if not data["type"]:
                _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn,
                                    note="Please select at least one type first.")
                return True
            pending_entry["step"] = "ask_person"
            kb("Who went?", [[PLAYER_2], [PLAYER_1], ["Both"]])
        elif message_text in ACTIVITY_TYPES:
            if message_text in data["type"]:
                data["type"].remove(message_text)
            else:
                data["type"].append(message_text)
            _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn)
        else:
            _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn)
        return True

    # ── ask_person ───────────────────────────────────────────────────────────
    if step == "ask_person":
        if message_text not in PERSON_OPTIONS:
            kb("Who went?", [[PLAYER_2], [PLAYER_1], ["Both"]])
            return True
        data["person"] = message_text
        pending_entry["step"] = "ask_favourite"
        kb("Was this a favourite?", [["Yes"], ["No"]])
        return True

    # ── ask_favourite ────────────────────────────────────────────────────────
    if step == "ask_favourite":
        if message_text not in FAVOURITE_OPTIONS:
            kb("Was this a favourite?", [["Yes"], ["No"]])
            return True
        data["favourite"] = message_text
        pending_entry["step"] = "ask_time_of_day"
        kb("Time of day?", [["Day"], ["Night"], ["Both"]])
        return True

    # ── ask_time_of_day ──────────────────────────────────────────────────────
    if step == "ask_time_of_day":
        if message_text not in TIME_OF_DAY_OPTIONS:
            kb("Time of day?", [["Day"], ["Night"], ["Both"]])
            return True
        data["time_of_day"] = message_text
        pending_entry["step"] = "ask_notes"
        kb("Any notes to add?", [["Add Notes"], ["Skip"]])
        return True

    # ── ask_notes ────────────────────────────────────────────────────────────
    if step == "ask_notes":
        if message_text == "Add Notes":
            pending_entry["step"] = "wait_for_notes"
            send_message_fn(chat_id, "Type your notes.", message_thread_id=thread_id, force_reply=True)
        else:
            data["notes"] = None
            pending_entry["step"] = "review"
            _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    # ── wait_for_notes ───────────────────────────────────────────────────────
    if step == "wait_for_notes":
        data["notes"] = message_text or None
        pending_entry["step"] = "review"
        _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    # ── review ───────────────────────────────────────────────────────────────
    if step == "review":
        if message_text == "Confirm":
            missing = validate_activity_data(data)
            if missing:
                send_message_fn(chat_id,
                                f"Missing required fields: {', '.join(missing)}. Please use Edit.",
                                message_thread_id=thread_id)
                _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
                return True
            rm_kb("Creating your activity in Notion...")
            preview = _build_creation_preview(data)
            if preview:
                send_message_fn(chat_id, preview, message_thread_id=thread_id)
            page_id = create_dates_page(data)
            if page_id:
                send_message_fn(chat_id, _build_success_message(data), message_thread_id=thread_id)
            else:
                send_message_fn(chat_id,
                                "Failed to create the Notion page. Check server logs.",
                                message_thread_id=thread_id)
            return False

        elif message_text == "Edit":
            pending_entry["step"] = "edit_field"
            _show_edit_keyboard(chat_id, thread_id, data, send_keyboard_fn)

        elif message_text == "Retry" and data.get("mode") == "receipt":
            for field in ["date", "type", "location", "movie_name", "restaurant_name",
                          "food_items", "total_price", "cuisine",
                          "photo_file_upload_id", "date_idea"]:
                data.pop(field, None)
            data["type"] = []
            pending_entry["step"] = "wait_for_receipt"
            send_message_fn(chat_id, "Please send a clearer receipt or ticket photo.",
                            message_thread_id=thread_id, force_reply=True)

        elif message_text == "Cancel":
            rm_kb("Cancelled. No changes were made.")
            return False

        else:
            _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    # ── edit_field ───────────────────────────────────────────────────────────
    if step == "edit_field":
        if message_text == "Cancel Edit":
            pending_entry["step"] = "review"
            _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
            return True

        text_prompts = {
            "Date Idea":   ("edit_date_idea",   "Enter new activity name/title:"),
            "Date":        ("edit_date",         "Enter new date (DD/MM/YYYY):"),
            "Notes":       ("edit_notes",        "Enter new notes (or type 'clear' to remove):"),
            "Location":    ("edit_location",     "Enter new location (or 'clear' to remove):"),
            "Movie":       ("edit_movie",        "Enter new movie name (or 'clear' to remove):"),
            "Restaurant":  ("edit_restaurant",   "Enter new restaurant name (or 'clear' to remove):"),
        }
        if message_text in text_prompts:
            new_step, prompt = text_prompts[message_text]
            pending_entry["step"] = new_step
            send_message_fn(chat_id, prompt, message_thread_id=thread_id, force_reply=True)
        elif message_text == "Type":
            pending_entry["step"] = "edit_type"
            _reset_and_show_type(chat_id, thread_id, data, send_keyboard_fn)
        elif message_text == "Person":
            pending_entry["step"] = "edit_person"
            kb("Who went?", [[PLAYER_2], [PLAYER_1], ["Both"]])
        elif message_text == "Favourite":
            pending_entry["step"] = "edit_favourite"
            kb("Was this a favourite?", [["Yes"], ["No"]])
        elif message_text == "Time of Day":
            pending_entry["step"] = "edit_time_of_day"
            kb("Time of day?", [["Day"], ["Night"], ["Both"]])
        else:
            _show_edit_keyboard(chat_id, thread_id, data, send_keyboard_fn)
        return True

    # ── edit: text fields ─────────────────────────────────────────────────────
    if step == "edit_date_idea":
        if message_text:
            data["date_idea"] = message_text
        pending_entry["step"] = "review"
        _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    if step == "edit_date":
        try:
            data["date"] = parse_date_input(message_text)
        except ValueError:
            reply("Invalid date. Please use DD/MM/YYYY.", force_reply=True)
            return True
        pending_entry["step"] = "review"
        _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    if step == "edit_notes":
        data["notes"] = None if message_text.lower() == "clear" else (message_text or None)
        pending_entry["step"] = "review"
        _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    if step == "edit_location":
        data["location"] = None if message_text.lower() == "clear" else (message_text or None)
        pending_entry["step"] = "review"
        _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    if step == "edit_movie":
        data["movie_name"] = None if message_text.lower() == "clear" else (message_text or None)
        pending_entry["step"] = "review"
        _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    if step == "edit_restaurant":
        data["restaurant_name"] = None if message_text.lower() == "clear" else (message_text or None)
        pending_entry["step"] = "review"
        _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        return True

    # ── edit: keyboard fields ─────────────────────────────────────────────────
    if step == "edit_type":
        if message_text == "Done ✓":
            if not data["type"]:
                _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn,
                                    note="Please select at least one type first.")
                return True
            pending_entry["step"] = "review"
            _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        elif message_text in ACTIVITY_TYPES:
            if message_text in data["type"]:
                data["type"].remove(message_text)
            else:
                data["type"].append(message_text)
            _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn)
        else:
            _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn)
        return True

    if step == "edit_person":
        if message_text in PERSON_OPTIONS:
            data["person"] = message_text
            pending_entry["step"] = "review"
            _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        else:
            kb("Who went?", [[PLAYER_2], [PLAYER_1], ["Both"]])
        return True

    if step == "edit_favourite":
        if message_text in FAVOURITE_OPTIONS:
            data["favourite"] = message_text
            pending_entry["step"] = "review"
            _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        else:
            kb("Was this a favourite?", [["Yes"], ["No"]])
        return True

    if step == "edit_time_of_day":
        if message_text in TIME_OF_DAY_OPTIONS:
            data["time_of_day"] = message_text
            pending_entry["step"] = "review"
            _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn)
        else:
            kb("Time of day?", [["Day"], ["Night"], ["Both"]])
        return True

    return True


# ── Private helpers ───────────────────────────────────────────────────────────

def _show_type_keyboard(chat_id, thread_id, selected_types, send_keyboard_fn, note=None):
    selected_str = ", ".join(selected_types) if selected_types else "none"
    header = f"Type(s) selected: {selected_str}\nTap to toggle, then Done ✓"
    if note:
        header = f"{note}\n{header}"
    send_keyboard_fn(chat_id, header, [
        ["Fancy", "Activity", "Drive"],
        ["Game", "Food", "Shopping"],
        ["Chilling", "Movie", "Nightlife"],
        ["Attraction", "Nature"],
        ["Done ✓"],
    ], message_thread_id=thread_id, one_time=False)


def _reset_and_show_type(chat_id, thread_id, data, send_keyboard_fn):
    data["type"] = []
    _show_type_keyboard(chat_id, thread_id, data["type"], send_keyboard_fn)


def _show_edit_keyboard(chat_id, thread_id, data, send_keyboard_fn):
    rows = [["Date Idea", "Date"], ["Type", "Person"], ["Favourite", "Time of Day"], ["Notes"]]
    if data.get("mode") == "receipt":
        rows.insert(-1, ["Location", "Movie"])
        rows.insert(-1, ["Restaurant"])
    rows.append(["Cancel Edit"])
    send_keyboard_fn(chat_id, "Which field would you like to edit?", rows, message_thread_id=thread_id)


def _show_review(chat_id, thread_id, data, send_message_fn, send_keyboard_fn):
    send_message_fn(chat_id, build_activity_summary(data), message_thread_id=thread_id)
    buttons = [["Confirm"], ["Edit"], ["Retry"], ["Cancel"]] if data.get("mode") == "receipt" \
              else [["Confirm"], ["Edit"], ["Cancel"]]
    send_keyboard_fn(chat_id, "What would you like to do?", buttons, message_thread_id=thread_id)


def _build_creation_preview(data):
    """Return a short 'creating…' status message, or None if no relations to resolve."""
    lines = []
    types = data.get("type") or []
    if "Movie" in types and data.get("movie_name"):
        lines.append(f"🎬 Looking up movie: {data['movie_name']}")
    if "Food" in types and data.get("restaurant_name"):
        lines.append(f"🍽️  Finding/creating restaurant: {data['restaurant_name']}")
    if data.get("food_items"):
        n = len(data["food_items"])
        lines.append(f"🥘 Creating {n} food item{'s' if n != 1 else ''}...")
    return "\n".join(lines) if lines else None


def _build_success_message(data):
    lines = ["Activity added!"]
    if data.get("movie_page_id"):
        lines.append(f"🎬 Movie linked: {data.get('movie_name')}")
    elif data.get("movie_name"):
        lines.append(f"🎬 Movie not linked (not found on IMDb): {data['movie_name']}")
    if data.get("restaurant_page_id"):
        lines.append(f"🍽️  Restaurant linked: {data.get('restaurant_name')}")
    if data.get("food_item_page_ids"):
        n = len(data["food_item_page_ids"])
        lines.append(f"🥘 {n} food item{'s' if n != 1 else ''} linked")
    return "\n".join(lines)
