import json
import re
from urllib.parse import quote
import requests
from utils.time_utils import *
from config import *
from utils.time_utils import get_last_sunday_date
from urllib.parse import parse_qs, urlparse

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
        response = requests.post(url, headers=headers, data=json.dumps(new_page))
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        print(f"Error adding page to movies database: {e}")
        return None

    # Only treat the insert as successful when Notion returns a page id.
    return response_data.get("id")


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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        print(f"Error checking movie database: {e}")
        return False
    results = response_data.get("results", [])
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        print(f"Error checking queued movies: {e}")
        return 0
    results = response_data.get("results", [])
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        print(f"Error checking oldest queued movie: {e}")
        return None
    results = response_data.get("results", [])
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        print(f"Error checking movie database: {e}")
        return False

    results = response_data.get("results", [])
    if results:
        page_id = results[0]["id"]
        update_url = f"{PAGES_END_POINT}{page_id}"
        updated_page = {
            "properties": {
                "Queued": {"select": {"name": new_status}}
            }
        }
        try:
            response = requests.patch(update_url, headers=headers, json=updated_page)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error updating movie status: {e}")
            return False
    return False


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


def get_youtube_thumbnail_url(youtube_url):
    if not youtube_url:
        raise ValueError("YouTube URL is required.")

    parsed_url = urlparse(youtube_url.strip())
    hostname = (parsed_url.hostname or "").lower()
    video_id = None

    if hostname in {"youtu.be", "www.youtu.be"}:
        video_id = parsed_url.path.lstrip("/").split("/")[0]
    elif hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.path.startswith(("/embed/", "/shorts/", "/live/")):
            video_id = parsed_url.path.split("/")[2]

    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def _get_youtube_video_id(youtube_url):
    if not youtube_url:
        raise ValueError("YouTube URL is required.")

    parsed_url = urlparse(youtube_url.strip())
    hostname = (parsed_url.hostname or "").lower()
    video_id = None

    if hostname in {"youtu.be", "www.youtu.be"}:
        video_id = parsed_url.path.lstrip("/").split("/")[0]
    elif hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.path.startswith(("/embed/", "/shorts/", "/live/")):
            parts = parsed_url.path.split("/")
            if len(parts) > 2:
                video_id = parts[2]

    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    return video_id


def get_youtube_title(youtube_url):
    video_id = _get_youtube_video_id(youtube_url)
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        response = session.get(watch_url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Unable to fetch YouTube title: {e}") from e

    # Try the normal page title first, then fall back to metadata formats
    # YouTube sometimes serves to non-browser clients.
    match = re.search(r"<title>(.*?)</title>", response.text, re.DOTALL)
    if match:
        title = match.group(1).replace(" - YouTube", "").strip()
    else:
        match = re.search(r'<meta property="og:title" content="(.*?)">', response.text, re.DOTALL)
        if match:
            title = match.group(1).strip()
        else:
            match = re.search(r'"title":"(.*?)"', response.text, re.DOTALL)
            if not match:
                raise ValueError("Unable to parse YouTube title.")
            title = bytes(match.group(1), "utf-8").decode("unicode_escape").strip()

    if not title:
        raise ValueError("Unable to parse YouTube title.")

    return title


def add_video_page_to_movies(url, image, title, person, queued="Not Queued"):
    from utils.database_utils import MOVIE_DATA_SOURCE_ID

    video_page = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": MOVIE_DATA_SOURCE_ID
        },
        "properties": {
            "Cover": {"files": [{
                        "name": "Thumbnail",
                        "type": "external",
                        "external": {"url": image}}]},
            "Movie": {"title": [{"text": {"content": title}}]},
            "Person": {"select": {'name': person}},
            "Status": {"select": {"name": "Not Watched"}},
            "Queued": {"select": {"name": queued}},
            "URL": {"url": url}
        }
    }

    try:
        response = requests.post(PAGES_END_POINT, headers=headers, data=json.dumps(video_page))
        response.raise_for_status()
        response_data = response.json()
    except Exception as e:
        print(f"Error adding video page to movies database: {e}")
        return None

    # Only treat the insert as successful when Notion returns a page id.
    return response_data.get("id")
