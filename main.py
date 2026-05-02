import time
import requests
from PIL import Image
from io import BytesIO
from config import *
from utils.time_utils import get_date_yesterday, get_date_now, get_time_now, notion_date_format
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
                if not if_exists(scores, get_date_now(), user_name, "connections"):
                    page_id_connections = add_page_to_scores(SCORES_DATA_SOURCE_ID, 
                                                             get_date_now(date_format=notion_date_format), 
                                                             user_name, "connections", score, tries=total_tries)
                    insert_record({"name": user_name, "game": "connections", "score": [score, total_tries], "date": get_date_now(), "page_id": page_id_connections}, scores)
                    
                    if score == 4:
                        message = f"{user_name}'s Connections score is: {score} ({total_tries} tries)"
                    else:
                        message = f"{user_name}'s Connections score is: {score}"
                    send_message(chat_id, message, 
                                    message_thread_id=message_thread_id, reply_to_message_id=message_id)
                else:
                    update_record(scores, get_date_now(), user_name, [score, total_tries], "connections")
                    if score == 4:
                        message = f"{user_name}'s Connections score updated to: {score} ({total_tries} tries)"
                    else:
                        message = f"{user_name}'s Connections score updated to: {score}"
                    send_message(chat_id, message, 
                                    message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    page_id = get_page_id(scores, get_date_now(), user_name, "connections")
                    update_page_in_scores(page_id, score, tries=total_tries)
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
                if not if_exists(scores, get_date_now(), user_name, "globle"):
                    page_id_globle = add_page_to_scores(SCORES_DATA_SOURCE_ID, 
                                                        get_date_now(date_format=notion_date_format), 
                                                        user_name, "globle", tries)
                    insert_record({"name": user_name, "game": "globle", "score": tries, "date": get_date_now(), "page_id": page_id_globle}, scores)
                    send_message(chat_id, f"{user_name}'s Globle score is: {tries} guesses", 
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)

                else:
                    page_id = get_page_id(scores, get_date_now(), user_name, "globle")
                    update_record(scores, get_date_now(), user_name, tries, "globle")
                    send_message(chat_id, f"{user_name}'s Globle score is updated to: {tries} guesses", 
                                    message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    update_page_in_scores(page_id, tries)
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
                if not if_exists(scores, get_date_now(), user_name, "echo_chess"):
                    page_id_chess = add_page_to_scores(SCORES_DATA_SOURCE_ID, 
                                                            get_date_now(date_format=notion_date_format), 
                                                            user_name, "echo_chess", tries_taken)
                    insert_record({"name": user_name, "game": "echo_chess", "score": tries_taken, "date": get_date_now(), "page_id": page_id_chess}, scores)
                    send_message(chat_id, f"{user_name}'s Echo Chess tries taken: {tries_taken}", 
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)
                else:
                    page_id = get_page_id(scores, get_date_now(), user_name, "echo_chess")
                    update_record(scores, get_date_now(), user_name, tries_taken, "echo_chess")
                    send_message(chat_id, f"{user_name}'s Echo Chess tries taken updated to: {tries_taken}", 
                                message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    update_page_in_scores(page_id, tries_taken)
                    
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
                if not if_exists(scores, get_date_now(), user_name, "wordle"):
                    page_id_wordle = add_page_to_scores(SCORES_DATA_SOURCE_ID, 
                                                            get_date_now(date_format=notion_date_format), 
                                                            user_name, "wordle", score)
                    insert_record({"name": user_name, "game": "wordle", "score": score, "date": get_date_now(), "page_id": page_id_wordle}, scores)
                    send_message(chat_id, f"{user_name}'s Wordle score is: {score}",
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)
                else:
                    page_id = get_page_id(scores, get_date_now(), user_name, "wordle")
                    update_record(scores, get_date_now(), user_name, score, "wordle")
                    send_message(chat_id, f"{user_name}'s Wordle score updated to: {score}",
                                 message_thread_id=message_thread_id, reply_to_message_id=message_id)
                    update_page_in_scores(page_id, score)
                del pending[key]
                
            except Exception as e:
                res = send_message(chat_id, "Invalid input. Please try again.", 
                                   message_thread_id=message_thread_id, 
                                   reply_to_message_id=message_id, force_reply=True)
                pending[key]["prompt_id"] = res["message_id"]
                pending[key]["expiry"] = time.time() + expiry_time
            return
        
        if pending[key]["command"] == "/choosemovie":
            movie = message_text
            try:
                # Try the YouTube path first so links are saved with the video fields.
                image = get_youtube_thumbnail_url(movie)
                title = get_youtube_title(movie)

                if check_no_queued() >= 3:
                    unqueue_movie = check_oldest_queued()
                    change_queued_status(unqueue_movie, "Not Queued")
                    
                if check_movie_database(title):
                    queued = change_queued_status(title, "Queued")
                else:
                    queued = add_video_page_to_movies(movie, image, title, user_name, queued="Queued")

                # Do not send a success message when the database write/update failed.
                if not queued:
                    raise ValueError("Failed to queue video.")

                send_message(chat_id, message_thread_id=message_thread_id, reply_to_message_id=message_id, text="Video Queued!")
                del pending[key]

            except Exception as e:
                print(f"Error processing video choice '{movie}': {e}")
                try: 
                    # If the video fields cannot be resolved, fall back to the normal movie flow.
                    if check_no_queued() >= 3:
                        unqueue_movie = check_oldest_queued()
                        change_queued_status(unqueue_movie, "Not Queued")

                    if check_movie_database(movie):
                        queued = change_queued_status(movie, "Queued")
                    else: 
                        queued = add_page_to_movies(movie, user_name, queued="Queued")

                    # Do not send a success message when IMDb lookup or page creation failed.
                    if not queued:
                        raise ValueError("Failed to queue movie.")
                
                    send_message(chat_id, message_thread_id=message_thread_id, reply_to_message_id=message_id, text="Movie Queued!")
                    del pending[key]
                
                except Exception as e:
                    print(f"Error processing movie choice '{movie}': {e}")
                    res = send_message(chat_id, "Error processing movie choice. Please try again.", 
                                        message_thread_id=message_thread_id, reply_to_message_id=message_id)
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
        score = get_score(get_date_now(), user_name, "wordle")
        if score:
            score = int(score)
            send_message(chat_id, f"{user_name}'s Wordle score for {get_date_now()} is {score}", 
                        message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Wordle score for {get_date_now()}", 
                        message_thread_id=message_thread_id)
        return  

    if message_text == "/checkechochess@silverlining12bot":
        score = get_score(get_date_now(), user_name, "echo_chess")
        if score:
            score = int(score)
            send_message(chat_id, f"{user_name}'s Echo Chess score for {get_date_now()} is {score}", 
                        message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Echo Chess score for {get_date_now()}", 
                        message_thread_id=message_thread_id)
        return

    if message_text == "/checkconnections@silverlining12bot":
        score = get_score(get_date_now(), user_name, "connections")
        if score:
            score = list(map(int, score))
            if score[1] == 4:
                send_message(chat_id, f"{user_name}'s Connections score for {get_date_now()} is {score[0]} (Total Tries: {score[1]})", message_thread_id=message_thread_id)
            else:
                send_message(chat_id, f"{user_name}'s Connections score for {get_date_now()} is {score}", message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Connections score for {get_date_now()}", 
                        message_thread_id=message_thread_id)
        return

    if message_text == "/checkgloble@silverlining12bot":
        score = get_score(get_date_now(), user_name, "globle")
        if score:
            score = int(score)
            send_message(chat_id, f"{user_name}'s Globle score for {get_date_now()} is {score} guesses", 
                        message_thread_id=message_thread_id)
        else:
            send_message(chat_id, f"{user_name} has no Globle score for {get_date_now()}", 
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

        # Send daily summary at 00:00 only once per day
        if get_time_now() == "00:00":
            yesterday = get_date_yesterday()

            if not if_exists(daily_winners, yesterday):
                summary = generate_daily_summary(yesterday)
                summary_chat_id = -1002538310918
                send_message(summary_chat_id, summary)

        # Send weekly summary at 00:00 on Mondays only once per week
        if get_time_now() == "00:00" and get_date_now(True) == "Monday":
            end_date = get_date_yesterday()
            if not if_exists(weekly_winners, end_date):
                weekly_summary = generate_weekly_summary(end_date)
                weekly_summary_chat_id = -1002538310918
                send_message(weekly_summary_chat_id, weekly_summary)

        time.sleep(1)


if __name__ == "__main__":
    main()
