from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from math import ceil

from money.classes import Account, Transfer, Bridge, Plan, Once, Daily, Weekly, BiWeekly, Monthly, Yearly


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


def plot_accounts(
        starting_plan: Plan,
        bridges: List[Bridge],
        from_date: datetime,
        to_date: datetime
):
    plan = starting_plan
    bridges_by_date = {b.trigger_date: b for b in bridges}

    def generate_from_plan(p: Plan):
        global accounts_by_name, this_accounts_by_name, once, daily, weekly, biweekly, monthly, yearly

        once: Dict[datetime, List[Once]] = defaultdict(list)
        daily: List[Daily] = []
        weekly: Dict[int, List[Weekly]] = defaultdict(list)
        biweekly: Dict[int, Dict[int, List[BiWeekly]]] = defaultdict(lambda: defaultdict(list))
        monthly: Dict[int, List[Monthly]] = defaultdict(list)
        yearly: Dict[int, Dict[int, List[Yearly]]] = defaultdict(lambda: defaultdict(list))

        accounts_by_name = {a.name: a for a in p.accounts}
        this_accounts_by_name = accounts_by_name.copy()
        for t in p.transfers:
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

    generate_from_plan(plan)
    this_date = from_date
    data: List[Dict[str, float]] = [{a.name: a.amount for a in this_accounts_by_name}]
    while this_date <= to_date:
        this_bridge = bridges_by_date[this_date] if this_date in bridges_by_date else None
        weeklyref = weekly[this_date.weekday()]
        biweeklyref = biweekly[weekOfMonth(this_date) % 2][this_date.weekday()]
        monthlyref = monthly[this_date.day]
        yearlyref = yearly[this_date.month][this_date.day]
        this_transactions = once[this_date] + daily + weeklyref + biweeklyref + monthlyref + yearlyref

        # Iterate over transactions
        new_account_values = {a.name: a.value for a in this_accounts_by_name}
        for t in this_transactions:
            if t.from_account:
                new_account_values[t.from_account] -= t.amount
            if t.to_account:
                new_account_values[t.to_account] += t.amount

        # Handle transaction APR
        # TODO: Handle the math of these for i in range statements with exponential functions instead to make it faster
        for t in daily:
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
            for i in range(nb_days):
                t.amount += t.APR/365*t.amount
        for t in yearlyref:
            for i in range(365):
                t.amount += t.APR/365*t.amount

        # Handle account APR
        for name, a in accounts_by_name.items():
            new_account_values[name] += a.APR/365.0*new_account_values[name]

        # Create the new accounts
        this_accounts_by_name = {
            name: Account(name, dollars, accounts_by_name[name].APR, this_date)
            for name, dollars in new_account_values.items()
        }

        # Handle Bridges
        if this_bridge is not None:
            plan = this_bridge(plan)
            generate_from_plan(plan)

        # Increment our current date
        data.append({a.name: a.amount for a in this_accounts_by_name})
        this_date += timedelta(days=1)

    return data
