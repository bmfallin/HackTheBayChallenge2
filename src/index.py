import json
import random
import time
from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from dash.dependencies import Input, Output, State

import data
import pages.benthic_page as benthic_page
import pages.home_page as home_page
import pages.huc_page as huc_page
import pages.org_page as org_page
import pages.station_page as station_page
from app import app
from enums import Properties

# Set the app's layout
app.layout = html.Div(
    id="root",
    className="container",
    children=[
        html.Div(
            id="fixed-navigation",
            className="navigation container lg-12 md-12 sm-12 xs-12",
            children=[
                html.H4('Cheapeake Bay Watershed Analysis', id="nav-title", className="nav-title lg-4 md-12 sm-12 xs-12"),
                html.Button('Organization Comparison', id='org-page-button', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0),
                html.Button('Station Gap Analysis', id='station-page-button', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0),
                html.Button('HUC12 Gap Analysis', id='huc-page-button', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0),
                html.Button('Benthic Analysis', id='benthic-page-button', className="nav-button lg-2 md-6 sm-6 xs-12", n_clicks=0)
            ]
        ),

        # This div is hidden behind the top navigation to ensure the correct spacing is used
        html.Div(
            id="hidden-navigation",
            className="navigation container lg-12 md-12 sm-12 xs-12",
            children=[
                html.H4('Cheapeake Bay Watershed Analysis', className="nav-title lg-4 md-12 sm-12 xs-12"),
                html.Button('Organization Comparison', className="nav-button lg-2 md-6 sm-6 xs-12"),
                html.Button('Station Gap Analysis', className="nav-button lg-2 md-6 sm-6 xs-12"),
                html.Button('HUC12 Gap Analysis', className="nav-button lg-2 md-6 sm-6 xs-12"),
                html.Button('Benthic Analysis', className="nav-button lg-2 md-6 sm-6 xs-12")
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
    Input('org-page-button', 'n_clicks'),
    Input('station-page-button', 'n_clicks'),
    Input('huc-page-button', 'n_clicks'),
    Input('benthic-page-button', 'n_clicks'),
    Input('nav-title', 'n_clicks')
])
def navigate(org_clicks, station_clicks, huc_clicks, rec_clicks, home_clicks):

    layout = html.H4("Page Not Found")

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'org-page-button' in changed_id:
        layout = org_page.layout

    elif 'station-page-button' in changed_id:
        layout = station_page.layout

    elif 'huc-page-button' in changed_id:
        layout = huc_page.layout

    elif 'benthic-page-button' in changed_id:
        layout = benthic_page.layout

    elif 'nav-title' in changed_id:
        layout = home_page.layout

    return layout


if __name__ == '__main__':

    # Run the Dash app
    app.run_server(debug=False)
