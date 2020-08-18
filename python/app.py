import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from enums import Properties
from datetime import datetime as dt
import data
import random
import json


def get_prop_name(value: Properties) -> str:
    if value == Properties.E_COLI:
        return "E.Coli"

    if value == Properties.PH:
        return "pH"

    return value.name.replace("_", " ").title()


def __add_features_to_gaps(df):
    df["Task"] = df.apply(lambda row: row.HUC12, axis = 1)
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    df["Elapsed"] = df.apply(lambda row: row.Finish - row.Start, axis = 1)
    return df



if __name__ == '__main__':

    # Define our default parameters. Should be eventually updated/set via callback
    start = '01-01-2016'
    end = '01-01-2020'
    gap_threshold = 30

    # Load the main Water_FINAL.csv
    df = data.load_water_final()

    # Load the HUC12 region data
    gdf = data.load_huc12()

    # Find gaps per property and HUC12 region
    gaps_df = data.find_time_gaps(df, gdf["HUC12"], start, end, gap_threshold)
    gaps_df = data.parallel_dataframe(gaps_df, __add_features_to_gaps)

    # Simplify the geometry of the polygons for better web performance (polygons are extremely detailed)
    gdf["geometry"] = gdf.geometry.simplify(tolerance=0.008333,preserve_topology=True)

    # Convert the HUC12 region data into GeoJSON for the map
    regions = json.loads(gdf.to_json())
    for region in regions["features"]:
        region["id"] = "0" + str(region["properties"]["HUC12"])

    # Group the dataframe by HUC12 and PropertyName, then sum the elapsed date gaps
    map_df = gaps_df.groupby(['HUC12', 'PropertyName'])['Elapsed'].sum().reset_index()

    # Convert the elapsed timedeltas into day counts (choropleth map needs non timedelta values)
    map_df["Elapsed"] = map_df["Elapsed"].dt.days

    # Create the choropleth map for the web app
    map_fig = px.choropleth_mapbox(map_df, geojson=regions, locations="HUC12",
                            color="Elapsed",
                            color_continuous_scale="Viridis",
                            mapbox_style="light",
                            zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                            opacity=0.5
                          )

    # Add a mapbox token to the choropleth map
    map_fig.update_layout(mapbox_accesstoken="pk.eyJ1IjoiYmZhbGxpbiIsImEiOiJjanQ2ZjU3dWUwZ2dyM3lvNjA1ZGpuYmUyIn0.Ylu23fEbZoSmCuP-ekyIAA")

    # Create a 3D scatter plot for the webapp
    scatter_fig = px.scatter_3d(gaps_df, x='HUC12', y='Elapsed', z='PropertyName',
              color='PropertyName')


    # Create a list of properties for our dropdown
    property_options = []
    for prop in Properties:
        if prop == Properties.UNKNOWN:
            continue

        property_options.append({
            "label": get_prop_name(prop),
            "value": prop.value
        })

    # Define the stylesheet
    external_stylesheets = [".\\static\\stylesheet.css"]

    # Define the dash app
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    # Set the app's layout
    app.layout = html.Div(
        
        id="root",
        children=[
            html.H4(children="Gaps in Chesapeake Bay"),
            html.Div(
                children=[
                    dcc.Dropdown(
                        id="selected-properties",
                        multi=True,
                        value=[],
                        options=property_options,
                    ),
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=dt(1995, 8, 5),
                        max_date_allowed=dt(2017, 9, 19),
                        initial_visible_month=dt(2017, 8, 5),
                        start_date=dt(2016, 1, 1).date(),
                        end_date=dt(2019, 12, 31).date()
                    ),
                    dcc.Graph(
                        id='map-chart',
                        figure=map_fig
                    ),
                    dcc.Graph(
                        id='scatter-chart',
                        figure=scatter_fig
                    )
                ]
            )
        ]
    )

    # Run the Dash app
    app.run_server(debug=False)