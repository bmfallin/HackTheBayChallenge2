from datetime import datetime, timedelta
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.figure_factory as ff
import plotly.express as px

from enums import Properties, Organization

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



def get_prop_name(value: Properties) -> str:
    if value == Properties.E_COLI:
        return "E.Coli"

    if value == Properties.PH:
        return "pH"

    return value.name.replace("_", " ").title()

# Create a list of properties for our dropdown
property_options = []
for prop in Properties:
    if prop == Properties.UNKNOWN:
        continue

    property_options.append({
        "label": get_prop_name(prop),
        "value": prop.value
    })


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
                        value=[1],
                        options=property_options,
                    )
                ]
            ),
            html.Div(
                id="station-organization-container",
                className="form-control lg-3 md-6 sm-12 xs-12",
                children = [
                    html.H4(children="Organization"),
                    html.P("The organization to search", className="description"),
                    dcc.RadioItems(
                        id="station-organization-radio-buttons",
                        options=[
                            {'label': 'CMC', 'value': Organization.CMC.value},
                            {'label': 'CBP', 'value': Organization.CBP.value},
                            {'label': 'Both', 'value': Organization.UNKNOWN.value}
                        ],
                        value=Organization.UNKNOWN.value
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
                        end_date=datetime(2019, 12, 31).date()
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
    [
        Output(component_id='station-chart-2', component_property='figure'),
        Output(component_id='station-chart-2', component_property='title'),
    ],
    [ 
        Input(component_id='station-chart-1', component_property='selectedData')
    ],
    [
        State(component_id='station-property-dropdown', component_property='value'),
        State(component_id='station-organization-radio-buttons', component_property='value'),
        State(component_id='station-daterange-picker', component_property='start_date'),
        State(component_id='station-daterange-picker', component_property='end_date'),
        State(component_id='station-gap-threshold', component_property='value'),
    ]
)
def display_timeline(selected_stations, properties, organization, start_date, end_date, gap_threshold):

    df = filter_df(properties, organization, start_date, end_date, gap_threshold)

    # Combine All Stations
    stations = []
    for point in selected_stations["points"]:
        stations.append(point["customdata"][0])

    # Filter Stations
    df = df[df['StationCode'].isin(stations)]

    df["Task"] = df.apply(lambda row: f"{row.StationCode}: {row.PropertyName}", axis = 1)
    figure = ff.create_gantt(df, group_tasks=True)

    title = f"Time gaps over {gap_threshold} day(s) between {start_date} and {end_date}"

    return figure, title


@app.callback(
    [
        Output(component_id='station-chart-1', component_property='figure'),
        Output(component_id='station-chart-1', component_property='title'),
    ],
    [ 
        Input(component_id='station-search-button', component_property='n_clicks')
    ],
    [
        State(component_id='station-property-dropdown', component_property='value'),
        State(component_id='station-organization-radio-buttons', component_property='value'),
        State(component_id='station-daterange-picker', component_property='start_date'),
        State(component_id='station-daterange-picker', component_property='end_date'),
        State(component_id='station-gap-threshold', component_property='value'),
    ]
)
def display_map(clicks, properties, organization, start_date, end_date, gap_threshold):

    df = filter_df(properties, organization, start_date, end_date, gap_threshold)
    
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
    
    title = f"Time gaps over {gap_threshold} day(s) between {start_date} and {end_date}"

    return fig, title


@app.callback(
    Output(component_id="station-datatable", component_property="data"),
    [ 
        Input(component_id="station-search-button", component_property="n_clicks"),
        Input(component_id="station-datatable", component_property="page_current"),
        Input(component_id="station-datatable", component_property="page_size")
    ],
    [
        State(component_id='station-property-dropdown', component_property='value'),
        State(component_id='station-organization-radio-buttons', component_property='value'),
        State(component_id='station-daterange-picker', component_property='start_date'),
        State(component_id='station-daterange-picker', component_property='end_date'),
        State(component_id='station-gap-threshold', component_property='value'),
    ]
)
def update_table(clicks, page_current, page_size, properties, organization, start_date, end_date, gap_threshold):

    df = filter_df(properties, organization, start_date, end_date, gap_threshold)
    
    # reorder columns
    df = df[COLUMNS]
    df["Elapsed"] = df["Elapsed"].dt.days

    return df.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')


def filter_df(properties, organization, start_date, end_date, gap_threshold):

    df = station_gaps_df
    start_filter = (df["Start"] >= start_date)
    end_filter = (df["Finish"] <= end_date)
    elapsed_filter = (df["Elapsed"] >= timedelta(days=gap_threshold))

    df = df[start_filter & end_filter & elapsed_filter]

    df = df[df['PropertyValue'].isin(properties)]

    if organization != Organization.UNKNOWN.value:
        df = df[(df["Organization"] == organization)]

    return df