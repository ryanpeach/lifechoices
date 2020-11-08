from datetime import datetime, timedelta
from typing import List

from django_plotly_dash import DjangoDash

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd

from elements.models import Account, Transfer
from lifechoices import calculate_accounts
from lifechoices.utils import strip_date_timestamp

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash(__name__, external_stylesheets=external_stylesheets)
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
    data = calculate_accounts(
        accounts=accounts,
        transfers=transfers,
        from_date=start_date,
        to_date=end_date,
        tall_data=True
    )
    df = pd.DataFrame(data)
    fig = px.line(df, x="Date", color="Account", y="Value")
    return fig

