from datetime import datetime
from math import ceil


def weekOfMonth(dt: datetime):
    """
    Returns the week of the month for the specified date.
    REF: https://stackoverflow.com/questions/3806473/python-week-number-of-the-month
    """
    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))


def monthdelta(date, delta):
    """
    REF: https://stackoverflow.com/questions/3424899/whats-the-simplest-way-to-subtract-a-month-from-a-date-in-python
    """
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and (not y%100==0 or y%400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)


def strip_date_timestamp(dt):
    return datetime(dt.year, dt.month, dt.day)