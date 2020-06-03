"""Plotly Dash HTML layout override."""
import dash_html_components as html
import dash_core_components as dcc

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


def dash_layout(interval):

    layout = html.Div(
        id="wrapper",
        className="wrapper",
        children=[
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
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
                                    # Controller
                                    html.Div(
                                        className="station-switcher",
                                        children=[
                                            dcc.RadioItems(
                                                className="station-switcher__options",
                                                id="station-switcher__options",
                                                # options=stations_options,
                                                value="mythenquai",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Map
                    html.Div(
                        className="map",
                        children=[
                            html.Iframe(
                                src='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1398184.054189414!2d7.100613397498673!3d46.80768938179123!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x478c64ef6f596d61%3A0x5c56b5110fcb7b15!2sSchweiz!5e0!3m2!1sde!2sch!4v1591118065860!5m2!1sde!2sch" width="600" height="450" frameborder="0" style="border:0;'
                            )
                        ],
                    ),
                ],
            ),
        ],
    )

    return layout