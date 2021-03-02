import datetime
import pytz
from dateutil.parser import parse
from app.core.config import (
    TIMEZONE
)

tz = pytz.timezone(TIMEZONE)

def today():
    today = datetime.datetime.now(tz=tz).date()
    return today

def is_valid_date(instring):
    try:
        xx = parse(instring)
        return True
    except Exception as e:
        return False

def get_this_year():

    this_year = datetime.datetime.now(tz=tz).date().isoformat()[0:4]

    return this_year

def get_period_start_end(year, quarter=None):

    if quarter is None:
        period_start = f"{year}-01-01"
        period_end = f"{year}-12-31"
    else:
        if quarter == "Q1":
            period_start = f"{year}-01-01"
            period_end = f"{year}-03-31"
        elif quarter == "Q2":
            period_start = f"{year}-04-01"
            period_end = f"{year}-06-30"
        elif quarter == "Q3":
            period_start = f"{year}-07-01"
            period_end = f"{year}-09-01"
        elif quarter == "Q4":
            period_start = f"{year}-10-01"
            period_end = f"{year}-12-31"

        else:
            raise ValueError("Invalid year or quarter.")

    return period_start, period_end
