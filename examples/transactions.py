from lifechoices import *
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

INFLATION_RATE = .013
TODAY_DATE = datetime(2020, 10, 2)
RETIREMENT_DATE = datetime(2047, 4, 1)  # I'll be 55
DEATH_DATE = datetime(2082, 4, 1)   # I'll be 90
BOAT_PRICE = 70_000
BOAT_DATE = datetime(2040, 1, 1)
BOAT_MONTHLY = 450+.1*BOAT_PRICE*1/12
RETIREMENT_MONTHLY = 3_000

CurrentAccounts = [
    Account("Savings", 99_951.58, APR(.07-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
    Account("IRA", 6_000,  APR(.07-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
    Account("Keys401K", 56_000,  APR(.10-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
    Account("Nasco401K", 0.0,  APR(.10-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
    # Account("House", 230_000, APR(.038-INFLATION_RATE, Period.YEARLY), datetime(2017, 10, 1)),
    # Account("Mortgage", -207_025.83,  APR(.0399-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
    Account("House", 350_000, APR(.038-INFLATION_RATE, Period.YEARLY), datetime(2017, 10, 1)),
    Account("Mortgage", 230_000-207_025.83-350000,  APR(.0399-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
    Account("RSU", 80_000,  APR(.07-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
    Account("Car", 50_000, APR(-.2-INFLATION_RATE, Period.YEARLY), datetime(2020, 1, 1)),
    Account("ChildOrCharity", 0.0, APR(.07-INFLATION_RATE, Period.YEARLY), datetime(2020, 1, 1))
]

CurrentRecurringIncome = [
    Monthly("Pay", 0.0,                  to_account="Savings",        from_account=None),
    Monthly("Keys401kContrib", 1_514.06, to_account="Keys401K",       from_account=None, dayOfMonth=1),
    Monthly("IRAContribution", 6_000/12, to_account="IRA",            from_account="Savings"),
    Monthly("MortgagePayment", 2_000.32, to_account="Mortgage",       from_account=None, dayOfMonth=1),  # This comes from my checking account but I'm not going to simulate that
    # Monthly("HOA", 400,                  to_account=None,             from_account="Checking", dayOfMonth=1),
    NYearly("NewCar", 50_000,            to_account=None,             from_account="Savings", nyears=10, firstYear=2030, APR=APR(INFLATION_RATE, Period.YEARLY)),
    NYearly("NewBoat", BOAT_PRICE,       to_account=None,             from_account="Savings", nyears=10, firstYear=BOAT_DATE, APR=APR(INFLATION_RATE, Period.YEARLY)),
    Monthly("ChildSavings", 14_000/12/2, to_account="ChildOrCharity", from_account="Savings"),
    # Monthly("Paycheck", 3_500,           to_account="Checking",       from_account=None),
    Yearly("KeysStockBuy", 8_000, to_account="Savings", month=2, dayOfMonth=28),
    Yearly("KeysRSUAwards", 10_000, to_account="RSU", month=11, dayOfMonth=26),
]

CurrentPlan = Plan(
    accounts=CurrentAccounts,
    transfers=CurrentRecurringIncome
)


def boat_bridge(p: Plan) -> Plan:
    p_accounts_by_name = {a.name: a for a in p.accounts}
    transfers_by_name = {a.name: a for a in p.transfers}
    transfers_by_name["Keys401kContrib"].amount = 0
    transfers_by_name["IRAContribution"].amount = 0
    transfers_by_name["KeysStockBuy"].amount = 0
    transfers_by_name["KeysRSUAwards"].amount = 0
    transfers_by_name["MortgagePayment"].amount = 0
    p_accounts_by_name["Savings"].amount -= BOAT_PRICE
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["House"].amount + p_accounts_by_name["Car"].amount + p_accounts_by_name["Mortgage"].amount
    p_accounts_by_name["House"].amount = 0
    p_accounts_by_name["Car"].amount = 0
    p_accounts_by_name["Mortgage"].amount = 0
    p.transfers.append(Monthly("Earnings", 3000, from_account=None, to_account="Savings"))
    p.transfers.append(Monthly("Expense", 1288, from_account="Savings", to_account=None))
    return p


def retirement_bridge(p: Plan) -> Plan:
    p_accounts_by_name = {a.name: a for a in p.accounts}
    transfers_by_name = {a.name: a for a in p.transfers}
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["IRA"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["Keys401K"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["Nasco401K"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["RSU"].amount
    p_accounts_by_name["Keys401K"].amount = 0
    p_accounts_by_name["IRA"].amount = 0
    p_accounts_by_name["Nasco401K"].amount = 0
    p_accounts_by_name["RSU"].amount = 0
    transfers_by_name["Keys401kContrib"].amount = 0
    transfers_by_name["IRAContribution"].amount = 0
    transfers_by_name["KeysStockBuy"].amount = 0
    transfers_by_name["KeysRSUAwards"].amount = 0
    p.transfers.append(Monthly("Salary", 3000, APR=APR(INFLATION_RATE, period=Period.YEARLY), from_account="Savings", to_account=None))
    return p


def mortgage_payed(d: Dict[str, float]) -> bool:
    return 'Mortgage' in d and d['Mortgage'] >= 0

def mortgage_bridge(p: Plan) -> Plan:
    p_accounts_by_name = {a.name: a for a in p.accounts}
    p_transfers_by_name = {a.name: a for a in p.transfers}
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["Mortgage"].amount
    p_accounts_by_name["Mortgage"].amount = 0
    p_transfers_by_name['MortgagePayment'].to_account = "Savings"
    return p

def child_savedfor(d: Dict[str, float]) -> bool:
    ChildCost = price_at_year(
        price=233_610+9_410,
        date=d["Date"],
        yearly_inflation_rate=INFLATION_RATE,
        today=TODAY_DATE
    )
    return "ChildOrCharity" in d and d["ChildOrCharity"] >= ChildCost


def child_savedfor_bridge(p: Plan) -> Plan:
    p_transfers_by_name = {a.name: a for a in p.transfers}
    p_transfers_by_name['ChildSavings'].to_account = "Savings"
    return p

Bridges = [
    CallbackBridge("MortgagePayed", mortgage_bridge, mortgage_payed),
    CallbackBridge("ChildPayed", child_savedfor_bridge, child_savedfor),
    DateBridge("Boat", boat_bridge, BOAT_DATE),
    DateBridge("Retirement", retirement_bridge, RETIREMENT_DATE),
]

# And now we plot!
# Just to be fancy, we will use plotly dash
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=datetime(1995, 8, 5),
        max_date_allowed=datetime(2100, 8, 5),
        initial_visible_month=datetime.now(),
        start_date=strip_date_timestamp(datetime.now()),
        end_date=strip_date_timestamp(datetime.now()+timedelta(days=50*365))
    ),
    dcc.Graph(id='my-plot')
])

@app.callback(
    dash.dependencies.Output('my-plot', 'figure'),
    [dash.dependencies.Input('date-picker', 'start_date'),
     dash.dependencies.Input('date-picker', 'end_date')])
def plot(start_date: str, end_date: str):
    start_date = datetime.strptime(start_date.split('T')[0], '%Y-%m-%d')
    end_date = datetime.strptime(end_date.split('T')[0], '%Y-%m-%d')
    data = plot_accounts(
        starting_plan=Starting_Plan,
        bridges=Bridges,
        from_date=start_date,
        to_date=end_date,
        tall_data=True
    )
    df = pd.DataFrame(data)
    fig = px.line(df, x="Date", color="Account", y="Value")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
