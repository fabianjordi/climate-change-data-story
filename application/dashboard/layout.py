"""Plotly Dash HTML layout override."""
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px

html_layout = """
<!DOCTYPE html>
<html lang="de-CH">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer class="footer">
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


app_color = {
    "graph_bg": "#ffffff",
    "graph_gridline": "#EDEDED",
    "graph_line": "#007ACE",
    "transparent": "rgba(255, 255, 255, 0)",
}

basic_layout = dict(
    autosize=True,
    automargin=False,
    margin=dict(l=0, r=0, b=0, t=0),
    hovermode="closest",
    plot_bgcolor=app_color["graph_bg"],
    paper_bgcolor=app_color["graph_bg"],
    legend=dict(font=dict(size=10), orientation="h"),
)


def plot_switzerland_map():
    return html.Div([
        dcc.Graph(
            id='location-map-plot',
            config={'displayModeBar': True},
            figure={
                'data': [
                    # This plots a larger circle marker that's dark red - make's things look more like a volcano
                    go.Scattermapbox(
                        lat=(45.83203,47.69732),
                        lon=(6.07544, 9.83723),
                        text='jkljl',
                        hoverinfo='text',
                        mode='markers',
                        marker=dict(
                            size=17,
                            color='rgb(255, 0, 0)',
                        ),
                    ),
                    # This plots a smaller circle marker that's light red
                    go.Scattermapbox(
                        lat=(45.83203,47.69732),
                        lon=(6.07544, 9.83723),
                        text='jkljl',
                        hoverinfo='text',
                        mode='markers',
                        marker=dict(
                            size=8,
                            color='rgb(242, 177, 172)',
                        ),
                    ),
                ],
                'layout': go.Layout(
                    showlegend=False,
                    autosize=True,
                    margin=dict(l=0, r=0, b=0, t=0),
                    hovermode="closest",
                    plot_bgcolor="#F9F9F9",
                    paper_bgcolor="#F9F9F9",
                    legend=dict(font=dict(size=10), orientation="h"),

                    mapbox=dict(
                        accesstoken='pk.eyJ1IjoiZmFiaWFuam9yZGkiLCJhIjoiY2tiMTZwdDc1MGV2bTM1bWV0cGw3bWI3ZSJ9.juId8ozd5h6tKcK4ab9H_Q',
                        style="light",
                        center=dict(
                            lat=46.800663464,
                            lon=8.222665776,
                        ),
                        zoom=6
                    ),
                ),
            },
        )
    ])


def dash_layout(interval):

    layout = html.Div(
        id="wrapper",
        className="wrapper",
        children=[
            # empty Div to trigger javascript file for graph resizing
            html.Div(id='output-clientside'),
            dcc.Interval(
                id="update-interval",
                interval=int(interval),
                n_intervals=0,
            ),
            # Main
            html.Div(
                className="main",
                children=[
                    # Facts
                    html.Div(
                        id="facts",
                        className="facts",
                        children=[
                            # Header
                            html.Div(
                                id="header",
                                className="header",
                                children=[
                                    html.H1(
                                        className="header__title",
                                        id="header__title",
                                        children=[
                                            html.Span("Klimadaten in "),
                                            html.Span(
                                                className="header__subtitle",
                                                id="header__subtitle",
                                            ),
                                        ]
                                    ),
                                    dcc.Dropdown(
                                        id='rows',
                                        options=[{
                                            'label': i,
                                            'value': i
                                        } for i in [1, 2, 3, 4]],
                                        placeholder='Select number of rows...',
                                        clearable=False,
                                        value=2
                                    ),
                                    dcc.Dropdown(
                                        id='my-dropdown',
                                        options=[
                                            {'label': 'Coke', 'value': 'COKE'},
                                            {'label': 'Tesla', 'value': 'TSLA'},
                                            {'label': 'Apple', 'value': 'AAPL'}
                                        ],
                                        value='COKE'
                                    ),
                                ],
                            ),
                            dcc.Graph(id='graph'),
                        ],
                    ),
                    html.Div(
                        className='map',
                        children=[
                            plot_switzerland_map(),
                        ]
                    ),
                ],
            ),
        ],
    )

    return layout
