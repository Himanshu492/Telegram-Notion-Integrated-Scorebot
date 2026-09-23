import requests
import json
from config import *
import dotenv

dotenv.load_dotenv()
player_1 = os.getenv("PLAYER_1")
player_2 = os.getenv("PLAYER_2")

# ----- NOTION UTILITIES -----

# Notion can reissue a database's data source id underneath us (it happened on
# 2026-09-23 and took the bot down for every score submission). Nothing here is
# allowed to trust an id that was resolved once at import: writes re-resolve on
# retry, and every read asks for the current id.
_DS_CACHE = {}


def get_data_source_id(database_id):
    """One live lookup of a database's current data source id."""
    response = requests.get(f"{DATABASE_END_POINT}{database_id}", headers=headers, timeout=30).json()
    data_sources = response.get("data_sources") or []
    if not data_sources:
        raise RuntimeError(f"notion returned no data_sources for {database_id}: {str(response)[:300]}")
    return data_sources[0]["id"]


def data_source_id_for(database_id, force=False):
    """Cached database -> data source id lookup. force=True re-resolves from notion."""
    if force or database_id not in _DS_CACHE:
        _DS_CACHE[database_id] = get_data_source_id(database_id)
    return _DS_CACHE[database_id]


def refresh_data_source_ids():
    """Re-resolve every configured database id after a write has failed."""
    for database_id in (SCORES_NOTION, DAILY_WINNERS_NOTION, WEEKLY_WINNERS_NOTION, MOVIES_NOTION, DAY_NOTION):
        try:
            data_source_id_for(database_id, force=True)
        except Exception as e:
            print(f"[notion] refresh failed for {database_id}: {type(e).__name__}: {e}")


def data_source_query_url(database_id):
    return f"{DATA_SOURCE_END_POINT}{data_source_id_for(database_id)}/query"


def create_page_in(database_id, properties, label="page"):
    """Create a notion page, re-resolving the data source id and retrying once."""
    last_error = None
    for attempt in (1, 2):
        ds_id = data_source_id_for(database_id, force=(attempt == 2))
        payload = {"parent": {"type": "data_source_id", "data_source_id": ds_id}, "properties": properties}
        try:
            response = requests.post(PAGES_END_POINT, headers=headers, data=json.dumps(payload), timeout=30)
            body = response.json()
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
        else:
            if isinstance(body, dict) and body.get("id"):
                return body["id"]
            last_error = f"http {response.status_code}: {str(body)[:300]}"
        print(f"[notion] create {label} in {database_id} failed (attempt {attempt}): {last_error}")
    raise RuntimeError(f"notion page create failed ({label}): {last_error}")


def get_data_source_properties(data_source_id):
    url = f"{DATA_SOURCE_END_POINT}{data_source_id}"
    
    response = requests.get(url, headers=headers).json()

    return response


def add_page_to_scores(date, name, game, score, tries=None):
    properties = {
        "Date Value": {"date": {"start": date}},
        "ID": {"title": [{"text": {"content": "Score Entry"}}]},
        "Name": {"select": {'name': name}},
        "Game": {"select": {'name': game}},
        "Score": {"number": score},
    }
    if tries is not None:
        properties["Tries"] = {"number": tries}

    return create_page_in(SCORES_NOTION, properties, "score")


def update_page_in_scores(page_id, score, tries=None):
    url = f"{PAGES_END_POINT}{page_id}"
    updated_page = {
        "properties": {
            "Score": {"number": score}
        }
    }
    if tries is not None:
        updated_page["properties"]["Tries"] = {"number": tries}
    response = requests.patch(url, headers=headers, data=json.dumps(updated_page)).json()
    return response


def add_page_to_daily_winners(date, name, a, h):
    properties = {
        "Date": {"date": {"start": date}},
        "ID": {"title": [{"text": {"content": "Daily Winner Entry"}}]},
        "Winner": {"select": {'name': name}},
        player_2: {"number": a},
        player_1: {"number": h},
    }

    return create_page_in(DAILY_WINNERS_NOTION, properties, "daily winner")


def add_page_to_weekly_winners(date, name, a, h, difference):
    properties = {
        "Week End Date": {"date": {"start": date}},
        "ID": {"title": [{"text": {"content": "Weekly Winner"}}]},
        "Winner": {"select": {'name': name}},
        player_2: {"number": a},
        player_1: {"number": h},
        "Difference": {"number": difference},
    }

    return create_page_in(WEEKLY_WINNERS_NOTION, properties, "weekly winner")


def add_page_to_day(date):
    properties = {
        "Date": {"date": {"start": date}},
        "ID": {"title": [{"text": {"content": "Record"}}]},
    }

    return create_page_in(DAY_NOTION, properties, "day")


def find_page_id_by_date_and_name(database_id, date):
    url = data_source_query_url(database_id)
    query = {
        "filter": {
            "and": [
                {
                    "property": "Date",
                    "date": {
                        "equals": date
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(query)).json()
    results = response.get("results", [])
    
    if results:
        return results[0]["id"]
    return None


def update_page_in_day(name, date, wordle=None, globle=None, echo_chess=None, connections_score=None, connections_tries=None):
    page_id = find_page_id_by_date_and_name(DAY_NOTION, date)
    if not page_id:
        print(f"No page found for date: {date}")
        page_id = add_page_to_day(date)
    url = f"{PAGES_END_POINT}{page_id}"
    updated_properties = {"properties": {}}

    if wordle is not None:
        updated_properties["properties"][name + " Wordle"] = {"number": wordle}
    if globle is not None:
        updated_properties["properties"][name + " Globle"] = {"number": globle}
    if echo_chess is not None:
        updated_properties["properties"][name + " Echo Chess"] = {"number": echo_chess}
    if connections_score is not None:
        updated_properties["properties"][name + " Connections Score"] = {"number": connections_score}
    if connections_tries is not None:
        updated_properties["properties"][name + " Connections Tries"] = {"number": connections_tries}

    try: 
        response = requests.patch(url, headers=headers, data=json.dumps(updated_properties)).json()
    except Exception as e:
        print(f"Error updating page: {e}")
        raise e
    
    return response



# ----- MONGODB UTILITIES -----

# inserts a record into a collection
def insert_record(record, collection):
    result = collection.insert_one(record)
    print(f"Inserted record with id: {result.inserted_id}")


# updates a record's score by date, name, and optional game
def update_record(collection, date, name, new_score, game=None):
    query = {"date": date, "name": name}
    if game:
        query["game"] = game
    result = collection.update_one(query, {"$set": {"score": new_score}})
    print(f"Updated {result.modified_count} record(s) with date: {date}")


# deletes a specific record by date, name, and optional game
def delete_specific_record(collection, date, name, game=None):
    query = {"date": date, "name": name}
    if game:
        query["game"] = game

    result = collection.delete_one(query)

    print(f"Deleted {result.deleted_count} record(s) with date: {date} and name: {name}")


# finds a single record by date, with optional filters for name and game
def find_record(collection, date, name=None, game=None):
    query = {"date": date}
    if name:
        query["name"] = name
    if game:
        query["game"] = game

    record = collection.find_one(query)
    return record


def get_page_id(collection, date, name, game):
    record = find_record(collection, date, name, game)
    if record:
        return record.get("page_id", None)
    return None


# prints all records in a collection
def print_all_records(collection):
    records = collection.find()
    for record in records:
        print(record)


# gets score from a record
def get_score(date, name=None, game=None):
    record = find_record(scores, date, name, game)
    if record:
        return record.get("score", None)
    return None


# check if a record exists
def if_exists(collection, date, name=None, game=None):
    query = {"date": date}
    if name:
        query["name"] = name
    if game:
        query["game"] = game
    record = collection.find_one(query)
    return record is not None
