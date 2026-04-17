<div align="center">

# Silver Lining ✨

> A Telegram scoreboard bot for daily puzzle games, friendly rivalry, and the ritual of sending your score before midnight.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-Scoreboard-000000?style=for-the-badge&logo=notion&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Records-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

<b>Telegram topics</b> · <b>Daily scores</b> · <b>Notion logs</b> · <b>Weekly bragging rights</b>

</div>

Silver Lining is a little passion project I built for tracking daily game scores in a Telegram group. It watches game-specific Telegram topics, collects scores, saves them to MongoDB, mirrors them into Notion, and posts daily/weekly winner summaries so nobody has to keep a mental spreadsheet in their head.

<table>
  <tr>
    <td align="center" bgcolor="#D7ECFF"><font color="#1F2937"><b>💬 Telegram</b><br>topic-based submissions</font></td>
    <td align="center" bgcolor="#E4D7FF"><font color="#1F2937"><b>🧠 Gemini</b><br>screenshot score reading</font></td>
    <td align="center" bgcolor="#D9F7E6"><font color="#1F2937"><b>🗃️ Notion</b><br>cool dashboards</font></td>
    <td align="center" bgcolor="#FFE7B8"><font color="#1F2937"><b>🏆 Summaries</b><br>daily and weekly winners</font></td>
  </tr>
</table>

---

## 📸 A Peek

The screenshots that the bot reads and tracks scores from (mini is no longer in the bot because I kept losing).

<p align="center">
  <img src="test%20images/echochess4.jpeg" alt="Echo Chess result screenshot" width="205">
  <img src="test%20images/mini.jpeg" alt="Mini result screenshot" width="205">
</p>

---

## 🧩 What This Bot Does

|  |  |
| --- | --- |
| 💬 | Listens for Telegram commands inside topic threads |
| 📝 | Parses Wordle and Connections results text |
| 👀 | Uses Gemini to read Globle and Echo Chess screenshots |
| 🗃️ | Stores scores in MongoDB and mirrors them into Notion |
| 🔁 | Updates today's score if someone resubmits |
| 🌙 | Posts daily summaries at midnight Singapore time |
| 🏆 | Posts weekly summaries every Monday |
| 🍿 | Lets the weekly winner queue a movie |

Small scope. Real use case. Maximum competitiveness.


---

## 🎮 Supported Games

<table>
  <tr>
    <td align="center" bgcolor="#DDF9E4"><font color="#1F2937"><b>🟩 Wordle</b><br>text share</font></td>
    <td align="center" bgcolor="#E8DAFF"><font color="#1F2937"><b>🟪 Connections</b><br>text share</font></td>
    <td align="center" bgcolor="#D7F0FF"><font color="#1F2937"><b>🌍 Globle</b><br>screenshot</font></td>
    <td align="center" bgcolor="#FFE8BD"><font color="#1F2937"><b>♟️ Echo Chess</b><br>screenshot</font></td>
  </tr>
</table>

| Game | Command | What you send |
| --- | --- | --- |
| 🟩 Wordle | `/wordle@silverlining12bot` | The copied Wordle share text |
| 🟪 Connections | `/connections@silverlining12bot` | The copied Connections share text |
| 🌍 Globle | `/globle@silverlining12bot` | A clear screenshot of the result |
| ♟️ Echo Chess | `/echo_chess@silverlining12bot` | A clear screenshot of the result |

You can also check your saved score for today:

| Game | Check command |
| --- | --- |
| 🟩 Wordle | `/checkwordle@silverlining12bot` |
| 🟪 Connections | `/checkconnections@silverlining12bot` |
| 🌍 Globle | `/checkgloble@silverlining12bot` |
| ♟️ Echo Chess | `/checkechochess@silverlining12bot` |

---

## 💬 How Submissions Work

The bot uses a simple reply flow:

```text
game topic -> command -> bot prompt -> your result -> saved score -> Notion sync
```

1. Run the command for a game.
2. The bot replies asking for your result.
3. Send the copied text or screenshot.
4. The bot extracts the score and saves it.
5. If you submit again on the same day, it updates your existing score.

Pending replies expire after **120 seconds**, which is just enough time to find the screenshot you swore you got.

```text
/globle@silverlining12bot
Bot: Please send an image of your Globle result.
You: [sends screenshot]
Bot: Your Globle score is: 6 guesses
```

---

## 🏆 Daily And Weekly Winners

Every day at `00:00` Singapore time, Silver Lining:

- patches missing scores for both configured players
- compares results across all supported games
- records the daily winner in MongoDB and Notion
- posts a summary to the configured Telegram chat

Every Monday at `00:00`, it also rolls up the previous week:

- counts daily wins
- uses overall score difference as the tiebreaker
- records the weekly winner
- unlocks the tiny prize: movie queue rights

The weekly winner can run:

```text
/choosemovie@silverlining12bot
```

The bot checks whether they are the current winner, asks for a movie title, looks it up, and queues it in the Notion movie database. The queue keeps up to three movies at a time.

> [!TIP]
> Weekly wins are not just ceremonial. They are also the gatekeeper for `/choosemovie@silverlining12bot`.

---

## 🛠️ Telegram Setup

> [!IMPORTANT]
> Silver Lining expects topic threads. Create the game subtopics before trying the commands.

Create a Telegram group and turn on **Topics**.

Then create **4 subtopics**, one for each game:

- `Wordle`
- `Connections`
- `Globle`
- `Echo Chess`

Add the bot to the group and make sure it can read and reply to messages in topics.

This part matters: the code ignores messages that do not have a Telegram `message_thread_id`, so plain group chat messages will not trigger the game flow.

> [!IMPORTANT]
> If you use a different bot username, update the command checks in `main.py`. They currently include `@silverlining12bot`.

---

## ⚙️ Local Setup

<details>
<summary><b>Environment variables</b></summary>

Create a `.env` file in the project root:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_TOKEN=your_google_gemini_api_key
NOTION_TOKEN=your_notion_integration_token
MONGODB_TOKEN=your_mongodb_connection_string
PLAYER_1=FirstPlayerName
PLAYER_2=SecondPlayerName
```

</details>

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the bot:

```bash
python main.py
```

The repo also includes a `Procfile` for worker-style deployment:

```text
worker: python main.py
```

---

## 🗃️ Notion Integration

Notion is where the nice readable records live. The bot writes to databases for:

| Database | Purpose |
| --- | --- |
| `scores` | Daily game submissions |
| `daily winners` | Day-by-day winner records |
| `weekly winners` | Weekly rollups and tiebreakers |
| `movies` | Winner movie picks |

The database IDs are currently set in `config.py`, so swap those out if you are connecting your own workspace.

The scores database expects these properties:

| Property | Type |
| --- | --- |
| `Date Value` | Date |
| `ID` | Title |
| `Name` | Select |
| `Game` | Select |
| `Score` | Number |
| `Tries` | Number |

Daily winners, weekly winners, and movies use the property names referenced in `utils/database_utils.py` and `utils/movie_utils.py`.

> [!WARNING]
> The Notion database IDs are hard-coded in `config.py` right now. Swap them before using your own workspace.

---

## 🧪 Little Implementation Notes

<table>
  <tr>
    <td align="center" bgcolor="#E8EEF7"><font color="#1F2937"><b>Timezone</b><br>Singapore</font></td>
    <td align="center" bgcolor="#E8EEF7"><font color="#1F2937"><b>Runtime</b><br>Python 3.13.2</font></td>
    <td align="center" bgcolor="#E8EEF7"><font color="#1F2937"><b>Vision model</b><br>Gemini 2.5 Flash</font></td>
  </tr>
</table>

- Dates and summaries use **Singapore time**.
- MongoDB collections: `scores`, `daily_winners`, `weekly_winners`.
- Gemini model: `gemini-2.5-flash`.
- Wordle `X/6` is stored as `7`.
- Connections stores both solved groups and total tries.
- Globle and Echo Chess screenshots are downloaded from Telegram and processed in memory.
- The summary Telegram chat ID is currently hard-coded in `main.py`.

---

## 🗺️ Project Map

```text
.
|-- main.py                 # Telegram polling, commands, score flow
|-- config.py               # tokens, Gemini, Notion, MongoDB
|-- utils/
|   |-- daily_utils.py      # daily and weekly winner logic
|   |-- database_utils.py   # MongoDB and Notion helpers
|   |-- movie_utils.py      # IMDb lookup and movie queue
|   `-- time_utils.py       # Singapore-time helpers
|-- test images/            # sample screenshots used while building
|-- requirements.txt
|-- Procfile
`-- runtime.txt
```

---

## 💛 Why I Made This

Because daily puzzle games are more fun when they become a tiny shared ritual.

This bot keeps the boring parts tidy: who submitted, who forgot, who won the day, who won the week, and who gets to pick the movie. The rest stays where it belongs: in the group chat, with the screenshots, the excuses, and the occasional suspiciously fast solves.

---

## 👋 Author

Made by **Himanshu Sharma**.


If you want to chat about the project, puzzle bots, automation, or anything I am building next, connect with me here:

- [LinkedIn](https://www.linkedin.com/in/himanshusharma492/)
