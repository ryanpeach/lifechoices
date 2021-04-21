from lifechoices import *
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

INFLATION_RATE = .013
SHORT_TERM_GROWTH_RATE = .07
LONG_TERM_GROWTH_RATE = .13
TODAY_DATE = datetime.now()
END_DATE = datetime(2040, 1, 1)
BOAT_PRICE = 70000

ZILLOW_ESTIMATE = 276_838
PRINCIPAL_BALANCE = 206_399.65
OLD_HOUSE_RATE = 0.0399
NEW_HOUSE_AMOUNT = 350_000
NEW_HOUSE_RATE = 0.0399


def main(new_house_out_of_pocket, new_house_interest_rate):
    CurrentAccounts = [
        Account("Mortgage1", -PRINCIPAL_BALANCE, APR(OLD_HOUSE_RATE, Period.YEARLY), TODAY_DATE),
        Account("HOA1", 0, APR(SHORT_TERM_GROWTH_RATE, Period.YEARLY), TODAY_DATE),
        Account("Mortgage2", -new_house_out_of_pocket, APR(new_house_interest_rate, Period.YEARLY), TODAY_DATE),
        Account("HOA2", 0, APR(SHORT_TERM_GROWTH_RATE, Period.YEARLY), TODAY_DATE)
    ]

    CurrentRecurringIncome = [
        Monthly("MortgagePayment1", 2_000.32, to_account="Mortgage1", from_account=None, dayOfMonth=1),
        Monthly("HOAPayment1", 400, to_account=None, from_account="HOA1", dayOfMonth=1),
        Monthly("MortgagePayment2", 2_350.32, to_account="Mortgage2", from_account=None, dayOfMonth=1),
        Monthly("HOAPayment2", 50, to_account=None, from_account="HOA2", dayOfMonth=1),
    ]

    CurrentPlan = Plan(
        accounts=CurrentAccounts,
        transfers=CurrentRecurringIncome
    )
    return CurrentPlan


def mortgage_payed1(d: Dict[str, float]) -> bool:
    return 'Mortgage1' in d and d['Mortgage1'] >= 0


def mortgage_bridge1(p: Plan) -> Plan:
    p_accounts_by_name = {a.name: a for a in p.accounts}
    p_transfers_by_name = {a.name: a for a in p.transfers}
    # p_accounts_by_name['Mortgage1'].amount = 0
    p_transfers_by_name['MortgagePayment1'].amount = 0
    # Let's just assume we stop paying and stop losing potential money from HOA fees at this point
    p_transfers_by_name["HOAPayment1"].amount = 0
    p_accounts_by_name['HOA1'].APR = APR(0)
    return p


def mortgage_payed2(d: Dict[str, float]) -> bool:
    return 'Mortgage2' in d and d['Mortgage2'] >= 0


def mortgage_bridge2(p: Plan) -> Plan:
    p_accounts_by_name = {a.name: a for a in p.accounts}
    p_transfers_by_name = {a.name: a for a in p.transfers}
    # p_accounts_by_name['Mortgage2'].amount = 0
    p_transfers_by_name['MortgagePayment2'].amount = 0
    # Let's just assume we stop paying and stop losing potential money from HOA fees at this point
    p_transfers_by_name["HOAPayment2"].amount = 0
    p_accounts_by_name['HOA2'].APR = APR(0)
    return p


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
        end_date=strip_date_timestamp(END_DATE)
    ),
    dcc.Graph(id='my-plot'),
    dcc.Slider(
            id='house-price',
            min=200_000,
            max=400_000,
            step=10_000,
            value=350_000,
        ),
    html.Div(id='house-price-output-container'),
    dcc.Slider(
            id='interest-rate',
            min=0,
            max=0.04,
            step=0.0001,
            value=0.0299,
        ),
    html.Div(id='interest-rate-output-container'),
    html.Button('Submit', id='submit-val', n_clicks=0)
])

@app.callback(
    dash.dependencies.Output('interest-rate-output-container', 'children'),
    [dash.dependencies.Input('interest-rate', 'value')])
def update_interest_rate(value):
    return 'Interest Rate "{}"'.format(value)

@app.callback(
    dash.dependencies.Output('house-price-output-container', 'children'),
    [dash.dependencies.Input('house-price', 'value')])
def update_house_price(value):
    return 'House Price "{}"'.format(value)

@app.callback(
    dash.dependencies.Output('my-plot', 'figure'),
    [dash.dependencies.Input('date-picker', 'start_date'),
     dash.dependencies.Input('date-picker', 'end_date'),
     dash.dependencies.Input('submit-val', 'n_clicks')],
    [dash.dependencies.State('house-price', 'value'),
     dash.dependencies.State('interest-rate', 'value')]
)
def plot(start_date: str, end_date: str, n_clicks: int, house_price: float, interest_rate: float):
    NEW_HOUSE_OUT_OF_POCKET = house_price - (ZILLOW_ESTIMATE - PRINCIPAL_BALANCE)
    Bridges = [
        CallbackBridge("MortgagePayed1", mortgage_bridge1, mortgage_payed1),
        CallbackBridge("MortgagePayed2", mortgage_bridge2, mortgage_payed2)
    ]

    start_date = datetime.strptime(start_date.split('T')[0], '%Y-%m-%d')
    end_date = datetime.strptime(end_date.split('T')[0], '%Y-%m-%d')
    data = plot_accounts(
        starting_plan=main(new_house_out_of_pocket=NEW_HOUSE_OUT_OF_POCKET, new_house_interest_rate=interest_rate),
        bridges=Bridges,
        from_date=start_date,
        to_date=end_date,
        tall_data=False
    )
    df = pd.DataFrame(data)
    df["Total1"] = PRINCIPAL_BALANCE + df["Mortgage1"] - df["HOA1"]
    del df["Mortgage1"], df["HOA1"]
    df["Total2"] = NEW_HOUSE_OUT_OF_POCKET + df["Mortgage2"] - df["HOA2"]
    del df["Mortgage2"], df["HOA2"]
    df = wide_to_tall(df)
    fig = px.line(df, x="Date", color="Account", y="Value")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
