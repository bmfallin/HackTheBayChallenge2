import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from enums import Properties
from datetime import datetime as dt
import data
import random
import json
import time

from app import app
import pages.cmc_vs_cbp_page as cmc_vs_cbp_page
import pages.huc12_timeline_page as huc12_timeline_page
import pages.station_timeline_page as station_timeline_page
import pages.recommendations_page as recommendations_page


# Set the app's layout
app.layout = html.Div(
    id="root",
    className="container",
    children=[
        html.Div(
            id="navigation",
            className="container lg-12 md-12 sm-12 xs-12",
            children=[
                html.H4('Cheapeake Bay Watershed Analysis', id="nav-title", className="nav-title lg-4 md-12 sm-12 xs-12"),
                html.Button('CMC vs CBP', id='nav-button-page-1', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0),
                html.Button('Station Timeline', id='nav-button-page-2', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0),
                html.Button('HUC12 Timeline', id='nav-button-page-3', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0),
                html.Button('Recommendations', id='nav-button-page-4', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0)
            ]
        ),
        html.Div(
            id="page-content",
            className="container lg-12 md-12 sm-12 xs-12"
        )
    ]
)

@app.callback(Output("page-content", "children"),
[
    Input('nav-button-page-1', 'n_clicks'),
    Input('nav-button-page-2', 'n_clicks'),
    Input('nav-button-page-3', 'n_clicks'),
    Input('nav-button-page-4', 'n_clicks')
])
def navigate(org_clicks, station_clicks, huc_clicks, rec_clicks):

    layout = html.H4("Page Not Found")

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'nav-button-page-1' in changed_id:
        layout = cmc_vs_cbp_page.layout

    elif 'nav-button-page-2' in changed_id:
        layout = station_timeline_page.layout

    elif 'nav-button-page-3' in changed_id:
        layout = huc12_timeline_page.layout

    elif 'nav-button-page-4' in changed_id:
        layout = recommendations_page.layout

    return layout


if __name__ == '__main__':

    # Run the Dash app
    app.run_server(debug=False)