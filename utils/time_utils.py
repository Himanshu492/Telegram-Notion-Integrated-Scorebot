from datetime import timezone, timedelta, datetime

SINGAPORE_TZ = timezone(timedelta(hours=8))

date_format = "%d-%m-%Y"
notion_date_format = "%Y-%m-%d"
time_format = "%H:%M"

# ----- DATE / TIME UTILITIES -----
def get_date_yesterday(date_format=date_format):
    now = datetime.now(SINGAPORE_TZ)
    yesterday = now - timedelta(days=1)
    return yesterday.date().strftime(date_format)


def get_date_now(day=False, date_format=date_format):
    now = datetime.now(SINGAPORE_TZ)
    if day:
        return now.strftime("%A")
    return now.date().strftime(date_format)


def get_time_now():
    now = datetime.now(SINGAPORE_TZ)
    return now.time().strftime(time_format)


def get_last_sunday_date(date_format=date_format):
    now = datetime.now(SINGAPORE_TZ)
    days_since_sunday = (now.weekday() + 1) % 7 or 7
    last_sunday = now - timedelta(days=days_since_sunday)
    return last_sunday.date().strftime(date_format)
