from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

from lifechoices.classes import Account, Bridge, Plan, Once, Daily, Weekly, BiWeekly, Monthly, Yearly
from lifechoices.utils import weekOfMonth, monthdelta, strip_date_timestamp


@dataclass(frozen=False)
class _GenerateFromPlanOutput:
    once: Dict[datetime, List[Once]]
    daily: List[Daily]
    weekly: Dict[int, List[Weekly]]
    biweekly: Dict[int, Dict[int, List[BiWeekly]]]
    monthly: Dict[int, List[Monthly]]
    yearly: Dict[int, Dict[int, List[Yearly]]]
    accounts_by_name: Dict[str, Account]


def _generate_from_plan(p: Plan) -> _GenerateFromPlanOutput:
    once = defaultdict(list)
    daily = []
    weekly = defaultdict(list)
    biweekly = defaultdict(lambda: defaultdict(list))
    monthly = defaultdict(list)
    yearly = defaultdict(lambda: defaultdict(list))

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
        else:
            raise TypeError(f"Type '{type(t)}' not recognized.")
    return _GenerateFromPlanOutput(
        once, daily, weekly, biweekly, monthly, yearly, accounts_by_name
    )


# TODO: Append all dates removing the timestamp
def plot_accounts(
        starting_plan: Plan,
        bridges: List[Bridge],
        from_date: datetime,
        to_date: datetime
) -> List[Dict[str, float]]:
    """
    This is the main data plotting function in the code.
    It takes a starting plan, a sequence of bridges, and a to/from date.
    It returns a list of dictionaries (Like a pandas dataframe) containing accounts and their values, along with a
    tag called "Date" that tells you what date it was. Sorted by date ascending.
    Easiest thing to do is to take this and create a pandas Dataframe from it, and use that to plot it.
    """
    plan = starting_plan
    bridges_by_date = {b.trigger_date: b for b in bridges}
    V = _generate_from_plan(plan)
    this_date = strip_date_timestamp(from_date)
    data: List[Dict[str, float]] = [{a.name: a.amount for k, a in V.accounts_by_name.items()}]
    while this_date <= to_date:
        this_bridge = bridges_by_date[this_date] if this_date in bridges_by_date else None
        weeklyref = V.weekly[this_date.weekday()]
        biweeklyref = V.biweekly[weekOfMonth(this_date) % 2][this_date.weekday()]
        monthlyref = V.monthly[this_date.day]
        yearlyref = V.yearly[this_date.month][this_date.day]
        this_transactions = V.once[this_date] + V.daily + weeklyref + biweeklyref + monthlyref + yearlyref

        if this_date in bridges_by_date:
            print(this_bridge)

        # Iterate over transactions
        for t in this_transactions:
            if t.from_account:
                V.accounts_by_name[t.from_account].amount -= t.amount
            if t.to_account:
                V.accounts_by_name[t.to_account].amount += t.amount

        # Handle transaction APR
        # TODO: Handle the math of these for i in range statements with exponential functions instead to make it faster
        for t in V.daily:
            t.amount += t.APR/365*t.amount
        for t in weeklyref:
            for i in range(7):
                t.amount += t.APR/365*t.amount
        for t in biweeklyref:
            for i in range(14):
                t.amount += t.APR/365*t.amount
        for t in monthlyref:
            last_date = monthdelta(this_date, -1)
            nb_days = this_date - last_date
            for i in range(nb_days.days):
                t.amount += t.APR/365*t.amount
        for t in yearlyref:
            for i in range(365):
                t.amount += t.APR/365*t.amount

        # Handle account APR
        for name, a in V.accounts_by_name.items():
            V.accounts_by_name[name].amount += a.APR / 365.0 * V.accounts_by_name[name].amount

        # Handle Bridges
        if this_bridge is not None:
            print("New Bridge!")
            plan = this_bridge(plan)
            V = _generate_from_plan(plan)

        # Add our data to our output
        this_data = {a.name: a.amount for _, a in V.accounts_by_name.items()}
        this_data["Date"] = this_date
        data.append(this_data)

        # Increment our current date
        this_date += timedelta(days=1)

    return data
