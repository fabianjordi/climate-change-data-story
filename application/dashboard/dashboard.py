"""Instantiate a Dash app."""
import numpy as np
import pandas as pd
import dash
import dash_table
# import dash_html_components as html
# import dash_core_components as dcc
from .layout import html_layout, dash_layout


def create_dashboard(server):
    """Create a Plotly Dash dashboard."""

    dash_app = dash.Dash(server=server,
                         routes_pathname_prefix='/dashboard/',
                         external_stylesheets=['/static/dist/css/dashboard.css']
    )

    app_color = {
        "graph_bg": "#ffffff",
        "graph_gridline": "#EDEDED",
        "graph_line": "#007ACE",
        "transparent": "rgba(255, 255, 255, 0)",
    }

    layout = dict(
        autosize=True,
        automargin=False,
        margin=dict(l=40, r=10, b=40, t=40),
        hovermode="closest",
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        legend=dict(font=dict(size=10), orientation="h"),
    )

    # Prepare a DataFrame
    df = pd.read_csv('data/311-calls.csv', parse_dates=['created'])
    df['created'] = df['created'].dt.date
    df.drop(columns=['incident_zip'], inplace=True)
    num_complaints = df['complaint_type'].value_counts()
    to_remove = num_complaints[num_complaints <= 30].index
    df.replace(to_remove, np.nan, inplace=True)

    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout
    interval = server.config['GRAPH_INTERVAL']
    dash_app.layout = dash_layout(interval)

    return dash_app.server


def create_data_table(df):
    """Create Dash datatable from Pandas DataFrame."""
    table = dash_table.DataTable(
        id='database-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action="native",
        sort_mode='native',
        page_size=300
    )
    return table
