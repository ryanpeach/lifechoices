from money import *
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

INFLATION_RATE = .05
Retirement_Date = datetime(2045, 1, 1)

Accounts_Young = [Account("Savings", 0.0, 0.1-INFLATION_RATE, datetime(2020, 10, 2))]

Transfers_Young = [Monthly("Salary", 1000, "Savings")]

Accounts_Old = [Account("Savings", 0.0, 0.07-INFLATION_RATE, Retirement_Date)]

Transfers_Old = [Monthly("Salary", -1000, "Savings")]

def our_bridge(p: Plan) -> Plan:
    Accounts_Old[0].dollars = p.accounts[0].dollars
    return Plan(
        accounts=Accounts_Old,
        transfers=Transfers_Old
    )

Bridges = [Bridge(Retirement_Date, our_bridge)]

Starting_Plan = Plan(
    accounts=Accounts_Young,
    transfers=Transfers_Young
)

data = plot_accounts(starting_plan=Starting_Plan, bridges=Bridges, from_date=datetime(2020,10,2), to_date=datetime(2080, 1, 1))
df = pd.DataFrame(data)
df = df.set_index("Date")
df.plot()
plt.show()