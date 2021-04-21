from lifechoices import *
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

INFLATION_RATE = .013
RAISE_RATE = .03
SHORT_TERM_GROWTH_RATE = .07
LONG_TERM_GROWTH_RATE = .13
TODAY_DATE = datetime(2020, 10, 2)
PRE_RETIREMENT_DATE = datetime(1992+40, 4, 1)
RETIREMENT_DATE = datetime(1992+59, 4, 1)
DEATH_DATE = datetime(1992+90, 4, 1)   # I'll be 90
BOAT_PRICE = 70000

# TODO: Add Taxes
# TODO: Add low and high bounds
# TODO:


def main():
    CurrentAccounts = [
        Account("Savings", 99_951.58, APR(SHORT_TERM_GROWTH_RATE-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
        Account("IRA", 6_000,  APR(SHORT_TERM_GROWTH_RATE-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
        Account("Keys401K", 56_000,  APR(LONG_TERM_GROWTH_RATE-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
        Account("Nasco401K", 0.0,  APR(LONG_TERM_GROWTH_RATE-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
        Account("House", 300_000, APR(.038-INFLATION_RATE, Period.YEARLY), datetime(2017, 10, 1)),
        # TODO: Is this + inflation or - inflation
        Account("Mortgage", 230_000-207_025.83-350000,  APR(.0399-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
        Account("RSU", 80_000,  APR(SHORT_TERM_GROWTH_RATE-INFLATION_RATE, Period.YEARLY), TODAY_DATE),
        Account("Car", 50_000, APR(-.2-INFLATION_RATE, Period.YEARLY), datetime(2020, 1, 1)),
    ]

    CurrentRecurringIncome = [
        Monthly("Pay", 2_728.34*2,             to_account="Savings",        from_account=None, APR=APR(INFLATION_RATE+RAISE_RATE, Period.YEARLY)),
        Monthly("CostOfLiving", 2_728.34*2-2000.32,    to_account=None,             from_account="Savings", APR=APR(INFLATION_RATE, Period.YEARLY)),
        Monthly("Keys401kContrib", 757.03,   to_account="Keys401K",       from_account=None, dayOfMonth=1, APR=APR(INFLATION_RATE, Period.YEARLY)),
        Monthly("IRAContribution", 6_000/12, to_account="IRA",            from_account="Savings"),
        Monthly("MortgagePayment", 2_000.32, to_account="Mortgage",       from_account="Savings", dayOfMonth=1),  # This comes from my checking account but I'm not going to simulate that
        # Monthly("HOA", 400,                  to_account=None,             from_account="Checking", dayOfMonth=1),
        NYearly("NewCar", 50_000,            to_account=None,             from_account="Savings", nyears=10, firstYear=2030, APR=APR(INFLATION_RATE, Period.YEARLY)),
        NYearly("NewBoat", BOAT_PRICE,       to_account=None,             from_account="Savings", nyears=10, firstYear=PRE_RETIREMENT_DATE, APR=APR(INFLATION_RATE, Period.YEARLY)),
        Yearly("KeysStockBuy", 6_480/.85,    to_account="Savings",        from_account=None, month=2, dayOfMonth=28),
        Yearly("KeysRSUAwards", 10_000,      to_account="RSU",            from_account=None, month=11, dayOfMonth=26),
    ]

    CurrentPlan = Plan(
        accounts=CurrentAccounts,
        transfers=CurrentRecurringIncome
    )
    return CurrentPlan


def pre_retirement_bridge(p: Plan) -> Plan:
    # Accounts
    p_accounts_by_name = {a.name: a for a in p.accounts}
    p_accounts_by_name["Savings"].amount -= BOAT_PRICE
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["House"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["Car"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["Mortgage"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["RSU"].amount
    # p_accounts_by_name["IRA"]
    # p_accounts_by_name["Keys401K"]
    # p_accounts_by_name["Nasco401K"]
    p_accounts_by_name["House"].amount = 0
    p_accounts_by_name["Mortgage"].amount = 0
    p_accounts_by_name["RSU"].amount = 0
    p_accounts_by_name["Car"].amount = 0

    # Transfers
    transfers_by_name = {a.name: a for a in p.transfers}
    transfers_by_name["Pay"].amount = 0
    transfers_by_name["Keys401kContrib"].amount = 0
    transfers_by_name["IRAContribution"].amount = 0
    transfers_by_name["MortgagePayment"].amount = 0
    # transfers_by_name["NewCar"].amount
    # transfers_by_name["NewBoat"]
    transfers_by_name["KeysStockBuy"].amount = 0
    transfers_by_name["KeysRSUAwards"].amount = 0

    p.transfers.append(Monthly("Earnings", 3000, from_account=None, to_account="Savings"))
    p.transfers.append(Monthly("Expense", 1288, from_account="Savings", to_account=None))
    return p


def retirement_bridge(p: Plan) -> Plan:
    # Accounts
    p_accounts_by_name = {a.name: a for a in p.accounts}
    p_accounts_by_name["Savings"].amount -= BOAT_PRICE
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["Nasco401K"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["Keys401K"].amount
    p_accounts_by_name["Savings"].amount += p_accounts_by_name["IRA"].amount
    p_accounts_by_name["IRA"].amount = 0
    p_accounts_by_name["Keys401K"].amount = 0
    p_accounts_by_name["Nasco401K"].amount = 0
    # p_accounts_by_name["House"].amount = 0
    # p_accounts_by_name["Mortgage"].amount = 0
    # p_accounts_by_name["RSU"].amount = 0
    # p_accounts_by_name["Car"].amount = 0

    # Transfers
    transfers_by_name = {a.name: a for a in p.transfers}
    # transfers_by_name["Keys401kContrib"].amount = 0
    # transfers_by_name["IRAContribution"].amount = 0
    # transfers_by_name["MortgagePayment"].amount = 0
    # transfers_by_name["NewCar"].amount
    # transfers_by_name["NewBoat"]
    # transfers_by_name["KeysStockBuy"].amount = 0
    # transfers_by_name["KeysRSUAwards"].amount = 0

    p.transfers.append(Monthly("Earnings", 3000, from_account=None, to_account="Savings"))
    p.transfers.append(Monthly("Expense", 1288, from_account="Savings", to_account=None))
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


Bridges = [
    CallbackBridge("MortgagePayed", mortgage_bridge, mortgage_payed),
    DateBridge("Pre Retirement", pre_retirement_bridge, PRE_RETIREMENT_DATE),
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
        start_date=strip_date_timestamp(TODAY_DATE),
        end_date=strip_date_timestamp(DEATH_DATE)
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
        starting_plan=main(),
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
