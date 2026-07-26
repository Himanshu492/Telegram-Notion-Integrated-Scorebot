import time
import requests
from PIL import Image
from io import BytesIO
from config import *
from datetime import datetime
from utils.time_utils import get_date_yesterday, get_date_now, get_time_now, notion_date_format, date_format
from utils.database_utils import *
from utils.daily_utils import *
from utils.movie_utils import *
pending = {}
games = ["globle", "connections", "echo_chess", "wordle"]

# ----- TELEGRAM UTILITIES -----

def get_updates(offset=None, timeout=20):
    params = {"timeout": timeout, "offset": offset}
    response = requests.get(f"{BASE}/getUpdates", params=params, timeout=timeout+5)
    return response.json()["result"]


def send_message(chat_id, text, message_thread_id=None, force_reply=False, reply_to_message_id=None):
    payload = {"chat_id": chat_id, "text": text}

    if message_thread_id:
        payload["message_thread_id"] = message_thread_id
    if force_reply:
        payload["reply_markup"] = {"force_reply": True, "selective": True}
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    response = requests.post(f"{BASE}/sendMessage", json=payload, timeout=5)
    response.raise_for_status()

    return response.json()["result"]


def send_photo(chat_id, photo_url, caption=None, message_thread_id=None, reply_markup=None, parse_mode=None):
    payload = {"chat_id": chat_id, "photo": photo_url}
    if caption:
        payload["caption"] = caption
    if message_thread_id:
        payload["message_thread_id"] = message_thread_id
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode
    response = requests.post(f"{BASE}/sendPhoto", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["result"]


def format_runtime(runtime):
    if not runtime:
        return "N/A"

    hrs, mins = divmod(runtime, 60)
    if hrs and mins:
        return f"{hrs} hr{'s' if hrs > 1 else ''} {mins} min{'s' if mins > 1 else ''}"
    if hrs:
        return f"{hrs} hr{'s' if hrs > 1 else ''}"
    return f"{mins} min{'s' if mins > 1 else ''}"


def send_movie_confirmation(chat_id, message_thread_id, movie, suggestions, suggestion_index, user_name, reply_keyboard, expiry_time):
    while suggestion_index < len(suggestions):
        suggestion = suggestions[suggestion_index]
        resolved_title = suggestion["l"]
        movie_id = suggestion["id"]
        image = (suggestion.get("i") or {}).get("imageUrl")

        if not image:
            suggestion_index += 1
            continue

        rating = get_imdb_rating_by_id(movie_id, resolved_title)
        genre = get_movie_genre(resolved_title)
        runtime = get_movie_runtime_by_id(movie_id, resolved_title)
        year = suggestion.get("y")
        display_title = f"{resolved_title} ({year})" if year else resolved_title
        caption = (
            f"<b>{display_title} ({rating if rating is not None else 'N/A'})</b>\n"
            f"<b>Genre:</b> {genre or 'N/A'}\n"
            f"<b>Runtime:</b> {format_runtime(runtime)}"
        )

        send_photo(
            chat_id,
            image,
            caption=caption,
            message_thread_id=message_thread_id,
            reply_markup=reply_keyboard,
            parse_mode="HTML"
        )
        return {
            "command": "/choosemovie_confirm",
            "type": "movie",
            "movie": movie,
            "resolved_title": resolved_title,
            "movie_id": movie_id,
            "image": image,
            "rating": rating,
            "genre": genre,
            "runtime": runtime,
            "user_name": user_name,
            "suggestions": suggestions,
            "suggestion_index": suggestion_index,
            "expiry": time.time() + expiry_time
        }

    return None


def extract_command(update):
    if "entities" in update["message"]:
        for entity in update["message"]["entities"]:
            if entity["type"] == "bot_command":
                offset = entity["offset"]
                length = entity["length"]
                return update["message"]["text"][offset:offset+length]
    return None


# ----- GAME LOGIC -----

def validate_mini_time(text):
    if ':' not in text:
        raise ValueError
        return
    if text == "-1":
        raise ValueError
        return


def mini_logic(image_input):
    mini_chat = model.start_chat(history=[
    {"role": "user", "parts": 
     "I will give you an image.\n"
    "The image will say 'You solved The Mini in x:xx.'\n"
    "Return exactly the time in m:ss.\n"
    "Do not guess; if unreadable return -1.\n"
    "Return only digits and a colon."}
    ]
    )
    # image_input may be a file path (str) or a file-like object (BytesIO) or a PIL Image
    if isinstance(image_input, str):
        img = Image.open(image_input)
    else:
        # assume file-like (BytesIO) or PIL Image
        try:
            # if it's already a PIL Image, use it directly
            if isinstance(image_input, Image.Image):
                img = image_input
            else:
                img = Image.open(image_input)
        except Exception:
            # let callers handle invalid images via validate_mini_time or higher-level exception handling
            raise
    
    tries = mini_chat.send_message([img, "return time taken"])
    validate_mini_time(tries.text.strip())

    total_time = tries.text.strip()
    minutes, seconds = map(int, total_time.split(':'))
    return minutes * 60 + seconds


def validate_globle_input(text):
    if not text.isdigit():
        raise ValueError
        return
    return


def globle_logic(image_input):
    globle_chat = model.start_chat(history=[
    {"role": "user", "parts": 
     "I will give you an image.\n"
     "The image will say 'Today's guesses'.\n"
     "return the number beside that phrase.\n"
     "return only the number. no other text.\n"
     "if unreadable return -1."}])

    if isinstance(image_input, str):
        img = Image.open(image_input)
    else:
        # assume file-like (BytesIO) or PIL Image
        try:
            # if it's already a PIL Image, use it directly
            if isinstance(image_input, Image.Image):
                img = image_input
            else:
                img = Image.open(image_input)
        except Exception:
            # let callers handle invalid images via validate_globle_input or higher-level exception handling
            raise
    
    tries = globle_chat.send_message([img, "return number of guesses"])
    validate_globle_input(tries.text.strip())

    return int(tries.text.strip())


def validate_echo_chess_tries(text):    
    if text.strip() == "-1":
        raise ValueError
        return


def echo_chess_logic(image_input):
    echo_chat = model.start_chat(history=[
    {"role": "user", 
     "parts": "I will give you an image. you have to output the number of tries the user took."
     "the image will have the date, 3 stars under it. and then under that - x moves! best is y moves."
     "i want you to return only the number of tries the user took to solve the game. no other text. no punctuation."
     "just the number. if the image is invalid, return -1."}
    ])

    if isinstance(image_input, str):
        img = Image.open(image_input)
    else:
        # assume file-like (BytesIO) or PIL Image
        try:
            # if it's already a PIL Image, use it directly
            if isinstance(image_input, Image.Image):
                img = image_input
            else:
                img = Image.open(image_input)
        except Exception:
            # let callers handle invalid images via validate_echo_chess or higher-level exception handling
            raise

    img = Image.open(image_input)
    tries = echo_chat.send_message([img, "number of tries taken?"])
    validate_echo_chess_tries(tries.text.strip())
    return int(tries.text.strip())


def validate_wordle_input(text):
    lines = text.split("\n")[:2]
    if "Wordle" not in lines[0].strip():
        raise ValueError
        return
    

def wordle_logic(text):
    validate_wordle_input(text)
    first_line = text.split("\n")[0]
    score = first_line.split(" ")[-1].split("/")[0]
    if score == "X":
        return 7
    return int(score)


def validate_connections_input(text):
    lines = text.split("\n")[:2]
    if lines[0].strip() != "Connections":
        raise ValueError
        return
    if "Puzzle #" not in lines[1].strip():
        raise ValueError
        return


def connections_logic(text):
    validate_connections_input(text)
    text_lines = text.split("\n")[2:]  # Skip the first two lines
    total_tries = len(text_lines)
    score = 0
    for line in text_lines:
        success = True
        for i in range(len(line)):
            if i == 0:
                to_check = line[i]
            else:
                if line[i] != to_check:
                    success = False
                    break
        if success:
            score += 1

    return score, total_tries


 # ----- UPDATE HANDLER -----

def update_handler(update):
    if "message" not in update:
        return
    if "message_thread_id" not in update["message"]:
        return
    
    expiry_time = 120

    message_thread_id = update["message"].get("message_thread_id", None)
    message_text = update["message"].get("text", None)
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    message_id = update["message"]["message_id"]
    user_name = update["message"]["from"].get("first_name", "User")

    key = (chat_id, user_id, message_thread_id)
    if key in pending:
        if pending[key]["command"] == "/connections":
            try:
                score = connections_logic(message_text)[0]
                total_tries = connections_logic(message_text)[1]
                submission_date = get_player_date_now(user_name)
                notion_date = datetime.strptime(submission_date, date_format).strftime(notion_date_format)
                if not if_exists(scores, submission_date, user_name, "connections"):
                    page_id_connections = add_page_to_scores(SCORES_DATA_SOURCE_ID,
                                                             notion_date,
                                                             user_name, "connections", score, tries=total_tries)
                    insert_record({"name": user_name, "game": "connections", "score": [score, total_tries], "date": submission_date, "page_id": page_id_connections}, scores)

                    if score == 4:
                        message = f"{user_name}'s Connections score is: {score} ({total_tries} tries)"
                    else:
                        message = f"{user_name}'s Connections score is: {score}"
                    send_message(chat_id, message,
                                    message_thread_id=message_thread_id, reply_to_message_id=message_id)
                else:
                    update_record(scores, submission_date, user_name, [score, total_tries], "connections")
                    if score == 4:
                        message = f"{user_name}'s Connections score updated to: {score} ({total_tries} tries)"
                    else:
                        message = f"{user_name}'s Connections score updated to: {score}"
                    send_message(chat_id, message,
                                    message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    page_id = get_page_id(scores, submission_date, user_name, "connections")
                    update_page_in_scores(page_id, score, tries=total_tries)

                update_page_in_day(user_name, notion_date, connections_score=score, connections_tries=total_tries)
                del pending[key]
            except Exception as e:
                res = send_message(chat_id, "Invalid input. Please try again.", 
                                   message_thread_id=message_thread_id, 
                                   reply_to_message_id=message_id, force_reply=True)
                pending[key]["prompt_id"] = res["message_id"]
                pending[key]["expiry"] = time.time() + expiry_time
            return
        
        if pending[key]["command"] == "/globle":
            try:
                # download the file from Telegram but do NOT save to disk; use an in-memory buffer
                file_id = update["message"]["photo"][-1]["file_id"]
                file_info_resp = requests.get(f"{BASE}/getFile", params={"file_id": file_id})
                file_info_resp.raise_for_status()
                file_info = file_info_resp.json()
                file_path = file_info["result"]["file_path"]
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                print(file_url)

                file_response = requests.get(file_url, stream=True)
                file_response.raise_for_status()

                buf = BytesIO()
                for chunk in file_response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    buf.write(chunk)
                buf.seek(0)

                # pass the in-memory buffer to globle_logic (it will open it with PIL)
                tries = globle_logic(buf)
                submission_date = get_player_date_now(user_name)
                notion_date = datetime.strptime(submission_date, date_format).strftime(notion_date_format)
                if not if_exists(scores, submission_date, user_name, "globle"):
                    page_id_globle = add_page_to_scores(SCORES_DATA_SOURCE_ID,
                                                        notion_date,
                                                        user_name, "globle", tries)
                    insert_record({"name": user_name, "game": "globle", "score": tries, "date": submission_date, "page_id": page_id_globle}, scores)
                    send_message(chat_id, f"{user_name}'s Globle score is: {tries} guesses",
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)

                else:
                    page_id = get_page_id(scores, submission_date, user_name, "globle")
                    update_record(scores, submission_date, user_name, tries, "globle")
                    send_message(chat_id, f"{user_name}'s Globle score is updated to: {tries} guesses",
                                    message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    update_page_in_scores(page_id, tries)

                try:
                    update_page_in_day(user_name, notion_date, globle=tries)
                except Exception as e:
                    print(f"Error updating day page for Globle: {e}")
                del pending[key]
            except Exception as e:
                res = send_message(chat_id, "Invalid image or unreadable time. Please send a clear image of your Globle result.", 
                                   message_thread_id=message_thread_id, 
                                   reply_to_message_id=message_id, force_reply=True)
                pending[key]["prompt_id"] = res["message_id"]
                pending[key]["expiry"] = time.time() + expiry_time
            except Exception:
                # treat network / decoding errors as invalid image input
                res = send_message(chat_id, "Could not process image. Please try again.", 
                                   message_thread_id=message_thread_id, 
                                   reply_to_message_id=message_id, force_reply=True)
                pending[key]["prompt_id"] = res["message_id"]
                pending[key]["expiry"] = time.time() + expiry_time
            return  
        
        if pending[key]["command"] == "/echo_chess":
            try:
                # download the file from Telegram but do NOT save to disk; use an in-memory buffer
                file_id = update["message"]["photo"][-1]["file_id"]
                file_info_resp = requests.get(f"{BASE}/getFile", params={"file_id": file_id})
                file_info_resp.raise_for_status()
                file_info = file_info_resp.json()
                file_path = file_info["result"]["file_path"]
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                print(file_url)

                file_response = requests.get(file_url, stream=True)
                file_response.raise_for_status()

                buf = BytesIO()
                for chunk in file_response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    buf.write(chunk)
                buf.seek(0)

                # pass the in-memory buffer to echo_chess_logic (it will open it with PIL)
                tries_taken = echo_chess_logic(buf)
                submission_date = get_player_date_now(user_name)
                notion_date = datetime.strptime(submission_date, date_format).strftime(notion_date_format)
                if not if_exists(scores, submission_date, user_name, "echo_chess"):
                    page_id_chess = add_page_to_scores(SCORES_DATA_SOURCE_ID,
                                                            notion_date,
                                                            user_name, "echo_chess", tries_taken)
                    insert_record({"name": user_name, "game": "echo_chess", "score": tries_taken, "date": submission_date, "page_id": page_id_chess}, scores)
                    send_message(chat_id, f"{user_name}'s Echo Chess tries taken: {tries_taken}",
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)
                else:
                    page_id = get_page_id(scores, submission_date, user_name, "echo_chess")
                    update_record(scores, submission_date, user_name, tries_taken, "echo_chess")
                    send_message(chat_id, f"{user_name}'s Echo Chess tries taken updated to: {tries_taken}",
                                message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    update_page_in_scores(page_id, tries_taken)

                update_page_in_day(user_name, notion_date, echo_chess=tries_taken)
                del pending[key]
            except Exception as e:
                res = send_message(chat_id, "Invalid image or unreadable tries. Please send a clear image of your Echo Chess result.", 
                                   message_thread_id=message_thread_id, 
                                   reply_to_message_id=message_id, force_reply=True)
                pending[key]["prompt_id"] = res["message_id"]
                pending[key]["expiry"] = time.time() + expiry_time
            except Exception:
                # treat network / decoding errors as invalid image input
                res = send_message(chat_id, "Could not process image. Please try again.", 
                                   message_thread_id=message_thread_id, 
                                   reply_to_message_id=message_id, force_reply=True)
                pending[key]["prompt_id"] = res["message_id"]
                pending[key]["expiry"] = time.time() + expiry_time
            return

        if pending[key]["command"] == "/wordle":
            try:
                score = wordle_logic(message_text)
                submission_date = get_player_date_now(user_name)
                notion_date = datetime.strptime(submission_date, date_format).strftime(notion_date_format)
                if not if_exists(scores, submission_date, user_name, "wordle"):
                    page_id_wordle = add_page_to_scores(SCORES_DATA_SOURCE_ID,
                                                            notion_date,
                                                            user_name, "wordle", score)
                    insert_record({"name": user_name, "game": "wordle", "score": score, "date": submission_date, "page_id": page_id_wordle}, scores)
                    send_message(chat_id, f"{user_name}'s Wordle score is: {score}",
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)
                else:
                    page_id = get_page_id(scores, submission_date, user_name, "wordle")
                    update_record(scores, submission_date, user_name, score, "wordle")
                    send_message(chat_id, f"{user_name}'s Wordle score updated to: {score}",
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    update_page_in_scores(page_id, score)

                update_page_in_day(user_name, notion_date, wordle=score)
                del pending[key]
                
            except Exception as e:
                res = send_message(chat_id, "Invalid input. Please try again.", 
                                   message_thread_id=message_thread_id, 
                                   reply_to_message_id=message_id, force_reply=True)
                pending[key]["prompt_id"] = res["message_id"]
                pending[key]["expiry"] = time.time() + expiry_time
            return
        
        if pending[key]["command"] == "/choosemovie_confirm":
            p = pending[key]
            if message_text == "Yes":
                try:
                    if p["type"] == "video":
                        movie, image, title = p["movie"], p["image"], p["title"]
                        if check_movie_database(title):
                            queued = change_queued_status(title, "Queued")
                        else:
                            queued = add_video_page_to_movies(movie, image, title, p["user_name"], queued="Queued")
                        if not queued:
                            raise ValueError("Failed to queue video.")
                        if check_no_queued() > 3:
                            change_queued_status(check_oldest_queued(), "Not Queued")
                        send_message(chat_id, "Video Queued!", message_thread_id=message_thread_id)
                    else:
                        resolved = p["resolved_title"]
                        movie_id = p["movie_id"]
                        if check_movie_database(resolved, movie_id=movie_id):
                            queued = change_queued_status(resolved, "Queued", movie_id=movie_id)
                        else:
                            prefetched = {"movie_id": movie_id, "image": p["image"], "rating": p["rating"], "genre": p["genre"], "runtime": p["runtime"]}
                            queued = add_page_to_movies(resolved, p["user_name"], queued="Queued", prefetched=prefetched)
                        if not queued:
                            raise ValueError("Failed to queue movie.")
                        if check_no_queued() > 3:
                            change_queued_status(check_oldest_queued(), "Not Queued")
                        send_message(chat_id, "Movie Queued!", message_thread_id=message_thread_id)
                except Exception as e:
                    print(f"Error queuing confirmed choice: {e}")
                    send_message(chat_id, "Error queuing. Please try again.", message_thread_id=message_thread_id)
                del pending[key]
            elif message_text == "No":
                if p["type"] == "movie":
                    reply_keyboard = {"keyboard": [["Yes", "No", "Cancel"]], "one_time_keyboard": True, "resize_keyboard": True}
                    next_index = p.get("suggestion_index", 0) + 1
                    next_pending = send_movie_confirmation(
                        chat_id,
                        message_thread_id,
                        p["movie"],
                        p.get("suggestions", []),
                        next_index,
                        p["user_name"],
                        reply_keyboard,
                        expiry_time
                    )
                    if next_pending:
                        pending[key] = next_pending
                    else:
                        res = send_message(chat_id, "No more matches found. Try adding the year, like How to Train Your Dragon 2010.", message_thread_id=message_thread_id, force_reply=True)
                        pending[key] = {"command": "/choosemovie", "prompt_id": res["message_id"], "expiry": time.time() + expiry_time}
                else:
                    res = send_message(chat_id, "Please choose another movie.", message_thread_id=message_thread_id, force_reply=True)
                    pending[key] = {"command": "/choosemovie", "prompt_id": res["message_id"], "expiry": time.time() + expiry_time}
            elif message_text == "Cancel":
                send_message(chat_id, "Cancelled.", message_thread_id=message_thread_id)
                del pending[key]
            return

        if pending[key]["command"] == "/choosemovie":
            movie = message_text
            reply_keyboard = {"keyboard": [["Yes", "No", "Cancel"]], "one_time_keyboard": True, "resize_keyboard": True}
            try:
                # Try YouTube path first so links are saved with the video fields.
                image = get_youtube_thumbnail_url(movie)
                title = get_youtube_title(movie)
                send_photo(chat_id, image, caption=f"<b>{title}</b>", message_thread_id=message_thread_id, reply_markup=reply_keyboard, parse_mode="HTML")
                pending[key] = {"command": "/choosemovie_confirm", "type": "video", "movie": movie, "image": image, "title": title, "user_name": user_name, "expiry": time.time() + expiry_time}
            except Exception:
                try:
                    # Fall back to movie path.
                    suggestions = get_imdb_suggestions(movie)
                    if not suggestions:
                        raise ValueError("Movie not found.")
                    next_pending = send_movie_confirmation(
                        chat_id,
                        message_thread_id,
                        movie,
                        suggestions,
                        0,
                        user_name,
                        reply_keyboard,
                        expiry_time
                    )
                    if not next_pending:
                        raise ValueError("No movie poster found.")
                    pending[key] = next_pending
                except Exception as e:
                    print(f"Error processing movie choice '{movie}': {e}")
                    res = send_message(chat_id, "Error processing movie choice. Please try again.", message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    pending[key]["prompt_id"] = res["message_id"]
                    pending[key]["expiry"] = time.time() + expiry_time
            return
            
    if message_text == "/connections@silverlining12bot":
        res = send_message(chat_id, "Please send your Connections game text.", 
                        message_thread_id=message_thread_id, 
                        reply_to_message_id=message_id, force_reply=True)
        pending[key] = {
            "command": "/connections",
            "prompt_id": res["message_id"],
            "expiry": time.time() + expiry_time
        }
        return
    
    if message_text == "/globle@silverlining12bot":
        res = send_message(chat_id, "Please send an image of your Globle result.", 
                        message_thread_id=message_thread_id, 
                        reply_to_message_id=message_id, force_reply=True)
        pending[key] = {
            "command": "/globle",
            "prompt_id": res["message_id"],
            "expiry": time.time() + expiry_time
        }
        return
    
    if message_text == "/echo_chess@silverlining12bot":
        res = send_message(chat_id, "Please send an image of your Echo Chess result.", 
                        message_thread_id=message_thread_id, 
                        reply_to_message_id=message_id, force_reply=True)
        pending[key] = {
            "command": "/echo_chess",
            "prompt_id": res["message_id"],
            "expiry": time.time() + expiry_time
        }
        return
    
    if message_text == "/wordle@silverlining12bot":
        res = send_message(chat_id, "Please send your Wordle game text.", 
                        message_thread_id=message_thread_id, 
                        reply_to_message_id=message_id, force_reply=True)
        pending[key] = {
            "command": "/wordle",
            "prompt_id": res["message_id"],
            "expiry": time.time() + expiry_time
        }
        return
    
    if message_text == "/checkwordle@silverlining12bot":
        check_date = get_player_date_now(user_name)
        score = get_score(check_date, user_name, "wordle")
        if score:
            score = int(score)
            send_message(chat_id, f"{user_name}'s Wordle score for {check_date} is {score}",
                        message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Wordle score for {check_date}",
                        message_thread_id=message_thread_id)
        return

    if message_text == "/checkechochess@silverlining12bot":
        check_date = get_player_date_now(user_name)
        score = get_score(check_date, user_name, "echo_chess")
        if score:
            score = int(score)
            send_message(chat_id, f"{user_name}'s Echo Chess score for {check_date} is {score}",
                        message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Echo Chess score for {check_date}",
                        message_thread_id=message_thread_id)
        return

    if message_text == "/checkconnections@silverlining12bot":
        check_date = get_player_date_now(user_name)
        score = get_score(check_date, user_name, "connections")
        if score:
            score = list(map(int, score))
            if score[1] == 4:
                send_message(chat_id, f"{user_name}'s Connections score for {check_date} is {score[0]} (Total Tries: {score[1]})", message_thread_id=message_thread_id)
            else:
                send_message(chat_id, f"{user_name}'s Connections score for {check_date} is {score}", message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Connections score for {check_date}",
                        message_thread_id=message_thread_id)
        return

    if message_text == "/checkgloble@silverlining12bot":
        check_date = get_player_date_now(user_name)
        score = get_score(check_date, user_name, "globle")
        if score:
            score = int(score)
            send_message(chat_id, f"{user_name}'s Globle score for {check_date} is {score} guesses",
                        message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Globle score for {check_date}",
                        message_thread_id=message_thread_id)
        return
    
    if message_text == "/choosemovie@silverlining12bot":
        current_winner = check_current_winner()
        if current_winner and current_winner == user_name:
            send_message(chat_id, "Please choose a movie for this week", message_thread_id=message_thread_id, reply_to_message_id=message_id, force_reply=True)
            pending[key] = {
                "command": "/choosemovie",
                "prompt_id": message_id,
                "expiry": time.time() + expiry_time
            }
            return
        send_message(chat_id, "Sorry you are not the current winner!", message_thread_id=message_thread_id)
        return


    if extract_command(update):  # only reply if it was a bot command we don't recognize
        if message_thread_id:
            send_message(chat_id, "Unknown command.", message_thread_id=message_thread_id)


def main():
    last_update_id = None

    while True:
        updates = get_updates(offset=last_update_id, timeout=20)

        for update in updates:
            last_update_id = update["update_id"] + 1
            update_handler(update)

        # Clean up expired pending prompts
        current_time = time.time()
        keys_to_delete = [key for key, val in pending.items() if val["expiry"] < current_time]
        for key in keys_to_delete:
            del pending[key]

        # Ensure a Notion "day" page exists for each player's current local date
        for name in (player_1, player_2):
            tz = get_player_timezone(name)
            today_notion = get_date_now(tz, date_format=notion_date_format)
            if not find_page_id_by_date_and_name(DAY_DATA_SOURCE_ID, today_notion):
                add_page_to_day(today_notion)

        # A date is "settled" (both players' local days for it have ended) once
        # neither player's current local date still equals that date. Fire the
        # daily/weekly summary for a date the moment it becomes settled - this
        # naturally happens at whichever player's midnight comes later.
        for name in (player_1, player_2):
            tz = get_player_timezone(name)
            if get_time_now(tz) != "00:00":
                continue

            closed_date = get_date_yesterday(tz)
            other = player_2 if name == player_1 else player_1
            other_tz = get_player_timezone(other)
            if get_date_now(other_tz) == closed_date:
                # the other player is still inside closed_date; not settled yet
                continue

            if not if_exists(daily_winners, closed_date):
                summary = generate_daily_summary(closed_date)
                summary_chat_id = -1002538310918
                send_message(summary_chat_id, summary)

            if datetime.strptime(closed_date, date_format).strftime("%A") == "Sunday":
                if not if_exists(weekly_winners, closed_date):
                    weekly_summary = generate_weekly_summary(closed_date)
                    weekly_summary_chat_id = -1002538310918
                    send_message(weekly_summary_chat_id, weekly_summary)

        time.sleep(1)


if __name__ == "__main__":
    main()
