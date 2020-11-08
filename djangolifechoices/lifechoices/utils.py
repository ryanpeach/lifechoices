from datetime import datetime
from math import ceil


def weekOfMonth(dt: datetime):
    """
    Returns the week of the month for the specified date.
    Not by simple division, but as you would see it on a calendar.

    References
    -----------
    https://stackoverflow.com/questions/3806473/python-week-number-of-the-month
    """
    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))


def monthdelta(date: datetime, delta: int) -> datetime:
    """
    Adds or subtracts months (`delta`) from a date (`date`).

    References
    -----------
    https://stackoverflow.com/questions/3424899/whats-the-simplest-way-to-subtract-a-month-from-a-date-in-python
    """
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and (not y%100==0 or y%400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)


def strip_date_timestamp(dt: datetime) -> datetime:
    """ Get's rid of the hour, minute, and second of a datetime. """
    return datetime(dt.year, dt.month, dt.day)


def effective_interest_rate_per_period(interest_rate_per_period: float, compounding_times_per_period: float) -> float:
    """
    Finding the interest rate as if it has been compounded n times over 1 period.

    Reference
    ----------
    https://www.calculatorsoup.com/calculators/financial/effective-interest-rate-calculator.php
    """
    return (1 + interest_rate_per_period / compounding_times_per_period) ** compounding_times_per_period - 1


def interest_rate_per_period(effective_interest_rate_per_period: float, compounding_times_per_period: float) -> float:
    """ Finding the interest rate from an effective interest rate that has been compounded n times already. """
    return (-1 + (1 + effective_interest_rate_per_period)**(1/compounding_times_per_period)) * compounding_times_per_period


def effective_interest_rate_per_t_periods(
        interest_rate_per_period: float,
        compounding_times_per_period: float,
        t: float
) -> float:
    """
    Finding the interest rate as if it has been compounded n*t times over t periods.

    Reference
    ----------
    https://www.calculatorsoup.com/calculators/financial/effective-interest-rate-calculator.php
    """
    return (1 + interest_rate_per_period / compounding_times_per_period) ** (compounding_times_per_period * t) - 1

def price_at_year(
        price: float,
        yearly_inflation_rate: float,
        date: datetime,
        today: datetime = datetime.now()
):
    """ Returns the price of something with inflation some amount of time from now. """
    return price * effective_interest_rate_per_t_periods(
        interest_rate_per_period=yearly_inflation_rate,
        compounding_times_per_period=1,
        t=(date - today).days/365
    ) + price