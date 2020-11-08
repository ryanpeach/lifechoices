from typing import Dict, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

from elements.models import Transfer, Account, APR

from lifechoices.utils import weekOfMonth, monthdelta, strip_date_timestamp, effective_interest_rate_per_t_periods, \
    interest_rate_per_period


@dataclass(frozen=False)
class _GenerateFromPlanOutput:
    atstart: Dict[datetime, List[Transfer]]
    daily: List[Transfer]
    weekly: Dict[int, List[Transfer]]
    monthly: Dict[int, List[Transfer]]
    yearly: Dict[int, Dict[int, List[Transfer]]]
    accounts_by_name: Dict[str, Account]


def _generate_from_plan(p: List[Transfer]) -> _GenerateFromPlanOutput:
    atstart = defaultdict(list)
    daily = []
    weekly = defaultdict(list)
    monthly = defaultdict(list)
    yearly = defaultdict(lambda: defaultdict(list))

    accounts_by_name = {a.name: a for a in p.accounts}
    for t in p.transfers:
        t.check()
        t._n = 0
        if t.interval == Transfer.ATSTART:
            atstart[t.date].append(t)
        elif t.interval == Transfer.DAILY:
            daily.append(t)
        elif t.interval == Transfer.NDAILY:
            daily.append(t)
            assert t.repeat_n >= 2, f"repeat_n for {t.name} must be at least 2, got {t.repeat_n}"
        elif t.interval == Transfer.WEEKLY:
            weekly[t.dayOfWeek].append(t)
        elif t.interval == Transfer.NWEEKLY:
            weekly[t.dayOfWeek].append(t)
            assert t.repeat_n >= 2, f"repeat_n for {t.name} must be at least 2, got {t.repeat_n}"
        elif t.interval == Transfer.MONTHLY:
            monthly[t.dayOfMonth].append(t)
        elif t.interval == Transfer.NMONTHLY:
            monthly[t.dayOfMonth].append(t)
            assert t.repeat_n >= 2, f"repeat_n for {t.name} must be at least 2, got {t.repeat_n}"
        elif t.interval == Transfer.YEARLY:
            yearly[t.month][t.dayOfMonth].append(t)
        elif t.interval == Transfer.NYEARLY:
            yearly[t.month][t.dayOfMonth].append(t)
            assert t.repeat_n >= 2, f"repeat_n for {t.name} must be at least 2, got {t.repeat_n}"
        else:
            raise TypeError(f"Type '{type(t)}' not recognized.")
    return _GenerateFromPlanOutput(
        atstart, daily, weekly, monthly, yearly, accounts_by_name
    )


def apr_to_daily(apr: APR) -> float:
    """ Given an apr, returns a daily rate to adjust by. """
    if apr.period == APR.APRPeriod.DAILY:
        return apr.value
    return interest_rate_per_period(apr.value, APR.APRPeriod.DAILY.value/apr.period)


# TODO: Append all dates removing the timestamp
# This is our main function
def calculate_accounts(
        accounts: List[Account],
        transfers: List[Transfer],
        from_date: datetime,
        to_date: datetime,
        tall_data: bool = True
) -> List[Dict[str, float]]:
    """
    This is the main data plotting function in the code.
    It takes a starting plan, a sequence of bridges, and a to/from date.
    It returns a list of dictionaries (Like a pandas dataframe) containing accounts and their values, along with a
    tag called "Date" that tells you what date it was. Sorted by date ascending.
    Easiest thing to do is to take this and create a pandas Dataframe from it, and use that to plot it.

    If you use the flag tall_data the data will look like this:
    Date  Account  Value
    Date1 Account1 Value1
    Date1 Account2 Value2
    Date2 Account1 Value3
    Date2 Account2 Value4
    ...   ...      ...
    If you set it to false the data will look like this:
    Date  Account1 Account2 ...
    Date1 Value1   Value2   ...
    Date2 Value3   Value4   ...
    ...   ...      ...
    """
    V = _generate_from_plan(transfers)
    this_date = strip_date_timestamp(from_date)
    first_data = {a.name: a.amount for k, a in V.accounts_by_name.items()}
    first_data["Date"] = from_date
    data: List[Dict[str, float]] = [first_data]
    while this_date < to_date:
        # Increment our current date
        # We do this at the beginning of the loop because we assume
        # That you know the "true" account values at the end of the start day
        this_date += timedelta(days=1)

        # Now get our references to lists that we need
        atstartref = V.atstart[this_date]
        dailyref = V.daily
        weeklyref = V.weekly[this_date.weekday()]
        monthlyref = V.monthly[this_date.day]
        yearlyref = V.yearly[this_date.month][this_date.day]

        this_transactions_unfiltered = \
            atstartref + dailyref + weeklyref + \
            monthlyref + yearlyref

        # Handle the n values of each transaction
        this_transactions = [t for t in this_transactions_unfiltered if t._n % t.repeat_n == 0]
        for t in this_transactions_unfiltered:
            t._n += 1

        # Iterate over transactions
        for t in this_transactions:
            if t.from_account:
                V.accounts_by_name[t.from_account].amount -= t.amount
            if t.to_account:
                V.accounts_by_name[t.to_account].amount += t.amount

        # Handle transaction APR
        # TODO: Handle the math of these for i in range statements with exponential functions instead to make it faster
        for t in transfers:
            t.amount += apr_to_daily(t.APR) * t.amount

        # Handle account APR
        for _, a in V.accounts_by_name.items():
            a.amount += apr_to_daily(t.APR) * a.amount

        # Add our data to our output
        this_data = {a.name: a.amount for _, a in V.accounts_by_name.items()}
        this_data["Date"] = this_date
        data.append(this_data)

    # Make our data "tall"
    if tall_data:
        # Get the represented in the dataset
        all_accounts = set(V.accounts_by_name.keys())

        # Make a list for each output column
        account, date, value = [], [], []
        for row in data:
            for acc in all_accounts:
                date.append(row["Date"])
                account.append(acc)
                if acc in row:
                    value.append(row[acc])
                else:
                    value.append(float("NaN"))

        return {"Account": account,
                "Date": date,
                "Value": value}

    return data
