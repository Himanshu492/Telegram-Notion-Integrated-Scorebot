Let me explore the codebase first before writing the plan.

Agent:Codebase exploration for Telegram bot structure
IN
Explore the codebase at /Users/himanshusharma/Documents/Silver Lining thoroughly. I need a complete picture of the project structure to plan a new feature.

Please find and report:

1. The full directory and file tree (all files, not just top-level)
2. The main Telegram bot entry point and how commands are registered
3. All existing Telegram command handlers — their names, file locations, and rough structure
4. All Notion-related helper/utility files — what functions they expose
5. Any LangGraph usage (files, graph definitions, state structures, nodes)
6. Any prompts file or prompts module
7. The database_utils.py file — full contents if possible
8. Any file that defines Notion database IDs or data source IDs
9. Any existing add_movie, add_food, add_date, or similar command implementations
10. Any existing helper functions for: creating Notion pages, finding/searching pages, building Notion payloads, handling relations, handling file uploads
11. Any existing restaurant-related or food-item-related helpers
12. Any existing movie-related helpers (IMDb lookup, movie page creation, etc.)
13. The conversation state management pattern (how multi-step Telegram conversations are handled)
14. Any config files, .env references, or constants files

Please read the actual file contents for all key files (not just list them). I need enough detail to understand the coding style, naming conventions, function signatures, and modularization patterns used throughout the project.

Be very thorough — this is a planning task and I need to understand the full codebase before writing a detailed implementation plan.
Bash
IN
find /Users/himanshusharma/Documents/Silver\ Lining -type f -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name ".env*" | head -100

OUT
/Users/himanshusharma/Documents/Silver Lining/config.py
/Users/himanshusharma/Documents/Silver Lining/requirements.txt
/Users/himanshusharma/Documents/Silver Lining/runtime.txt
/Users/himanshusharma/Documents/Silver Lining/README.md
/Users/himanshusharma/Documents/Silver Lining/.env
/Users/himanshusharma/Documents/Silver Lining/main.py
/Users/himanshusharma/Documents/Silver Lining/tests/update.py
/Users/himanshusharma/Documents/Silver Lining/tests/youtube.py
/Users/himanshusharma/Documents/Silver Lining/tests/notiontest.py
/Users/himanshusharma/Documents/Silver Lining/tests/imdb_rating_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/test.py
/Users/himanshusharma/Documents/Silver Lining/tests/db_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/test2.py
/Users/himanshusharma/Documents/Silver Lining/tests/movie_database.py
/Users/himanshusharma/Documents/Silver Lining/tests/gemini_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/summary_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/time_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/image.py
/Users/himanshusharma/Documents/Silver Lining/tests/notiontest2.py
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py
/Users/himanshusharma/Documents/Silver Lining/utils/time_utils.py
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/google_auth_httplib2.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/typing_extensions.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto_plus-1.26.1.dist-info/top_level.txt
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/cachetools-6.2.1.dist-info/top_level.txt
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/binary.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/raw_bson.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/decimal128.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/int64.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/objectid.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/dbref.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/code.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/typings.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/tz_util.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/json_util.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/datetime_ms.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/max_key.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/errors.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/timestamp.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/son.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/min_key.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/codec_options.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/regex.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/bson/_helpers.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/google_generativeai-0.8.5.dist-info/namespace_packages.txt
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/google_generativeai-0.8.5.dist-info/top_level.txt
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/pyasn1/error.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/pyasn1/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/pyasn1/debug.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/requests-2.32.5.dist-info/top_level.txt
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/version.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/discovery.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/channel.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/sample_tools.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/model.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/http.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/errors.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/mimeparse.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/_auth.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/_helpers.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/googleapiclient/schema.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/version.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/variables.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/parser.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/cli.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/ipython.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/main.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/dotenv/__main__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/annotated_types/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/annotated_types/test_cases.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/datetime_helpers.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/enums.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/version.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/fields.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/primitives.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/message.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/utils.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/_file_info.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/_package_info.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/proto/modules.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/httplib2/auth.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/httplib2/iri2uri.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/httplib2/error.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/httplib2/certs.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/httplib2/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/httplib2/cacerts.txt
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/google_api_core-2.27.0.dist-info/top_level.txt
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/grpc/_typing.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/grpc/_compression.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/grpc/_channel.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/grpc/_common.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/grpc/__init__.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/grpc/_utilities.py
/Users/himanshusharma/Documents/Silver Lining/venv/lib/python3.13/site-packages/grpc/_simple_stubs.py
Bash
IN
find /Users/himanshusharma/Documents/Silver\ Lining -not -path "*/venv/*" -not -path "*/.git/*" -type f \( -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name ".env*" \) | sort

OUT
/Users/himanshusharma/Documents/Silver Lining/.env
/Users/himanshusharma/Documents/Silver Lining/README.md
/Users/himanshusharma/Documents/Silver Lining/config.py
/Users/himanshusharma/Documents/Silver Lining/main.py
/Users/himanshusharma/Documents/Silver Lining/requirements.txt
/Users/himanshusharma/Documents/Silver Lining/runtime.txt
/Users/himanshusharma/Documents/Silver Lining/tests/db_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/gemini_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/image.py
/Users/himanshusharma/Documents/Silver Lining/tests/imdb_rating_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/movie_database.py
/Users/himanshusharma/Documents/Silver Lining/tests/notiontest.py
/Users/himanshusharma/Documents/Silver Lining/tests/notiontest2.py
/Users/himanshusharma/Documents/Silver Lining/tests/summary_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/test.py
/Users/himanshusharma/Documents/Silver Lining/tests/test2.py
/Users/himanshusharma/Documents/Silver Lining/tests/time_test.py
/Users/himanshusharma/Documents/Silver Lining/tests/update.py
/Users/himanshusharma/Documents/Silver Lining/tests/youtube.py
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py
/Users/himanshusharma/Documents/Silver Lining/utils/time_utils.py
Read database_utils.py
Read time_utils.py
Read README.md
Bash
IN
ls -la /Users/himanshusharma/Documents/Silver\ Lining | grep -v venv

OUT
total 152
drwxr-xr-x@  17 himanshusharma  staff    544 May 26 17:58 .
drwx------@ 179 himanshusharma  staff   5728 May 26 17:58 ..
-rw-r--r--@   1 himanshusharma  staff   8196 Apr 14 01:02 .DS_Store
-rw-r--r--@   1 himanshusharma  staff    325 Apr 17 08:50 .env
drwxr-xr-x@  14 himanshusharma  staff    448 May 26 17:03 .git
-rw-r--r--@   1 himanshusharma  staff     57 Apr 17 08:50 .gitignore
-rw-r--r--@   1 himanshusharma  staff     22 Nov  2  2025 Procfile
-rw-r--r--@   1 himanshusharma  staff   9291 Apr 17 20:33 README.md
drwxr-xr-x@   4 himanshusharma  staff    128 May 21 00:05 __pycache__
-rw-r--r--@   1 himanshusharma  staff   1319 May 10 00:06 config.py
-rw-r--r--@   1 himanshusharma  staff  27578 May 16 15:18 main.py
-rw-r--r--@   1 himanshusharma  staff    691 Apr 17 00:17 requirements.txt
-rw-r--r--@   1 himanshusharma  staff     13 Nov  2  2025 runtime.txt
drwxr-xr-x@   9 himanshusharma  staff    288 Apr 17 00:17 test images
drwxr-xr-x@  17 himanshusharma  staff    544 Apr 25 14:57 tests
drwxr-xr-x@   7 himanshusharma  staff    224 May 26 17:58 utils
Bash
IN
ls -la /Users/himanshusharma/Documents/Silver\ Lining/tests/

OUT
total 240
drwxr-xr-x@ 17 himanshusharma  staff    544 Apr 25 14:57 .
drwxr-xr-x@ 17 himanshusharma  staff    544 May 26 17:58 ..
drwxr-xr-x@  6 himanshusharma  staff    192 Apr 25 14:57 __pycache__
-rw-r--r--@  1 himanshusharma  staff   8274 Nov 16  2025 db_test.py
-rw-r--r--@  1 himanshusharma  staff   1278 Dec 31 01:43 gemini_test.py
-rw-r--r--@  1 himanshusharma  staff   3757 Mar 13 21:49 image.py
-rw-r--r--@  1 himanshusharma  staff    984 Mar 23 00:09 imdb_rating_test.py
-rw-r--r--@  1 himanshusharma  staff  11729 Mar 20 23:14 movie_database.py
-rw-rw-r--@  1 himanshusharma  staff   7333 Mar 14 00:31 movie_list.csv
-rw-r--r--@  1 himanshusharma  staff   1977 Mar  6 00:05 notiontest.py
-rw-r--r--@  1 himanshusharma  staff   4227 Mar 10 23:57 notiontest2.py
-rw-r--r--@  1 himanshusharma  staff  29370 Dec  8 06:50 summary_test.py
-rw-r--r--@  1 himanshusharma  staff   5970 Oct 24  2025 test.py
-rw-r--r--@  1 himanshusharma  staff   8416 Oct 30  2025 test2.py
-rw-r--r--@  1 himanshusharma  staff   4010 Nov  3  2025 time_test.py
-rw-r--r--@  1 himanshusharma  staff   1267 Mar  6 00:59 update.py
-rw-r--r--@  1 himanshusharma  staff   2092 Apr 25 14:26 youtube.py
Read youtube.py
Read .env
Bash
IN
grep -r "def " /Users/himanshusharma/Documents/Silver\ Lining/utils/ | grep -v ".pyc" | head -50

OUT
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def generate_week_list(end_date):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def daily_patching(date):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def sort_records_by_name(records):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def find_all_records_by_date(collection, date, name=None, game=None):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def check_winner(date):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def generate_daily_summary(date):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def check_score_difference(date):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def check_week_winner(end_date):
/Users/himanshusharma/Documents/Silver Lining/utils/daily_utils.py:def generate_weekly_summary(end_date):
/Users/himanshusharma/Documents/Silver Lining/utils/time_utils.py:def get_date_yesterday(date_format=date_format):
/Users/himanshusharma/Documents/Silver Lining/utils/time_utils.py:def get_date_now(day=False, date_format=date_format):
/Users/himanshusharma/Documents/Silver Lining/utils/time_utils.py:def get_time_now():
/Users/himanshusharma/Documents/Silver Lining/utils/time_utils.py:def get_last_sunday_date(date_format=date_format):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def _get_imdb_suggestion(title):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def _get_imdb_image_for_title(title):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def _get_imdb_title_id(title):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def get_movie_name_from_id(movie_id):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def get_imdb_rating(movie_title):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def get_movie_image_url(movie_title):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def get_movie_genre(movie_title):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def add_page_to_movies(movie, person, queued="Not Queued"):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def check_movie_database(movie_name):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def check_no_queued():
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def check_oldest_queued():
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def change_queued_status(movie_name, new_status):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def check_current_winner():
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def movie_summary(movie_title):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def get_youtube_thumbnail_url(youtube_url):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def _get_youtube_video_id(youtube_url):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def get_youtube_title(youtube_url):
/Users/himanshusharma/Documents/Silver Lining/utils/movie_utils.py:def add_video_page_to_movies(url, image, title, person, queued="Not Queued"):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def get_data_source_id(database_id):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def get_data_source_properties(data_source_id):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def add_page_to_scores(data_source_id, date, name, game, score, tries=None):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def update_page_in_scores(page_id, score, tries=None):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def add_page_to_daily_winners(data_source_id, date, name, a, h):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def add_page_to_weekly_winners(data_source_id, date, name, a, h, difference):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def add_page_to_day(date):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def find_page_id_by_date_and_name(data_source_id, date):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def update_page_in_day(name, date, wordle=None, globle=None, echo_chess=None, connections_score=None, connections_tries=None):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def insert_record(record, collection):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def update_record(collection, date, name, new_score, game=None):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def delete_specific_record(collection, date, name, game=None):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def find_record(collection, date, name=None, game=None):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def get_page_id(collection, date, name, game):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def print_all_records(collection):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def get_score(date, name=None, game=None):
/Users/himanshusharma/Documents/Silver Lining/utils/database_utils.py:def if_exists(collection, date, name=None, game=None):
Good. Now let me read the key files directly to confirm exact function signatures and patterns.

Read database_utils.py
Read movie_utils.py
Now let me read main.py to understand the full command handler pattern.

Read main.py
Read config.py
Good, I have everything I need. Here is the full implementation plan.

/add_activity Implementation Plan
1. Overall Feature Flow

User: /add_activity
Bot:  [keyboard] Manual Entry | Receipt/Ticket Upload | Cancel

── Manual Entry path ──────────────────────────────────────────────────
  Ask Date (text) → Ask Type (keyboard) → Ask Person (keyboard)
  → Ask Favourite (keyboard) → Ask Time of Day (keyboard)
  → Ask Photo (keyboard: Upload / Skip) → Ask Notes (keyboard: Add / Skip)
  → Show Summary → [keyboard] Confirm | Edit | Cancel
  → If Edit: pick field → re-ask → back to Summary
  → If Confirm: resolve relations → create Notion pages → success

── Receipt / Ticket Upload path ────────────────────────────────────────
  Ask for photo/file
  → Download image (BytesIO, no disk)
  → Run LangGraph extraction pipeline
  → Ask Person (keyboard) [not extractable]
  → Ask Favourite (keyboard) [not extractable]
  → Ask Time of Day (keyboard) [if not derivable from extracted time]
  → Show Summary with all extracted + user-provided values
  → [keyboard] Confirm | Edit | Retry | Cancel
  → If Retry: re-upload or re-run extraction
  → If Edit: pick field → re-ask → back to Summary
  → If Confirm: resolve relations → create Notion pages → success

── Shared creation flow ────────────────────────────────────────────────
  1. Resolve Year page ID from Date
  2. Find or create Movie page (if type includes Movie)
  3. Find or create Restaurant page (if type includes Food/restaurant)
  4. Find or create Food Item pages (if food items were extracted)
  5. Create Dates page with all collected data + relation IDs
  6. Update Food Item pages with back-relation to Dates (if property exists)
  7. Send confirmation message
2. Files You Would Add
File	Purpose
utils/activity_utils.py	All Notion helpers for Dates, Restaurants, Food Items + year resolution + step-handler function
utils/activity_graph.py	LangGraph StateGraph definition for receipt extraction
utils/activity_prompts.py	All Gemini prompts for extraction nodes, stored as module-level string constants
3. Files You Would Modify
File	What Changes
main.py	Add send_keyboard() helper; add /add_activity@silverlining12bot trigger; add /add_activity block in the pending dispatch section
utils/database_utils.py	Add RESTAURANTS_DATA_SOURCE_ID; add YEARS_DATA_SOURCE_ID (or extend YEAR_2026_PAGE_ID mapping); add get_year_page_id(date_str) helper
utils/movie_utils.py	Add get_movie_page_id(movie_name) — same query as check_movie_database but returns page_id instead of bool; optionally add find_or_create_movie_page(movie_name) that wraps check + create
requirements.txt	Add langgraph
4. Existing Helpers / Modules You Would Inspect and Reuse
Helper	Location	How Reused
ACTIVITIES_DATA_SOURCE_ID	database_utils.py:177	Parent for Dates page creation
FOOD_DATA_SOURCE_ID	database_utils.py:178	Parent for Food Item page creation
MOVIE_DATA_SOURCE_ID	database_utils.py:175	Movie relation lookup
YEAR_2026_PAGE_ID	database_utils.py:179	Year relation (extended to a lookup helper)
PAGES_END_POINT, DATA_SOURCE_END_POINT, headers	config.py	All Notion API calls
check_movie_database(movie_name)	movie_utils.py:171	Check if movie already in Notion
add_page_to_movies(movie, person)	movie_utils.py:124	Create movie page if not found, reuse as-is
_get_imdb_suggestion(title)	movie_utils.py:14	IMDb lookup in movie resolution
_get_imdb_title_id(title)	movie_utils.py:39	IMDb ID for movie dedup
model (Gemini)	config.py:15	All LangGraph extraction nodes use this
send_message()	main.py:21	All Telegram replies
get_date_now(), notion_date_format	time_utils.py	Date formatting
pending dict pattern	main.py:10	Extended with step and data fields
5. Telegram Command Flow Step-by-Step

1.  User sends /add_activity@silverlining12bot
2.  Bot calls send_keyboard() → "How do you want to add this activity?"
    Buttons: [[Manual Entry], [Receipt / Ticket Upload], [Cancel]]
    pending[key] = {command: "/add_activity", step: "choose_mode", data: {}, ...}

── MANUAL PATH ──────────────────────────────────────
3.  User taps "Manual Entry"
    → step = "ask_date"
    → Bot: "What date was this? (e.g. 25/05/2026)" [force_reply]

4.  User types a date
    → parse to YYYY-MM-DD, store data["date"]
    → step = "ask_type"
    → send_keyboard() → "What type of activity?"
    Buttons (rows of 3): [[Fancy, Activity, Drive], [Game, Food, Shopping],
                          [Chilling, Movie, Nightlife], [Attraction, Nature]]

5.  User picks type(s)
    (First version: one tap = one type; plan for multi-select noted below)
    → store data["type"] = [selected]
    → step = "ask_person"
    → send_keyboard() → "Who went?"  [[Aabha], [Himanshu], [Both]]

6.  User picks person → store data["person"]
    → step = "ask_favourite"
    → send_keyboard() → "Was this a favourite?" [[Yes], [No]]

7.  User picks → store data["favourite"]
    → step = "ask_time_of_day"
    → send_keyboard() → "Time of day?" [[Day], [Night], [Both]]

8.  User picks → store data["time_of_day"]
    → step = "ask_photo"
    → send_keyboard() → "Want to add a photo?" [[Upload Photo], [Skip]]

9a. User taps Upload Photo → step = "wait_for_photo"
    Bot: "Send the photo now." [force_reply]
9b. User taps Skip → step = "ask_notes" (skip to 10)

10. If photo received: download BytesIO, upload to external file host (see note §17),
    store data["photo_url"]
    → step = "ask_notes"
    → send_keyboard() → "Any notes?" [[Add Notes], [Skip]]

11a. User taps Add Notes → step = "wait_for_notes"
     Bot: "Type your notes." [force_reply]
11b. User taps Skip → step = "review"

12. If notes received: store data["notes"] → step = "review"

13. step = "review": call build_activity_summary(data)
    → send_message() with formatted summary
    → send_keyboard() → [[Confirm], [Edit], [Cancel]]

14a. User taps Confirm → resolve relations → create pages → send success
14b. User taps Cancel → del pending[key], send "Cancelled."
14c. User taps Edit → step = "edit_field"
     send_keyboard() → list of editable fields

15. User picks field → step = "edit_value"
    Bot re-asks for that specific field (keyboard or force_reply)

16. User provides new value → update data[field] → step = "review" (loop back to 13)

── RECEIPT PATH ─────────────────────────────────────
3.  User taps "Receipt / Ticket Upload"
    → step = "wait_for_receipt"
    → Bot: "Send a photo of your receipt or ticket." [force_reply]

4.  User sends image
    → download BytesIO (same pattern as globle handler in main.py:267-283)
    → store data["receipt_bytes"]
    → step = "extracting"
    → Bot: "Extracting details..." [non-blocking send]
    → run activity_graph.run_extraction(image_bytes) synchronously
    → merge results into data{}
    → step = "ask_person" (never extractable from receipt)
    → send_keyboard() → "Who went?" [[Aabha], [Himanshu], [Both]]

5.  Continue: ask_favourite → ask_time_of_day (skip if extracted confidently)
    → step = "review"

6.  Review: show full summary including extracted values
    → send_keyboard() → [[Confirm], [Edit], [Retry], [Cancel]]

7a. Confirm → create pages
7b. Edit → same field edit flow as manual
7c. Retry → step = "wait_for_receipt", Bot: "Send a clearer receipt/ticket."
7d. Cancel → del pending[key]
6. LangGraph State Structure

# utils/activity_graph.py

from typing import TypedDict, Optional

class ActivityState(TypedDict):
    # Input
    image_bytes: bytes

    # First-pass raw extraction
    raw_text: Optional[str]          # full Gemini OCR/parse output

    # Extracted fields
    date: Optional[str]              # YYYY-MM-DD or None
    types: list[str]                 # e.g. ["Food", "Movie"]
    location: Optional[str]
    movie_name: Optional[str]
    restaurant_name: Optional[str]
    food_items: list[dict]           # [{"dish": str, "price": Optional[float], "cuisine": Optional[str]}]
    total_price: Optional[float]
    cuisine: list[str]               # e.g. ["Japanese", "Italian"]
    notes: Optional[str]

    # Control / metadata
    errors: list[str]
    retry_count: int
7. LangGraph Nodes and Conditional Edges

Nodes
─────
extract_raw_text        reads image_bytes, sends to Gemini with RAW_TEXT_EXTRACTION_PROMPT,
                        stores full structured response in state["raw_text"]

extract_date            reads raw_text, sends with DATE_EXTRACTION_PROMPT,
                        stores state["date"] as YYYY-MM-DD or None

classify_type           reads raw_text, sends with TYPE_CLASSIFICATION_PROMPT,
                        stores state["types"] as list of valid Type options

extract_location        reads raw_text, sends with LOCATION_EXTRACTION_PROMPT,
                        stores state["location"]

route_by_type           conditional node: checks state["types"]

extract_movie           reads raw_text + "movie_name" hint, sends with MOVIE_EXTRACTION_PROMPT,
                        stores state["movie_name"]

extract_restaurant      reads raw_text, sends with RESTAURANT_EXTRACTION_PROMPT,
                        stores state["restaurant_name"]

extract_food_items      reads raw_text, sends with FOOD_ITEMS_EXTRACTION_PROMPT,
                        stores state["food_items"] as list of dicts

extract_price_details   reads raw_text + food_items, sends with PRICE_EXTRACTION_PROMPT,
                        fills prices into food_items, stores state["total_price"]

extract_cuisine         reads raw_text + restaurant_name + food_items,
                        sends with CUISINE_EXTRACTION_PROMPT, stores state["cuisine"]

normalize_data          reads all fields, sends with NORMALIZATION_PROMPT for final validation,
                        fills state["errors"] for any fields that look wrong

Edges
─────
START → extract_raw_text
extract_raw_text → extract_date
extract_raw_text → classify_type
extract_raw_text → extract_location
classify_type → route_by_type

route_by_type:
  "Movie" in types  → extract_movie  → normalize_data
  "Food"  in types  → extract_restaurant → extract_food_items
                                        → extract_price_details
                                        → extract_cuisine
                                        → normalize_data
  neither           → normalize_data

extract_date  → normalize_data
extract_location → normalize_data
normalize_data → END
The graph is compiled and called synchronously via graph.invoke(initial_state) — no async needed; fits the existing polling model.

8. Prompt File Structure

# utils/activity_prompts.py

RAW_TEXT_EXTRACTION_PROMPT = """
You are a receipt/ticket parser. Given the image, extract ALL readable text and numbers 
in a structured way. Include: any dates, prices, item names, venue names, locations, 
movie/event names, totals. Do not interpret yet — just faithfully extract the text.
Output as JSON with keys: dates_found, venue, items, prices, location_hints, other_text.
If unreadable, return {"error": "unreadable"}.
"""

DATE_EXTRACTION_PROMPT = """
Given this extracted receipt/ticket text:
{raw_text}

Identify the TRANSACTION DATE, ACTIVITY DATE, BOOKING DATE, or TICKET DATE.
Rules:
- Use the date of the actual activity/booking/purchase, not terms & conditions dates,
  validity periods, ad expiry dates, or promotional dates.
- Return ONLY in format YYYY-MM-DD.
- If no clear date found, return null.
"""

TYPE_CLASSIFICATION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Classify the activity type. Choose one or more from ONLY these options:
Fancy, Activity, Drive, Game, Food, Shopping, Chilling, Movie, Nightlife, Attraction, Nature

Rules:
- Movie ticket → Movie
- Restaurant receipt → Food
- Grocery/supermarket → Shopping
- Theme park → Attraction
- Bar/club → Nightlife
Return as JSON array, e.g. ["Food"] or ["Movie", "Food"]
"""

LOCATION_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the venue name and/or address/location.
Return as a plain string. If not found, return null.
"""

MOVIE_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the full movie title being watched.
Return ONLY the movie title as a plain string. If not found, return null.
"""

RESTAURANT_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the restaurant or food establishment name.
Return ONLY the restaurant name as a plain string. If not found, return null.
"""

FOOD_ITEMS_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract each individual dish or food item ordered.
Return as JSON array: [{"dish": "name", "price": 12.50, "quantity": 1}]
Use null for price or quantity if not found. Return [] if no items found.
"""

PRICE_EXTRACTION_PROMPT = """
Given this receipt/ticket text:
{raw_text}

Extract the total bill amount. Return ONLY the numeric value (e.g. 45.80).
If not found, return null.
"""

CUISINE_EXTRACTION_PROMPT = """
Given this restaurant name "{restaurant_name}" and items {food_items},
identify the cuisine type(s).
Return as JSON array of strings from common cuisine categories.
Example: ["Japanese"] or ["Italian", "Mediterranean"]
"""

NORMALIZATION_PROMPT = """
Review these extracted activity values:
{state_json}

Check for obvious errors:
- Date should be a real valid date in YYYY-MM-DD format
- Types should only contain valid options: Fancy/Activity/Drive/Game/Food/Shopping/Chilling/Movie/Nightlife/Attraction/Nature
- Prices should be positive numbers

Return JSON with same structure plus an "errors" list describing any problems found.
If all looks good, errors should be [].
"""
9. Manual Entry Flow (Detailed)

Step         Bot asks                          Input type        Stored in data{}
──────────── ───────────────────────────────── ───────────────── ────────────────────
ask_date     "What date? (DD/MM/YYYY)"         force_reply text  data["date"] YYYY-MM-DD
ask_type     "What type of activity?"          keyboard          data["type"] list
ask_person   "Who went?"                       keyboard          data["person"]
ask_favourite "Was this a favourite?"          keyboard          data["favourite"]
ask_time_of_day "Time of day?"                 keyboard          data["time_of_day"]
ask_date_idea "Give it a name/title (or skip)" force_reply+Skip  data["date_idea"]
ask_photo    "Add a photo?"                    keyboard          → wait_for_photo step
ask_notes    "Any notes?"                      keyboard          → wait_for_notes step
review       <summary>                         keyboard          —
Date idea (the title property) is asked optionally. If skipped, auto-generate from type + date, e.g. "Food - 25/05/2026".

Type multi-select: show keyboard with all 11 options plus a "Done" button. Each tap adds to data["type"] list. Tapping a type a second time removes it (toggle). Tapping Done finalises.

10. Receipt / Ticket Upload Flow (Detailed)

1. User taps "Receipt / Ticket Upload"
   → step = "wait_for_receipt"
   → Bot: "Send a photo of your receipt or ticket."

2. User sends photo
   → Download using same BytesIO pattern as globle handler (main.py:267-283)
   → Store image_bytes in data["receipt_bytes"]
   → Bot: "Got it! Extracting details..."
   → Call: extracted = activity_graph.run_extraction(image_bytes)
   → Merge extracted fields into data{}:
       data["date"] = extracted["date"]
       data["type"] = extracted["types"]
       data["location"] = extracted["location"]
       data["movie_name"] = extracted["movie_name"]
       data["restaurant_name"] = extracted["restaurant_name"]
       data["food_items"] = extracted["food_items"]
       data["notes"] = extracted["notes"]
   → Also store image as data["photo_url"] if we can get a public URL (see §17, edge case 4)

3. Ask for person (keyboard) — never in a receipt
4. Ask for favourite (keyboard)
5. Ask for time of day (keyboard) — skip if extracted time clearly implies Day/Night

6. Show review summary (same as manual §9 step 13)
   Extra: show "Retry" option since this came from extraction

7. Retry flow:
   → step = "wait_for_receipt"
   → Bot: "Please send a clearer receipt or ticket."
   → repeat from step 2
run_extraction(image_bytes) in activity_graph.py is a plain function that compiles the graph, calls graph.invoke({"image_bytes": image_bytes, "errors": [], "retry_count": 0, ...}), and returns the final state.

11. Movie Relation Resolution
New function to add in movie_utils.py:


def get_movie_page_id(movie_name: str) -> Optional[str]:
    """Return Notion page_id for movie_name, or None if not in database."""
    # Same query logic as check_movie_database() but returns page_id
    movie_id = _get_imdb_title_id(movie_name)
    # query DATA_SOURCE_END_POINT / MOVIE_DATA_SOURCE_ID / query
    # filter by ID (rich_text) if movie_id exists, else by Movie (title)
    # return results[0]["id"] if results else None

def find_or_create_movie_page(movie_name: str, person: str) -> Optional[str]:
    """Return existing page_id or create new movie page. Returns page_id."""
    page_id = get_movie_page_id(movie_name)
    if page_id:
        return page_id
    return add_page_to_movies(movie_name, person)
    # add_page_to_movies already returns page_id
Flow when resolving movie relation:

Call find_or_create_movie_page(data["movie_name"], data["person"])
If None: log error, skip Movie relation (do not fail entire creation)
If page_id returned: add to data["movie_page_id"]
The add_page_to_movies() at movie_utils.py:124 already returns page_id (line 168). Reused as-is.

12. Restaurant Relation Resolution
New functions to add in activity_utils.py:


def find_restaurant_by_name(name: str) -> Optional[str]:
    """Query Restaurants database by Name (title). Return page_id or None."""
    # POST DATA_SOURCE_END_POINT / RESTAURANTS_DATA_SOURCE_ID / query
    # filter: {"property": "Name", "title": {"equals": name}}
    # return results[0]["id"] if results else None

def create_restaurant_page(name: str, cuisine: list[str] = None,
                            location: str = None, visited: str = "Yes") -> Optional[str]:
    """Create restaurant page. Return page_id."""
    # POST PAGES_END_POINT
    # properties: Name (title), Cuisine (multi_select), Location (place/rich_text),
    #             Visited (select: "Yes"), Favourite (select: "No" default)
    # Do NOT write to Photo — it is a rollup

def find_or_create_restaurant(name: str, cuisine: list[str] = None,
                               location: str = None) -> Optional[str]:
    """Return existing page_id or create. Returns page_id."""
    page_id = find_restaurant_by_name(name)
    if page_id:
        return page_id
    return create_restaurant_page(name, cuisine, location)
Database ID to add in database_utils.py:


RESTAURANTS_DATA_SOURCE_ID = "<needs confirmation from user>"
13. Food Items / 🍽️ Recipe Book Relation Resolution
New functions to add in activity_utils.py:


def find_food_item_by_dish(dish_name: str) -> Optional[str]:
    """Query Food Items database by Dish (title). Return page_id or None."""
    # POST DATA_SOURCE_END_POINT / FOOD_DATA_SOURCE_ID / query
    # filter: {"property": "Dish", "title": {"equals": dish_name}}
    # return results[0]["id"] if results else None

def create_food_item_page(dish: str, date: str, person: str,
                           cuisine: list[str] = None,
                           favourite: str = "No",
                           year_page_id: str = None) -> Optional[str]:
    """Create food item page. Return page_id."""
    # POST PAGES_END_POINT
    # properties:
    #   Dish (title), Date (date), Person (select), Cuisine (multi_select),
    #   Favourite (select), Year (relation: year_page_id), Type (select: "Dish")
    # Date is compulsory per spec
    # Type = "Dish" for outside restaurant food (default for this flow)

def find_or_create_food_item(dish: str, date: str, person: str,
                              cuisine: list[str] = None,
                              favourite: str = "No",
                              year_page_id: str = None) -> Optional[str]:
    """Return existing page_id or create. Returns page_id."""
    page_id = find_food_item_by_dish(dish)
    if page_id:
        return page_id
    return create_food_item_page(dish, date, person, cuisine, favourite, year_page_id)
Resolution flow for a list of food items:


food_item_ids = []
for item in data["food_items"]:
    page_id = find_or_create_food_item(
        dish=item["dish"],
        date=data["date"],
        person=data["person"],
        cuisine=data.get("cuisine"),
        year_page_id=data["year_page_id"]
    )
    if page_id:
        food_item_ids.append(page_id)
data["food_item_page_ids"] = food_item_ids
14. Notion Payload Preparation
New function in activity_utils.py:


def build_dates_payload(data: dict) -> dict:
    """Build the Notion page creation payload for the Dates database."""
    date_idea = data.get("date_idea") or f"{'/'.join(data['type'])} - {data['date']}"
    
    properties = {
        "Date Idea": {"title": [{"text": {"content": date_idea}}]},
        "Date": {"date": {"start": data["date"]}},
        "Person": {"select": {"name": data["person"]}},
        "Favourite": {"select": {"name": data["favourite"]}},
        "Status": {"status": {"name": "Done"}},
        "Time of Day": {"select": {"name": data["time_of_day"]}},
        "Type": {"multi_select": [{"name": t} for t in data["type"]]},
        "Year": {"relation": [{"id": data["year_page_id"]}]},
    }

    # Optional properties — only add if value is present
    if data.get("photo_url"):
        properties["Photo"] = {"files": [{"name": "Photo", "type": "external",
                                           "external": {"url": data["photo_url"]}}]}
    if data.get("notes"):
        properties["Notes"] = {"rich_text": [{"text": {"content": data["notes"]}}]}
    if data.get("location"):
        # ⚠️ Exact format depends on whether Location is a place or rich_text property
        # — see assumption §18 #6
        properties["Location"] = {"rich_text": [{"text": {"content": data["location"]}}]}
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
        "properties": properties
    }
15. Notion Page Creation / Update Order

Step  Action                                    Function
────  ────────────────────────────────────────  ────────────────────────────────────
1.    Derive year page ID from data["date"]     get_year_page_id(date)         [new in database_utils.py]
2.    Find/create Movie page (if needed)        find_or_create_movie_page()    [new in movie_utils.py]
3.    Find/create Restaurant page (if needed)   find_or_create_restaurant()    [new in activity_utils.py]
4.    Find/create Food Item pages (if needed)   find_or_create_food_item() ×N  [new in activity_utils.py]
5.    Build payload                             build_dates_payload(data)       [new in activity_utils.py]
6.    Create Dates page                         POST PAGES_END_POINT            [new in activity_utils.py]
7.    [Optional] Update Food Items with         PATCH each food item page       [new in activity_utils.py]
      Date <3 back-relation                     add "Date <3": relation to
                                                 new dates_page_id
The creation function:


def create_dates_page(data: dict) -> Optional[str]:
    """Orchestrate relation resolution and Dates page creation. Return page_id."""
    data["year_page_id"] = get_year_page_id(data["date"])
    if "Movie" in data["type"] and data.get("movie_name"):
        data["movie_page_id"] = find_or_create_movie_page(data["movie_name"], data["person"])
    if "Food" in data["type"] and data.get("restaurant_name"):
        data["restaurant_page_id"] = find_or_create_restaurant(...)
    if data.get("food_items"):
        data["food_item_page_ids"] = [find_or_create_food_item(...) for each item]
    
    payload = build_dates_payload(data)
    response = requests.post(PAGES_END_POINT, headers=headers, json=payload)
    response.raise_for_status()
    dates_page_id = response.json()["id"]

    # Back-relate food items if Date <3 relation exists
    for fid in data.get("food_item_page_ids", []):
        update_food_item_date_relation(fid, dates_page_id)

    return dates_page_id
16. Review, Edit, Retry, and Cancel Logic
Review summary builder (build_activity_summary(data) in activity_utils.py):


📋 Activity Summary
───────────────────
Date:        25/05/2026
Date Idea:   Food - 25/05/2026
Type:        Food
Person:      Both
Favourite:   Yes
Time of Day: Night
Status:      Done (auto)
Year:        2026 (auto)

Relations:
🎬 Movie:      —
🍽️ Restaurant: Sushi Tei (will create)
   Cuisine:   Japanese
🥘 Food Items: Salmon Sashimi ($18), Miso Soup ($5)

Photo:    ✓
Location: Vivocity, Singapore
Notes:    Great evening out!
───────────────────
Edit flow:


step = "edit_field"
Bot: send_keyboard() → list of editable fields
     e.g. [[Date], [Type], [Person], [Favourite], [Time of Day],
            [Photo], [Notes], [Location], [Movie], [Restaurant], [Food Items]]

User picks field → step = "edit_value"
Bot re-asks for that field using same keyboard or force_reply as in original flow
User provides value → update data[field] → step = "review"
Summary is shown again with updated value
Retry flow (receipt mode only):


User taps Retry
→ clear extracted fields from data{} (keep mode="receipt")
→ step = "wait_for_receipt"
→ Bot: "Send a clearer receipt or ticket photo."
→ Same extraction pipeline re-runs
Cancel:


User taps Cancel at any step
→ del pending[key]
→ send_keyboard with remove_keyboard marker
→ Bot: "Cancelled. No changes were made."
Expiry extension: The default 120-second expiry is too short for this flow. For /add_activity, set expiry to time.time() + 600 (10 minutes) and refresh it on every valid interaction.

17. Edge Cases to Handle
Invalid date format: Catch parse errors, re-ask with error message and example format.
Type toggle (multi-select): Track selected types as a list in data["type"]. If user sends a type already in the list, remove it (toggle). Add a "Done ✓" option to confirm selection.
Movie not found on IMDb: _get_imdb_suggestion() returns None. Gracefully skip Movie relation and note in summary "Movie not linked."
Telegram photo for Dates Photo property: Telegram returns a file that can be downloaded as BytesIO. Notion's files property requires a public URL. You currently have no file hosting integration. Options: (a) skip Photo in first milestone; (b) upload to a service like Cloudinary/Imgur and store the URL. Flag for confirmation.
Restaurant not found, cuisine unknown: Create restaurant with Name only, leave Cuisine empty. Note in summary.
Location property type: "place" is not a standard Notion API v1 property type — it may be rich_text, url, or a newer location type. Need to query actual schema with get_data_source_properties(ACTIVITIES_DATA_SOURCE_ID) to confirm format before building payload.
Year page ID beyond 2026: Only YEAR_2026_PAGE_ID is currently defined. Need either a full Years database query or a hardcoded mapping {2026: "...", 2025: "..."}. Flag for confirmation.
Bot not in a thread: message_thread_id is required for existing commands. The /add_activity handler should guard for None thread id, same as existing commands.
LangGraph extraction failure: If any node raises an exception, catch it in run_extraction(), populate errors, and return a partial state. The Telegram handler then shows a "partial extraction" summary where unextracted fields are blank.
Food item already exists: find_food_item_by_dish() matches by exact dish name. Partial matches won't be caught. For v1, exact match is fine. Flag as a known limitation.
Concurrent /add_activity sessions: Two users can each have their own pending key since the key is (chat_id, user_id, message_thread_id). No collision issue.
User sends a non-keyboard text when a keyboard is shown: Validate that the response matches one of the expected options. If not, re-show keyboard with error message.
18. Assumptions You Need to Confirm Before Implementation
RESTAURANTS_DATA_SOURCE_ID — Not in the codebase. Please provide the Restaurants Notion database ID so it can be added to database_utils.py.
Years database — Is there a Years Notion database I should query dynamically to resolve Year relation IDs for any year? Or should I maintain a hardcoded mapping (currently only 2026 exists)?
Photo upload for Dates — Notion requires a public URL for the files property. Do you have a file hosting service (Cloudinary, Imgur, etc.) integrated or want one added? Or should Photo be skipped in early milestones?
Location property type — Is the Location property in the Dates database rich_text, url, or a Notion location type? (I can check with get_data_source_properties() but want to confirm before building the payload.)
Status property format — Is Status in the Dates database a Notion status type ({"status": {"name": "Done"}}) or a select type ({"select": {"name": "Done"}})?
Date <3 back-relation — Should Food Items always be updated with a back-relation to the created Dates page? And is the property name exactly Date <3?
Date Idea when user doesn't provide one — Is an auto-generated title like "Food - 25/05/2026" acceptable as the fallback? Or do you always want to prompt for it?
Type multi-select in Manual Entry — For the first version, is one type per activity acceptable? Or do you need multi-select from the start (with a "Done" button to end selection)?
choosemovie person logic — add_page_to_movies() takes a person arg. For movie relation in /add_activity, should the person be whoever logged the activity (from user_name) or the Person field they selected?
Restaurants database property: Visited — The select options you specified are Yes/No. For this flow (completed activity), should Visited always be set to Yes?
Milestones
Milestone 1 — Entry point and keyboard
Achieves: /add_activity command works; mode selection keyboard appears; Cancel works; pending state is initialized.

Files touched: main.py

Helpers reused: send_message(), pending dict

New helpers added: send_keyboard(chat_id, text, buttons, message_thread_id) in main.py; remove_keyboard() in main.py

Expected behavior:

User sends /add_activity@silverlining12bot in a thread
Bot replies with keyboard: Manual Entry | Receipt/Ticket Upload | Cancel
Tapping Cancel dismisses keyboard and sends "Cancelled."
Pending entry is created with step = "choose_mode"
How to test: Send /add_activity@silverlining12bot in the group thread. Verify keyboard appears. Tap Cancel — verify keyboard disappears and "Cancelled." is sent. Tap Manual Entry — verify bot asks for date.

Milestone 2 — Manual Entry flow (required fields, no Notion yet)
Achieves: Full conversation flow from mode selection through to the review summary, with all required fields collected. No Notion writes yet — just validates the step machine works.

Files touched: main.py, utils/activity_utils.py (new)

Helpers reused: send_keyboard(), send_message(), pending dict pattern

New helpers added:

handle_add_activity_step(update, pending_entry) in activity_utils.py — the step dispatcher
build_activity_summary(data) in activity_utils.py
parse_date_input(text) in activity_utils.py — converts user date text to YYYY-MM-DD
Expected behavior: All steps work in order. Keyboard buttons map to correct values. Review summary is accurate. Edit flow allows changing any field and re-showing summary. Cancel works at any step.

How to test: Complete the full Manual Entry flow with all fields. Verify summary text matches what was entered. Test Edit for each field. Test Cancel mid-flow.

Milestone 3 — Basic Dates page creation in Notion
Achieves: After Confirm, a new page is created in the Dates Notion database with all required fields (no relations yet except Year).

Files touched: utils/activity_utils.py, utils/database_utils.py

Helpers reused: ACTIVITIES_DATA_SOURCE_ID, PAGES_END_POINT, headers, requests.post

New helpers added:

get_year_page_id(date_str) in database_utils.py
build_dates_payload(data) in activity_utils.py
create_dates_page(data) in activity_utils.py
Expected behavior: Confirm → page appears in Notion Dates database with Date, Person, Favourite, Status=Done, Time of Day, Type, Year relation, Date Idea. Bot sends "Activity added!" message.

How to test: Complete Manual Entry flow and tap Confirm. Check Notion database for the new page. Verify all property values match what was entered.

Milestone 4 — Receipt / ticket upload handling
Achieves: Bot accepts a photo, downloads it to BytesIO (no disk), and stores it in pending state. No extraction yet — just hardcoded placeholder values to complete the flow.

Files touched: main.py, utils/activity_utils.py

Helpers reused: File download BytesIO pattern from globle handler (main.py:267-283)

New helpers added: download_telegram_photo(update) extracted as a helper in main.py or activity_utils.py (the BytesIO download logic is duplicated for globle/echo_chess; this refactors it into one place)

Expected behavior: User taps Receipt/Ticket Upload → bot asks for photo → user sends photo → bot acknowledges receipt → shows a placeholder summary → Confirm creates a Dates page.

How to test: Tap Receipt/Ticket Upload, send any photo, verify bot acknowledges and eventually creates a Dates page (even with placeholder values).

Milestone 5 — LangGraph extraction flow
Achieves: Gemini extracts date, type, location, restaurant, food items from the receipt image. Results populate the review summary.

Files touched: utils/activity_graph.py (new), utils/activity_prompts.py (new), requirements.txt

Helpers reused: model (Gemini) from config.py

New helpers added: Full ActivityState TypedDict, all LangGraph nodes, run_extraction(image_bytes) function

Expected behavior: After photo upload, bot extracts fields and shows them in the review summary. Wrong extractions can be edited. Retry re-runs extraction.

How to test: Use a real restaurant receipt or cinema ticket photo. Verify extracted date/type/location/restaurant match what's on the receipt. Test with a blurry/unreadable photo and verify graceful error handling.

Milestone 6 — Movie relation resolution
Achieves: If activity type includes Movie and a movie name was extracted or entered, the correct Notion movie page is linked or created.

Files touched: utils/movie_utils.py, utils/activity_utils.py

Helpers reused: check_movie_database(), add_page_to_movies(), _get_imdb_suggestion(), _get_imdb_title_id()

New helpers added: get_movie_page_id(movie_name) in movie_utils.py; find_or_create_movie_page(movie_name, person) in movie_utils.py

Expected behavior: For a movie activity, the Movie relation in the Dates page links to the correct existing movie page (or a newly created one). No duplicate pages are created.

How to test: Add a Movie activity with a film already in your Notion movies database. Verify the relation links to the existing page, not a new one. Then add one that doesn't exist and verify a new page is created with correct IMDb data.

Milestone 7 — Restaurant relation resolution
Achieves: If activity includes Food, the restaurant is found or created in the Restaurants database, and linked to the Dates page.

Files touched: utils/activity_utils.py, utils/database_utils.py

Helpers reused: FOOD_DATA_SOURCE_ID, PAGES_END_POINT, DATA_SOURCE_END_POINT, headers

New helpers added: find_restaurant_by_name(), create_restaurant_page(), find_or_create_restaurant() — all in activity_utils.py

Prerequisite: RESTAURANTS_DATA_SOURCE_ID confirmed and added.

Expected behavior: Food activity links to the correct Restaurant page. New restaurants are created with Name + Cuisine + Location + Visited=Yes.

How to test: Add a Food activity with a restaurant already in Notion — verify it links. Add one with a new restaurant — verify it's created and linked.

Milestone 8 — Food Items / 🍽️ Recipe Book relation resolution
Achieves: Individual dishes from a restaurant receipt are created or found as Food Item pages and linked to the Dates page via 🍽️ Recipe Book. Food Items are also back-related to the Dates page via Date <3.

Files touched: utils/activity_utils.py

Helpers reused: FOOD_DATA_SOURCE_ID, get_year_page_id()

New helpers added: find_food_item_by_dish(), create_food_item_page(), find_or_create_food_item(), update_food_item_date_relation() — all in activity_utils.py

Expected behavior: Each extracted dish becomes a Food Item page (or links to existing). All are linked to the Dates page via 🍽️ Recipe Book. Each Food Item page has Date, Person, Year, Type=Dish filled.

How to test: Use a restaurant receipt with multiple dishes. Verify each dish has a Food Item page in Notion, all linked from the Dates page. Add a dish that already exists — verify no duplicate.

Milestone 9 — Review / edit / retry / cancel polish
Achieves: All edge cases from §17 are handled. Edit flow works for all fields. Retry re-runs extraction cleanly. Expiry is extended to 10 minutes. Keyboard is always removed on cancel/complete. Error messages are user-friendly.

Files touched: main.py, utils/activity_utils.py, utils/activity_graph.py

Expected behavior: Robust end-to-end flow. Can edit any field individually. Retry works from receipt mode. Cancel at any step leaves no partial data in Notion. Unknown keyboard inputs re-show options.

How to test: Run through the full flow and intentionally: send wrong date format, send non-keyboard text when keyboard shown, cancel at each step, use Retry twice before confirming.