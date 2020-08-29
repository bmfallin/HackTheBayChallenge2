from datetime import datetime, timedelta
from enum import IntEnum
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.figure_factory as ff
import plotly.express as px

from enums import Properties, Organization, DateRangeType

from app import app, station_gaps_df, stations_df, mapbox_token


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
    "Organization",
    "PropertyValue",
    "Station",
    "HUC12Number"
]

property_options = map(lambda x: {
        "label": str(x),
        "value": x.value
    }, Properties)

date_range_options = map(lambda x: {
        "label": str(x),
        "value": x.value
    }, DateRangeType)




layout = [
    html.Div(
        id = "station-form",
        className = "tile container lg-12 md-12 sm-12 xs-12",
        children=[
            html.Div(
                id="station-properties-container",
                className="form-control lg-3 md-6 sm-12 xs-12",
                children = [
                    html.H4(children="Properties"),
                    html.P("The properties to detect gaps in", className="description"),
                    dcc.Dropdown(
                        id="station-property-dropdown",
                        multi=True,
                        value=[Properties.WATER_TEMPERATURE.value],
                        options=[{"label": str(x), "value": x.value } for x in Properties if x != Properties.UNKNOWN],
                        clearable=False
                    )
                ]
            ),
            html.Div(
                id="station-daterange-container",
                className="form-control lg-3 md-6 sm-12 xs-12",
                children = [
                    html.H4(children="Date Range"),
                    html.P("The date range in which to search for gaps", className="description"),
                    dcc.DatePickerRange(
                        id='station-daterange-picker',
                        min_date_allowed=datetime(1990, 1, 1),
                        max_date_allowed=datetime.now(),
                        initial_visible_month=datetime.now(),
                        start_date=datetime(2012, 1, 1).date(),
                        end_date=datetime(2019, 12, 31).date(),
                        clearable=False
                    )
                ]
            ),
            html.Div(
                id="station-daterange-type-container",
                className="form-control lg-3 md-6 sm-12 xs-12",
                children = [
                    html.H4(children="Date Range Type"),
                    html.P("The type of date range search to use", className="description"),
                    dcc.Dropdown(
                        id="station-date-range-dropdown",
                        options= [{"label": str(x), "value": x.value } for x in DateRangeType if x != DateRangeType.UNKNOWN],
                        value=DateRangeType.BETWEEN_DATE_RANGE.value,
                        clearable=False
                    )
                ]
            ),

            html.Div(
                id="station-gapthreshold-container",
                className="form-control lg-3 md-6 sm-12 xs-12",
                children = [
                    html.H4(children="Day Gap Threshold"),
                    html.P("The number of days to be considered a gap", className="description"),
                    dcc.Input(
                        id="station-gap-threshold",
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
            html.Div(
                id="station-search-button-container",
                className = "search-button-container lg-12 md-12 sm-12 xs-12",
                children=[
                    dcc.Loading(
                        id="station-loading",
                        type="default",
                        children=html.Button('Search', id='station-search-button', className="button search-button", n_clicks=0)
                    )
                ]
            )
        ]
    ),
    html.Div(
        className = "container lg-12 md-12 sm-12 xs-12",
        children=[
            html.Div(
                className="tile lg-6 md-12 sm-12 xs-12",
                children=[
                    dcc.Loading(
                        id="station-chart-1-loading",
                        type="default",
                        children=[
                            dcc.Graph(id='station-chart-1')
                        ]
                    )
                ]
            ),
            html.Div(
                className="tile lg-6 md-12 sm-12 xs-12",
                children=[
                    dcc.Loading(
                        id="station-chart-2-loading",
                        type="default",
                        children=[
                            dcc.Graph(id='station-chart-2')
                        ]
                    )
                ]
            )
        ]
    ),
    html.Div(
        className = "container lg-12 md-12 sm-12 xs-12",
        children=[
            html.Div(
                className="tile lg-12 md-12 sm-12 xs-12",
                children=[
                    dash_table.DataTable(
                        id='station-datatable',
                        columns=[
                            {"name": i, "id": i} for i in COLUMNS[:-4]
                        ],
                        page_current=0,
                        page_size=PAGE_SIZE,
                        page_action='custom',
                        style_table={'overflowX': 'auto'}
                    )
                ]
            )
        ]
    )
]


@app.callback(
    [
        Output(component_id='station-gap-threshold', component_property='max'),
        Output(component_id='station-gap-threshold', component_property='value'),
        Output(component_id='station-gap-threshold', component_property='placeholder'),
    ],
    [
        Input(component_id='station-daterange-picker', component_property='start_date'),
        Input(component_id='station-daterange-picker', component_property='end_date'),
    ],
    [
        State(component_id='station-gap-threshold', component_property='value')
    ]
)
def set_gap_limit(start_date, end_date, value):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    difference = end - start

    gap = difference.days
    placeholder = f"(min: 1, max: {gap})"
    output_value = min(max(1, value), gap)

    return [gap, output_value, placeholder]


@app.callback(
    Output(component_id='station-chart-1', component_property='figure'),
    [ 
        Input(component_id='station-search-button', component_property='n_clicks')
    ],
    [
        State(component_id='station-property-dropdown', component_property='value'),
        State(component_id='station-daterange-picker', component_property='start_date'),
        State(component_id='station-daterange-picker', component_property='end_date'),
        State(component_id='station-date-range-dropdown', component_property='value'),
        State(component_id='station-gap-threshold', component_property='value'),
    ]
)
def display_map(clicks, properties, start_date, end_date, date_range_type, gap_threshold):

    df = filter_df(properties, start_date, end_date, date_range_type, gap_threshold)
    
    df["Days"] = df["Elapsed"].dt.days
    
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="PropertyName",
        size="Days",
        custom_data=["StationCode"],
        height=700,
        zoom=5
    )
    fig.update_layout(mapbox=dict(accesstoken=mapbox_token))
    
    title = get_chart_gap_title(start_date, end_date, gap_threshold, date_range_type)
    fig.update_layout(title=title)

    return fig


@app.callback(
    Output(component_id='station-chart-2', component_property='figure'),
    [ 
        Input(component_id='station-chart-1', component_property='selectedData')
    ],
    [
        State(component_id='station-property-dropdown', component_property='value'),
        State(component_id='station-daterange-picker', component_property='start_date'),
        State(component_id='station-daterange-picker', component_property='end_date'),
        State(component_id='station-date-range-dropdown', component_property='value'),
        State(component_id='station-gap-threshold', component_property='value'),
    ]
)
def display_timeline(selected_stations, properties, start_date, end_date, date_range_type, gap_threshold):

    df = filter_df(properties, start_date, end_date, date_range_type, gap_threshold)

    # Combine All Stations
    stations = []
    for point in selected_stations["points"]:
        stations.append(point["customdata"][0])

    # Filter Stations
    df = df[df['StationCode'].isin(stations)]

    df["Task"] = df.apply(lambda row: f"{row.StationCode}: {row.PropertyName}", axis = 1)
    fig = ff.create_gantt(df, group_tasks=True)

    title = get_chart_gap_title(start_date, end_date, gap_threshold, date_range_type)
    fig.update_layout(title=title)

    return fig


@app.callback(
    Output(component_id="station-datatable", component_property="data"),
    [ 
        Input(component_id="station-search-button", component_property="n_clicks"),
        Input(component_id="station-datatable", component_property="page_current"),
        Input(component_id="station-datatable", component_property="page_size")
    ],
    [
        State(component_id='station-property-dropdown', component_property='value'),
        State(component_id='station-daterange-picker', component_property='start_date'),
        State(component_id='station-daterange-picker', component_property='end_date'),
        State(component_id='station-date-range-dropdown', component_property='value'),
        State(component_id='station-gap-threshold', component_property='value'),
    ]
)
def update_table(clicks, page_current, page_size, properties, start_date, end_date, date_range_type, gap_threshold):

    df = filter_df(properties, start_date, end_date, date_range_type, gap_threshold)
    
    # reorder columns
    df = df[COLUMNS]
    df["Elapsed"] = df["Elapsed"].dt.days

    return df.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')



def get_chart_gap_title(start_date, end_date, gap_threshold, date_range_type):

    if gap_threshold > 1:
        gap_timespan = f"{gap_threshold} days"
    else:
        gap_timespan = f"{gap_threshold} day"

    start_string = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
    end_string = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")

    if date_range_type == DateRangeType.BETWEEN_DATE_RANGE:
        search_type = "between"
    else:
        search_type = "overlapping"

    return f"Time gaps greater than {gap_timespan} {search_type} date range {start_string} - {end_string}"


def filter_df(properties, start_date, end_date, date_range_type, gap_threshold):

    df = station_gaps_df

    if date_range_type == DateRangeType.BETWEEN_DATE_RANGE:
        date_filter = (df["Start"] >= start_date) & (df["Finish"] <= end_date)
    else:
        date_filter = (df["Start"] <= end_date) & (df["Finish"] >= start_date)


    elapsed_filter = (df["Elapsed"] >= timedelta(days=gap_threshold))

    df = df[date_filter & elapsed_filter]

    df = df[df['PropertyValue'].isin(properties)]

    """
    if organization != Organization.UNKNOWN.value:
        df = df[(df["Organization"] == organization)]
    """

    return df