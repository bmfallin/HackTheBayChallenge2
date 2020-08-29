import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app

layout = [
    html.Div(
        className="tile lg-12 md-12 sm-12 xs-12",
        children=[
            html.H2("Coming Soon!")
        ]
    )
]