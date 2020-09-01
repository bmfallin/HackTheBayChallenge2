import json
from datetime import datetime, timedelta
from enum import IntEnum

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

import chartutils
from app import app, geo_df, land_cover_df, mapbox_token, summary_df
from enums import ChartType, DateRangeType, Organization, Properties

PAGE_SIZE = 20
COLUMNS = [
    "Start",
    "Finish",
    "Elapsed",
    "PropertyName",
    "StationCode",
    "HUC12",
    "HUCName",
    "Latitude",
    "Longitude",
    "County",
    "State",
    "OrganizationName",
    "Property",
    "Station",
    "HUC12"
]


layout = [

    # Top Row
    html.Div(
        className = "container lg-12 md-12 sm-12 xs-12",
        children=[

            # Description/Form
            html.Div(
                id = "huc-form",
                className = "tile lg-3 md-12 sm-12 xs-12",
                children=[
                    dcc.Tabs(
                        children=[
                            dcc.Tab(
                                label="Description",
                                children=[
                                    html.H2("HUC12 Analysis"),
                                    html.P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis efficitur mi quis massa vulputate, in pretium arcu semper. Nullam aliquam ornare nisi sit amet ultricies. Vestibulum lobortis erat vel eros aliquam, nec accumsan magna dignissim. Donec vulputate augue eu massa facilisis consectetur. Vestibulum pulvinar dui purus, vel sollicitudin tellus scelerisque non. Mauris tincidunt mauris ut risus pretium, ac dignissim felis viverra. Maecenas dolor dolor, faucibus lacinia sem vitae, commodo venenatis velit. Sed id ipsum tempus, ornare nibh sit amet, elementum arcu. In consequat lectus eu mi molestie consequat. Quisque dapibus sodales sem, vel aliquet leo condimentum in. Nulla facilisi. Maecenas a est venenatis, tristique elit vitae, interdum risus. Morbi dolor turpis, dignissim a quam sit amet, faucibus fringilla leo. Nulla ultrices et urna at lobortis."),
                                    html.P("Sed vel tortor sem. Phasellus dictum laoreet quam in porttitor. Proin tellus dui, dapibus quis quam quis, consequat tristique nulla. Aliquam fermentum rutrum ullamcorper. Donec iaculis ante et rutrum euismod. Suspendisse bibendum ultricies pharetra. Aliquam facilisis, tortor ut lobortis vulputate, turpis urna facilisis ante, in fermentum risus nulla in mauris. Morbi gravida rhoncus pharetra. Ut blandit, purus vel posuere maximus, enim tortor porta dui, at molestie eros eros eu arcu. Vivamus ultricies felis ac ullamcorper tincidunt. Cras in velit eu tortor pellentesque convallis. Vivamus cursus felis quam. Ut nunc ex, gravida a scelerisque convallis, fermentum at nisi. Vestibulum rutrum mattis fermentum. Etiam quis leo elit. Aenean eu nunc eu sem placerat condimentum.")
                                ]
                            ),
                            dcc.Tab(
                                label="Filter",
                                children=[
                                    # Property Dropdown
                                    html.Div(
                                        className="form-control lg-12 md-12 sm-12 xs-12",
                                        children = [
                                            html.H4(children="Properties"),
                                            html.P("The properties to detect gaps in", className="description"),
                                            dcc.Dropdown(
                                                id="huc-property-dropdown",
                                                multi=True,
                                                value=[Properties.WATER_TEMPERATURE.value],
                                                options=[{"label": str(x), "value": x.value } for x in Properties if x != Properties.UNKNOWN],
                                                clearable=False
                                            )
                                        ]
                                    ),

                                    # Date Range Picker
                                    html.Div(
                                        className="form-control lg-12 md-12 sm-12 xs-12",
                                        children = [
                                            html.H4(children="Date Range"),
                                            html.P("The date range in which to search for gaps", className="description"),
                                            dcc.DatePickerRange(
                                                id='huc-daterange-picker',
                                                min_date_allowed=datetime(1990, 1, 1),
                                                max_date_allowed=datetime.now(),
                                                initial_visible_month=datetime.now(),
                                                start_date=datetime(2012, 1, 1).date(),
                                                end_date=datetime(2019, 12, 31).date(),
                                                clearable=False
                                            )
                                        ]
                                    ),

                                    # Date Range Type
                                    html.Div(
                                        className="form-control lg-12 md-12 sm-12 xs-12",
                                        children = [
                                            html.H4(children="Date Range Type"),
                                            html.P("The type of date range search to use", className="description"),
                                            dcc.Dropdown(
                                                id="huc-date-range-dropdown",
                                                options= [{"label": str(x), "value": x.value } for x in DateRangeType if x != DateRangeType.UNKNOWN],
                                                value=DateRangeType.BETWEEN_DATE_RANGE.value,
                                                clearable=False
                                            )
                                        ]
                                    ),

                                    # Gap Threshold
                                    html.Div(
                                        className="form-control lg-12 md-12 sm-12 xs-12",
                                        children = [
                                            html.H4(children="Day Gap Threshold"),
                                            html.P("The number of days to be considered a gap", className="description"),
                                            dcc.Input(
                                                id="huc-gap-threshold",
                                                className="input",
                                                type="number",
                                                placeholder="(min: 1, max: 1000)",
                                                min=1,
                                                max=1000,
                                                step=1,
                                                value=30
                                            )
                                        ]
                                    ),

                                    # Serach Button
                                    html.Div(
                                        className = "search-button-container lg-12 md-12 sm-12 xs-12",
                                        children=[
                                            dcc.Loading(
                                                type="default",
                                                children=html.Button('Search', id='huc-search-button', className="button search-button", n_clicks=0)
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),

            # Map
            html.Div(
                className="tile lg-9 md-12 sm-12 xs-12",
                children=[
                    dcc.Loading(
                        type="default",
                        children=[
                            dcc.Graph(id='huc-chart-1')
                        ]
                    )
                ]
            ),

        ]
    ),
    # Charts
    html.Div(
        className = "container lg-12 md-12 sm-12 xs-12",
        children=[
            # Timeline
            html.Div(
                className="tile lg-6 md-12 sm-12 xs-12",
                children=[
                    dcc.Dropdown(
                        id="huc-chart-2-dropdown",
                        options= [{"label": str(x), "value": x.value } for x in ChartType if x != ChartType.UNKNOWN],
                        value=ChartType.COVERAGE_TIMESPANS_OVER_GAP_THRESHOLD.value,
                        clearable=False
                    ),
                    dcc.Loading(
                        type="default",
                        children=[
                            dcc.Graph(id='huc-chart-2')
                        ]
                    )
                ]
            )
        ]
    )
]



@app.callback(
    Output(component_id='huc-chart-1', component_property='figure'),
    [ 
        Input(component_id='huc-search-button', component_property='n_clicks')
    ]
)
def update_map(clicks):

    df = pd.merge(geo_df, land_cover_df, on="HUC12", how="left")
    
    #df["geometry"] = df.geometry.simplify(tolerance=0.000083,preserve_topology=True)

    df.set_index("HUC12")

    regions = json.loads(df.to_json())
    for region in regions["features"]:
        region["id"] = str(region["properties"]["HUC12"])

    """
    fig = px.choropleth_mapbox(
        df,
        geojson=regions,
        locations="HUC12",
        color="Percent Developed",
        color_continuous_scale="Inferno",
        mapbox_style="light",
        zoom=5, center = {"lat": 39.842286, "lon": -76.651252},
        opacity=0.5
    )
    """

    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=regions,
            locations=df["HUC12"],
            z=df["Percent Developed"],
            colorscale="Teal",
            zmin=0,
            zmax=100,
            marker_line_width=0,

        )
    )

    fig.update_layout(
        mapbox_style="light",
        mapbox_zoom=5,
        mapbox_center = {"lat": 39.842286, "lon": -76.651252},
        mapbox_accesstoken=mapbox_token,
        height=700,
        margin={"r":5,"t":50,"l":5,"b":5}
    )

    return fig




    "Percent Wetland"
    "Percent Developed"
    "Percent Agriculture"
    
    
    """
    gdf = geo_df

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
    fig = px.choropleth_mapbox(
        map_df,
        geojson=regions,
        locations="HUC12",
        color="Elapsed",
        color_continuous_scale="Viridis",
        mapbox_style="light",
        zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
        opacity=0.5
    )

    # Add a mapbox token to the choropleth map
    fig.update_layout(
        mapbox_accesstoken=mapbox_token
    )


    return fig
    """
