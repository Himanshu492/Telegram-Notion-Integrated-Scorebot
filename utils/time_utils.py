from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

date_format = "%d-%m-%Y"
notion_date_format = "%Y-%m-%d"
time_format = "%H:%M"

DEFAULT_TZ = ZoneInfo("Asia/Singapore")

# ----- DATE / TIME UTILITIES -----
def get_date_yesterday(tz=DEFAULT_TZ, date_format=date_format):
    now = datetime.now(tz)
    yesterday = now - timedelta(days=1)
    return yesterday.date().strftime(date_format)


def get_date_now(tz=DEFAULT_TZ, day=False, date_format=date_format):
    now = datetime.now(tz)
    if day:
        return now.strftime("%A")
    return now.date().strftime(date_format)


def get_time_now(tz=DEFAULT_TZ):
    now = datetime.now(tz)
    return now.time().strftime(time_format)


def get_last_sunday_date(tz=DEFAULT_TZ, date_format=date_format):
    now = datetime.now(tz)
    days_since_sunday = (now.weekday() + 1) % 7 or 7
    last_sunday = now - timedelta(days=days_since_sunday)
    return last_sunday.date().strftime(date_format)
