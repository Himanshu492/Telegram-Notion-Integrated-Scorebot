import requests
import json
from config import *
import dotenv

dotenv.load_dotenv()
player_1 = os.getenv("PLAYER_1")
player_2 = os.getenv("PLAYER_2")

# ----- NOTION UTILITIES -----

def get_data_source_id(database_id):
    url = f"{DATABASE_END_POINT}{database_id}"

    response = requests.get(url, headers=headers).json()
    
    return response["data_sources"][0]["id"]


def get_data_source_properties(data_source_id):
    url = f"{DATA_SOURCE_END_POINT}{data_source_id}"
    
    response = requests.get(url, headers=headers).json()

    return response


def add_page_to_scores(data_source_id, date, name, game, score, tries=None):
    url = PAGES_END_POINT
    new_page = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": data_source_id
        },
        "properties": {
            "Date Value": {"date": {"start": date}},
            "ID": {"title": [{"text": {"content": "Score Entry"}}]},
            "Name": {"select": {'name': name}},
            "Game": {"select": {'name': game}},
            "Score": {"number": score},
        }
    }
    if tries is not None:
        new_page["properties"]["Tries"] = {"number": tries}

    response = requests.post(url, headers=headers, data=json.dumps(new_page)).json()
    return response["id"]


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


def add_page_to_daily_winners(data_source_id, date, name, a, h):
    url = PAGES_END_POINT
    new_page = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": data_source_id
        },
        "properties": {
            "Date": {"date": {"start": date}},
            "ID": {"title": [{"text": {"content": "Daily Winner Entry"}}]},
            "Winner": {"select": {'name': name}},
            player_2: {"number": a},
            player_1: {"number": h}
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(new_page)).json()
    return response["id"]


def add_page_to_weekly_winners(data_source_id, date, name, a, h, difference):
    url = PAGES_END_POINT
    new_page = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": data_source_id
        },
        "properties": {
            "Week End Date": {"date": {"start": date}},
            "ID": {"title": [{"text": {"content": "Weekly Winner"}}]},
            "Winner": {"select": {'name': name}},
            player_2: {"number": a},
            player_1: {"number": h},
            "Difference": {"number": difference}
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(new_page)).json()
    return response["id"]


def add_page_to_day(data_source_id, date, name):
    url = PAGES_END_POINT
    new_page = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": data_source_id
        },
        "properties": {
            "Date": {"date": {"start": date}},
            "ID": {"title": [{"text": {"content": "Record"}}]}
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(new_page)).json()
    return response["id"]


def find_page_id_by_date_and_name(data_source_id, date):
    url = f"{DATA_SOURCE_END_POINT}{data_source_id}/pages"
    query = {
        "filter": [
                {
                    "property": "Date",
                    "date": {
                        "equals": date
                    }
                }
            ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(query)).json()
    results = response.get("results", [])
    if results:
        return results[0]["id"]
    return None


def update_page_in_day(name, date, wordle=None, globle=None, echo_chess=None, connections_score=None, connections_tries=None):
    page_id = find_page_id_by_date_and_name(DAY_DATA_SOURCE_ID, date)
    if not page_id:
        print(f"No page found for date: {date}")
        return None
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

    response = requests.patch(url, headers=headers, data=json.dumps(updated_properties)).json()
    return response


SCORES_DATA_SOURCE_ID = get_data_source_id(SCORES_NOTION)
DAILY_WINNERS_DATA_SOURCE_ID = get_data_source_id(DAILY_WINNERS_NOTION)
WEEKLY_WINNERS_DATA_SOURCE_ID = get_data_source_id(WEEKLY_WINNERS_NOTION)
MOVIE_DATA_SOURCE_ID = get_data_source_id(MOVIES_NOTION)
DAY_DATA_SOURCE_ID = get_data_source_id(DAY_NOTION)

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
