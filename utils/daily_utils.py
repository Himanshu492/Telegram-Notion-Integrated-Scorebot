from datetime import datetime, timedelta
from utils.time_utils import *
from utils.database_utils import *
import dotenv

dotenv.load_dotenv()
player_1 = os.getenv("PLAYER_1")
player_2 = os.getenv("PLAYER_2")
games = ["globle", "connections", "echo_chess", "wordle"]

# ----- DAY AND WEEK UTILITIES -----

# generates a list of the last 7 dates ending with end_date (not inclusive)
def generate_week_list(end_date):
    end_dt = datetime.strptime(end_date, date_format)
    week_list = []
    for i in range(7):
        day = end_dt - timedelta(days=i)
        week_list.append(day.strftime(date_format))
    return week_list


# patching for missing records
def daily_patching(date):
    reversed_date = datetime.strptime(date, date_format).strftime(notion_date_format)
    for game in games:
        if game  == "connections":
            if not if_exists(scores, date, player_1, game):
                insert_record({"name": player_1, "game": game, "score": [-1, -1], "date": date}, scores)
                add_page_to_scores(SCORES_DATA_SOURCE_ID, reversed_date, player_1, game, 0, 0)
            if not if_exists(scores, date, player_2, game):
                insert_record({"name": player_2, "game": game, "score": [-1, -1], "date": date}, scores)
                add_page_to_scores(SCORES_DATA_SOURCE_ID, reversed_date, player_2, game, 0, 0)
        else:
            if not if_exists(scores, date, player_1, game):
                insert_record({"name": player_1, "game": game, "score": 1234, "date": date}, scores)
                add_page_to_scores(SCORES_DATA_SOURCE_ID, reversed_date, player_1, game, 0)
            if not if_exists(scores, date, player_2, game):
                insert_record({"name": player_2, "game": game, "score": 1234, "date": date}, scores)
                add_page_to_scores(SCORES_DATA_SOURCE_ID, reversed_date, player_2, game, 0)


# sorts a LIST of records by the 'name' field
def sort_records_by_name(records):
    return sorted(records, key=lambda x: x['name'])


# finds all records by date, with optional filters for name and game
def find_all_records_by_date(collection, date, name=None, game=None):
    query = {"date": date}
    if name:
        query["name"] = name
    if game:
        query["game"] = game
    records = collection.find(query)
    return list(records)


# checks the winner for a given date
def check_winner(date):
    h_total = 0
    a_total = 0

    for game in games:
        h_score = get_score(date, player_1, game)
        a_score = get_score(date, player_2, game)

        if game == "connections":
            h_score = list(map(int, h_score))
            a_score = list(map(int, a_score))

            if a_score[0] > h_score[0]:
                a_total += 1
            elif h_score[0] > a_score[0]:
                h_total += 1
            else:
                if a_score[0] == h_score[0] == 4:
                    if a_score[1] < h_score[1]:
                        a_total += 1
                    elif h_score[1] < a_score[1]:
                        h_total += 1
        else:
            h_score = int(h_score)
            a_score = int(a_score)

            if a_score < h_score:
                a_total += 1
            elif h_score < a_score:
                h_total += 1
            else:
                pass
    
    return (a_total, h_total)


# generates daily summary for a given date, sends the winner, and updates the daily_winners collection
def generate_daily_summary(date):
    summary = "Summary for " + date + ":\n\n"
    
    for game in games:
        daily_patching(date)

        records = find_all_records_by_date(scores, date, game=game)
        summary += game.capitalize() + ":\n"

        records = sort_records_by_name(records)

        for record in records:
            if game == "connections":
                if record["score"][0] == -1:
                    summary += f"{record['name']}: No Score\n"
                else:
                    if record["score"][0] == 4:
                        summary += f"{record['name']}: {record['score'][0]} (Total Tries: {record['score'][1]})\n"
                    else:
                        summary += f"{record['name']}: {record['score'][0]}\n"
            else:
                if record["score"] == 1234:
                    summary += f"{record['name']}: No Score\n"
                else:
                    summary += f"{record['name']}: {record['score']}\n"

        summary += "\n"

    summary += "\n"

    result = check_winner(date)
    a_total, h_total = result
    if a_total > h_total:
        winner = player_2
        summary += f"{player_2} wins {a_total} to {h_total}\n"
    elif h_total > a_total:
        winner = player_1
        summary += f"{player_1} wins {h_total} to {a_total}\n"
    else:
        winner = "Tie"
        summary += f"It's a tie ({a_total} - {h_total})\n"

    insert_record({"date": date, "winner": winner, "score": result}, daily_winners)
    reversed_date = datetime.strptime(date, date_format).strftime(notion_date_format)
    add_page_to_daily_winners(DAILY_WINNERS_DATA_SOURCE_ID, reversed_date, winner, a_total, h_total)

    return summary


def check_score_difference(date):
    score = daily_winners.find_one({"date": date}).get("score", None)
    if score:
        return score[0] - score[1]
    return None


# checks weekly winner
def check_week_winner(end_date):
    a_wins = 0
    h_wins = 0
    overall_diff = 0

    week_dates = generate_week_list(end_date)
    for date in week_dates:
        winner_record = find_record(daily_winners, date)
        if winner_record:
            winner = winner_record["winner"]
            score_diff = check_score_difference(date)
            if score_diff:
                overall_diff += score_diff
            if winner == player_2:
                a_wins += 1
            elif winner == player_1:
                h_wins += 1

    return a_wins, h_wins, overall_diff
    

def generate_weekly_summary(end_date):
    week_dates = generate_week_list(end_date)
    summary = f"Weekly Summary for {week_dates[-1]} to {week_dates[0]}:\n\n"

    for date in week_dates[::-1]:
        record = find_record(daily_winners, date)
        summary += f"{date}: {record['winner'] if record else 'No data'}\n"
    
    summary += "\n"

    a_wins, h_wins, overall_diff = check_week_winner(end_date)

    if a_wins > h_wins:
        winner = player_2
        summary += f"{player_2} wins the week {a_wins} to {h_wins}\n"
    elif h_wins > a_wins:
        winner = player_1
        summary += f"{player_1} wins the week {h_wins} to {a_wins}\n"
    else:
        if overall_diff > 0:
            winner = player_2
            summary += f"Score is tied but {player_2} wins by overall score difference of {overall_diff}\n"
        elif overall_diff < 0:
            winner = player_1
            summary += f"Score is tied but {player_1} wins by overall score difference of {abs(overall_diff)}\n"
        else:
            winner = "Tie"
            summary += "Score is tied and overall score difference is also tied\n"

    insert_record({"date": week_dates[0], "winner": winner, 
                   "score": (a_wins, h_wins), "overall_diff": overall_diff}, weekly_winners)
    
    reversed_end_date = datetime.strptime(week_dates[0], date_format).strftime(notion_date_format)
    add_page_to_weekly_winners(WEEKLY_WINNERS_DATA_SOURCE_ID, reversed_end_date, winner, a_wins, h_wins, overall_diff)

    return summary

