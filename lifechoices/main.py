from typing import Dict, List, Union, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

from lifechoices.classes import Account, Bridge, DateBridge, CallbackBridge, Plan, Once, Daily, Weekly, BiWeekly, Monthly, Yearly, NYearly
from lifechoices.utils import weekOfMonth, monthdelta, strip_date_timestamp, effective_interest_rate_per_t_periods

import pandas as pd


@dataclass(frozen=False)
class _GenerateFromPlanOutput:
    once: Dict[datetime, List[Once]]
    daily: List[Daily]
    weekly: Dict[int, List[Weekly]]
    biweekly: Dict[int, Dict[int, List[BiWeekly]]]
    monthly: Dict[int, List[Monthly]]
    yearly: Dict[int, Dict[int, List[Yearly]]]
    nyearly: Dict[int, Dict[int, Dict[int, List[NYearly]]]]
    accounts_by_name: Dict[str, Account]


def _generate_from_plan(p: Plan) -> _GenerateFromPlanOutput:
    once = defaultdict(list)
    daily = []
    weekly = defaultdict(list)
    biweekly = defaultdict(lambda: defaultdict(list))
    monthly = defaultdict(list)
    yearly = defaultdict(lambda: defaultdict(list))
    nyearly = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    accounts_by_name = {a.name: a for a in p.accounts}
    for t in p.transfers:
        t.check()
        if isinstance(t, Daily):
            daily.append(t)
        if isinstance(t, Once):
            once[t.date].append(t)
        elif isinstance(t, Weekly):
            weekly[t.dayOfWeek].append(t)
        elif isinstance(t, BiWeekly):
            biweekly[t.weekOffset][t.dayOfWeek].append(t)
        elif isinstance(t, Monthly):
            monthly[t.dayOfMonth].append(t)
        elif isinstance(t, Yearly):
            yearly[t.month][t.dayOfMonth].append(t)
        elif isinstance(t, NYearly):
            for y in range(1997, 30_000, t.nyears):   # TODO: This is such a hack
                nyearly[y][t.month][t.dayOfMonth].append(t)
        else:
            raise TypeError(f"Type '{type(t)}' not recognized.")
    return _GenerateFromPlanOutput(
        once, daily, weekly, biweekly, monthly, yearly, nyearly, accounts_by_name
    )


# TODO: Append all dates removing the timestamp
def plot_accounts(
        starting_plan: Plan,
        bridges: List[Bridge],
        from_date: datetime,
        to_date: datetime,
        tall_data: bool = True,
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
    plan = starting_plan
    bridges_by_date = {b.trigger_date: b for b in bridges if isinstance(b, DateBridge)}
    V = _generate_from_plan(plan)
    this_date = strip_date_timestamp(from_date)
    first_data = {a.name: a.amount for k, a in V.accounts_by_name.items()}
    first_data["Date"] = from_date
    data: List[Dict[str, float]] = [first_data]
    while this_date < to_date:
        # Increment our current date
        # We do this at the beginning of the loop because we assume
        # That you know the "true" account values at the end of the start day
        this_date += timedelta(days=1)

        # Get our references to our transfer lists
        this_bridge = bridges_by_date[this_date] if this_date in bridges_by_date else None
        weeklyref = V.weekly[this_date.weekday()]
        biweeklyref = V.biweekly[weekOfMonth(this_date) % 2][this_date.weekday()]
        monthlyref = V.monthly[this_date.day]
        yearlyref = V.yearly[this_date.month][this_date.day]
        nyearlyref = V.nyearly[this_date.year][this_date.month][this_date.day]
        this_transactions = V.once[this_date] + V.daily + weeklyref + biweeklyref + monthlyref + yearlyref + nyearlyref

        # Iterate over transactions
        for t in this_transactions:
            if t.from_account:
                V.accounts_by_name[t.from_account].amount -= t.amount
            if t.to_account:
                V.accounts_by_name[t.to_account].amount += t.amount

        # Handle transaction APR
        # TODO: Handle the math of these for i in range statements with exponential functions instead to make it faster
        for t in V.daily:
            t.amount += effective_interest_rate_per_t_periods(t.APR.to_daily().value, 365, 1 / 365) * t.amount
        for t in weeklyref:
            t.amount += effective_interest_rate_per_t_periods(t.APR.to_daily().value, 365, 7 / 365) * t.amount
        for t in biweeklyref:
            t.amount += effective_interest_rate_per_t_periods(t.APR.to_daily().value, 365, 14 / 365) * t.amount
        for t in monthlyref:
            last_date = monthdelta(this_date, -1)
            nb_days = this_date - last_date
            t.amount += effective_interest_rate_per_t_periods(t.APR.to_daily().value, 365, nb_days.days / 365) * t.amount
        for t in yearlyref:
            t.amount += effective_interest_rate_per_t_periods(t.APR.to_daily().value, 365, 1.0) * t.amount
        for t in nyearlyref:
            t.amount += effective_interest_rate_per_t_periods(t.APR.to_daily().value, t.nyears*365, 1.0) * t.amount

        # Handle account APR
        for _, a in V.accounts_by_name.items():
            a.amount += effective_interest_rate_per_t_periods(a.APR.to_daily().value, 365, 1 / 365) * a.amount

        # Add our data to our output
        this_data = {a.name: a.amount for _, a in V.accounts_by_name.items()}
        this_data["Date"] = this_date
        data.append(this_data)

        # Handle Bridges
        bridge_activated = False
        if this_bridge is not None:
            plan = this_bridge(plan)
            V = _generate_from_plan(plan)
            if bridge_activated:
                raise RuntimeError("More than one bridge activated on the same date.")
            bridge_activated = True
            del bridges_by_date[this_date]
            print(f"Bridge {this_bridge.name} Activated on {this_date}")

        # Handle Callback Bridges
        for i, b in enumerate(bridges):
            if isinstance(b, CallbackBridge) and b.trigger_function(this_data):
                plan = b(plan)
                V = _generate_from_plan(plan)
                if bridge_activated:
                    raise RuntimeError("More than one bridge activated on the same date.")
                bridge_activated = True
                del bridges[i]
                print(f"Bridge {b.name} Activated on {this_date}")
                break

    # Make our data "tall"
    if tall_data:
        return wide_to_tall(data)

    return data


def wide_to_tall(data: Union[List[Dict[str, Any]], pd.DataFrame]) -> Union[Dict[str, List[Any]], pd.DataFrame]:
    """
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
    # Handle dataframes
    if isinstance(data, pd.DataFrame):
        create_dataframe = True
        data = [dict(row) for _, row in data.iterrows()]
    else:
        create_dataframe = False
    # Get the accounts represented in the dataset
    account_names = {key for row in data for key in row if key != "Date"}

    # Make a list for each output column
    account, date, value = [], [], []
    for row in data:
        for acc in account_names:
            date.append(row["Date"])
            account.append(acc)
            if acc in row:
                value.append(row[acc])
            else:
                value.append(float("NaN"))
    out = {"Account": account,
           "Date": date,
           "Value": value}
    if create_dataframe:
        return pd.DataFrame(out)
    return out
