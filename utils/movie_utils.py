import json
import re
from urllib.parse import quote
import requests
from utils.time_utils import *
from config import *
from utils.time_utils import get_last_sunday_date

session = requests.Session()


# ----- MOVIE UTILITIES -----
def _get_imdb_suggestion(title):
    title = (title or "").strip().lower()
    if not title:
        return None

    first_char = title[0]
    slug = quote(title)
    imdb_url = f"https://v2.sg.media-imdb.com/suggestion/{first_char}/{slug}.json"
    try:
        response = session.get(imdb_url, timeout=3)
        response.raise_for_status()
        data = response.json()
        for item in data.get("d", []):
            if item.get("id", "").startswith("tt"):
                return item
    except (requests.RequestException, ValueError):
        return None


def _get_imdb_image_for_title(title):
    item = _get_imdb_suggestion(title)
    image_info = (item or {}).get("i") or {}
    return image_info.get("imageUrl")


def _get_imdb_title_id(title):
    item = _get_imdb_suggestion(title)
    return (item or {}).get("id")


def get_movie_name_from_id(movie_id):
    if not movie_id:
        return None

    imdb_url = f"https://www.imdb.com/title/{movie_id}/reference/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        response = session.get(imdb_url, headers=headers, timeout=3)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching movie name for ID {movie_id}: {e}")
        return None

    match = re.search(r'<title>\s*(.*?)\s*\(.*?IMDb.*?</title>', response.text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def get_imdb_rating(movie_title):
    title = (movie_title or "").strip()
    if not title:
        return None

    title_id = _get_imdb_title_id(title)
    if not title_id:
        return None

    try:
        response = session.get(
            f"https://api.agregarr.org/api/ratings?id={title_id}",
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching IMDb rating for {movie_title}: {e}")
        return None

    if not data:
        return None

    return data[0].get("rating")


def get_movie_image_url(movie_title):
    title = (movie_title or "").strip()
    if not title:
        return None

    return _get_imdb_image_for_title(title)


def get_movie_genre(movie_title):
    genre_chat = model.start_chat(history=[
        {"role": "user", "parts": "I will give you a movie name"
        "and you will only reply with the genre (ONE CATEGORY) of the movie. "
        "no preamble, no explanation, no punctuation, no extra words."}
    ])
    
    try: 
        response = genre_chat.send_message(movie_title)
        # now to convert to title case
        genre = response.text.strip().title()
        return genre
    except Exception as e:
        print(f"Error fetching genre for {movie_title}: {e}")
        return None
    

def add_page_to_movies(movie, person, queued="Not Queued"):
    from utils.movie_utils import get_imdb_rating, get_movie_genre
    from utils.database_utils import MOVIE_DATA_SOURCE_ID

    suggestion = _get_imdb_suggestion(movie)
    if not suggestion:
        return None

    movie = suggestion["l"]
    movie_id = suggestion["id"]
    image_url = ((suggestion.get("i") or {}).get("imageUrl"))
    rating = get_imdb_rating(movie)
    genre = get_movie_genre(movie)

    url = PAGES_END_POINT
    new_page = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": MOVIE_DATA_SOURCE_ID
        },
        "properties": {
            "Cover": {"files": [{
                        "name": "Poster",
                        "type": "external",
                        "external": {"url": image_url}}]},
            "Movie": {"title": [{"text": {"content": movie}}]},
            "Person": {"select": {'name': person}},
            "IMDb": {"number": rating},
            "Genre": {"multi_select": [{"name": genre}]},
            "Status": {"select": {"name": "Not Watched"}},
            "Queued": {"select": {"name": queued}},
            "ID": {"rich_text": [{"text": {"content": movie_id}}]}
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(new_page)).json()
    except Exception as e:
        print(f"Error adding page to movies database: {e}")
        return None
    
    return response["id"]


def check_movie_database(movie_name):
    from utils.database_utils import MOVIE_DATA_SOURCE_ID

    movie_id = _get_imdb_title_id(movie_name)
    url = f"{DATA_SOURCE_END_POINT}{MOVIE_DATA_SOURCE_ID}/query"
    payload = {
        "filter": {
            "property": "ID",
            "rich_text": {"equals": movie_id}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload).json()
    except Exception as e:
        print(f"Error checking movie database: {e}")
        return False
    results = response.get("results", [])
    return len(results) > 0


def check_no_queued():
    from utils.database_utils import MOVIE_DATA_SOURCE_ID

    url = f"{DATA_SOURCE_END_POINT}{MOVIE_DATA_SOURCE_ID}/query"
    payload = {
        "filter": {
            "property": "Queued",
            "select": {"equals": "Queued"}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload).json()
    except Exception as e:
        print(f"Error checking queued movies: {e}")
        return 0
    results = response.get("results", [])
    return len(results)


def check_oldest_queued():
    from utils.database_utils import MOVIE_DATA_SOURCE_ID

    url = f"{DATA_SOURCE_END_POINT}{MOVIE_DATA_SOURCE_ID}/query"
    payload = {
        "filter": {
            "property": "Queued",
            "select": {"equals": "Queued"}
        },
        "sorts": [
            {
                "property": "Queued Date",
                "direction": "ascending"
            }
        ],
        "page_size": 1
    }
    try:
        response = requests.post(url, headers=headers, json=payload).json()
    except Exception as e:
        print(f"Error checking oldest queued movie: {e}")
        return None
    results = response.get("results", [])
    if results:
        return results[0]["properties"]["Movie"]["title"][0]["text"]["content"]
    return None


def change_queued_status(movie_name, new_status):
    from utils.database_utils import MOVIE_DATA_SOURCE_ID

    url = f"{DATA_SOURCE_END_POINT}{MOVIE_DATA_SOURCE_ID}/query"
    payload = {
        "filter": {
            "property": "Movie",
            "title": {"equals": movie_name}
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload).json()
    except Exception as e:
        print(f"Error checking movie database: {e}")
        return

    results = response.get("results", [])
    if results:
        page_id = results[0]["id"]
        update_url = f"{PAGES_END_POINT}{page_id}"
        updated_page = {
            "properties": {
                "Queued": {"select": {"name": new_status}}
            }
        }
        try:
            requests.patch(update_url, headers=headers, json=updated_page)
        except Exception as e:
            print(f"Error updating movie status: {e}")


def check_current_winner():
    from utils.database_utils import find_record

    date = get_last_sunday_date()
    record = find_record(weekly_winners, date)
    if record:
        return record["winner"]
    return None


def movie_summary(movie_title):
    rating = get_imdb_rating(movie_title)
    genre = get_movie_genre(movie_title)
    summary = f"Movie: {movie_title}\nGenre: {genre}\nIMDb Rating: {rating}"
    return summary
