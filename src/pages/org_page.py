import datetime as dt
from enum import IntEnum

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

import chartutils
import data
from app import app, mapbox_token, summary_df
from enums import Months, Organization

start = min(summary_df["DateTime"])
end = max(summary_df["DateTime"])

marks={}
for year in range(start.year, end.year+1):
    marks[year] = {
        "label": f"{year}"
    }


class AreaChartType(IntEnum):
    UNKNOWN = 0
    SAMPLE_PERCENTAGE_OVER_TIME = 1
    SAMPLE_COUNT_OVER_TIME = 2

    def __str__(self):
        return self.name.replace("_", " ").capitalize()


layout = [

    html.Div(
        className="container lg-12 md-12 sm-12 xs-12",
        children=[
            html.Div(
                className="tile lg-3 md-12 sm-12 xs-12",
                children=[
                    dcc.Tabs(
                        children=[
                            dcc.Tab(
                                label="Description",
                                children=[
                                    html.H2("Organization Comparison"),
                                    html.P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis efficitur mi quis massa vulputate, in pretium arcu semper. Nullam aliquam ornare nisi sit amet ultricies. Vestibulum lobortis erat vel eros aliquam, nec accumsan magna dignissim. Donec vulputate augue eu massa facilisis consectetur. Vestibulum pulvinar dui purus, vel sollicitudin tellus scelerisque non. Mauris tincidunt mauris ut risus pretium, ac dignissim felis viverra. Maecenas dolor dolor, faucibus lacinia sem vitae, commodo venenatis velit. Sed id ipsum tempus, ornare nibh sit amet, elementum arcu. In consequat lectus eu mi molestie consequat. Quisque dapibus sodales sem, vel aliquet leo condimentum in. Nulla facilisi. Maecenas a est venenatis, tristique elit vitae, interdum risus. Morbi dolor turpis, dignissim a quam sit amet, faucibus fringilla leo. Nulla ultrices et urna at lobortis."),
                                    html.P("Sed vel tortor sem. Phasellus dictum laoreet quam in porttitor. Proin tellus dui, dapibus quis quam quis, consequat tristique nulla. Aliquam fermentum rutrum ullamcorper. Donec iaculis ante et rutrum euismod. Suspendisse bibendum ultricies pharetra. Aliquam facilisis, tortor ut lobortis vulputate, turpis urna facilisis ante, in fermentum risus nulla in mauris. Morbi gravida rhoncus pharetra. Ut blandit, purus vel posuere maximus, enim tortor porta dui, at molestie eros eros eu arcu. Vivamus ultricies felis ac ullamcorper tincidunt. Cras in velit eu tortor pellentesque convallis. Vivamus cursus felis quam. Ut nunc ex, gravida a scelerisque convallis, fermentum at nisi. Vestibulum rutrum mattis fermentum. Etiam quis leo elit. Aenean eu nunc eu sem placerat condimentum.")
                                ]
                            ),
                            dcc.Tab(
                                label="Filter",
                                children=[
                                    html.H2("Filter Content"),
                                    html.Button('Search', id='search-button', className="button search-button", n_clicks=0)
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                className="tile lg-9 md-12 sm-12 xs-12",
                children=[
                    html.H2("Sample Collection Timeline"),
                    dcc.RangeSlider(
                        id="year-slider",
                        min=start.year,
                        max=end.year,
                        value=[end.year - 6, end.year],
                        marks=marks,
                        step=None,
                    ),
                    html.P(
                        id="year-slider-text"
                    ),
                    dcc.Loading(
                        type="default",
                        children=[
                            dcc.Graph(id='timeline-chart')
                        ]
                    )
                ]
            )
        ]
    ),
    html.Div(
        className="container lg-12 md-12 sm-12 xs-12",
        children=[
            html.Div(
                className="tile lg-12 md-12 sm-12 xs-12",
                children=[
                    html.H2("Organization Sample Comparison"),
                    dcc.Dropdown(
                        id="area-chart-type",
                        options= [{"label": str(x), "value": x.value } for x in AreaChartType if x != AreaChartType.UNKNOWN],
                        value=AreaChartType.SAMPLE_PERCENTAGE_OVER_TIME.value,
                        clearable=False
                    ),
                    dcc.Loading(
                        type="default",
                        children=[
                            dcc.Graph(id='area-chart')
                        ]
                    )
                ]
            )
        ]
    )
]


@app.callback(
    Output(component_id='year-slider-text', component_property='children'),
    [ 
        Input(component_id='year-slider', component_property='value')
    ]
)
def update_year_slider_text(slider_range):

    if slider_range[1] - slider_range[1] > 8:
        return f"Selecting a large time range may take a few minutes to load."

    return ""


@app.callback(
    Output(component_id='timeline-chart', component_property='figure'),
    [ 
        Input(component_id='year-slider', component_property='value')
    ]
)
def update_map_timeline(slider_range):
    
    try: 
        df = summary_df

        # Add year and month columns, then group by them to obtain counts
        df["Year"] = df["DateTime"].dt.year
        df["Month"] = df["DateTime"].dt.month
        gp = df.groupby(["Year", "Month", "Organization"])

        frames = []
        steps = []

        # loop through all valid date months and year to fill our axis
        for year in range(slider_range[0], slider_range[1]+1):

            start_month = start.month if year == start.year else 1
            end_month = end.month if year == end.year else 12

            for month in range(start_month, end_month+1):

                name = f"{month}/{year}"

                try:
                    cmc = gp.get_group((year, month, Organization.CMC.value))
                except:
                    cmc = pd.DataFrame(columns=["Latitude", "Longitude"])

                try:
                    cbp = gp.get_group((year, month, Organization.CBP.value))
                except:
                    cbp = pd.DataFrame(columns=["Latitude", "Longitude"])


                frame = {
                    "name": name,
                    "data": [
                        {
                            "type":"scattermapbox",
                            "lat":cmc["Latitude"],
                            "lon":cmc["Longitude"],
                            "name": "CMC",
                            "marker": go.scattermapbox.Marker(
                                size=10,
                                opacity=0.05,
                                color="red",
                                showscale=False,
                            )
                        },
                        {
                            "type":"scattermapbox",
                            "lat":cbp["Latitude"],
                            "lon":cbp["Longitude"],
                            "name": "CBP",
                            "marker": go.scattermapbox.Marker(
                                size=10,
                                opacity=0.05,
                                color="blue",
                                showscale=False,
                            )
                        }
                    ],
                }
                frames.append(frame)

                step = {
                    "label": name,
                    "method": "animate",
                    "args": [
                        [name],
                        {'mode':'immediate', 'frame':{'duration':300, 'redraw': True}, 'transition':{'duration':300}}
                    ],
                }
                steps.append(step)



        menus = create_menus()

        fig_layout = go.Layout(
            sliders=[{
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "x":0.08, 
                "len":0.88,
                "currentvalue": {
                    "font":{"size":15},
                    "visible":True,
                    "xanchor":"center"
                },
                "steps": steps
            }],
            updatemenus=menus,
            mapbox={
                'accesstoken':mapbox_token,
                'center':{"lat": 39.842286, "lon": -76.651252},
                'zoom':5,
                'style':'light',
            },
            height=700
        )


        fig = go.Figure(data=frames[0]['data'], layout = fig_layout, frames=frames)
        fig.update_layout(
            title=f"Collection timeline from {slider_range[0]} to {slider_range[1]}",
            margin={"r":5,"t":50,"l":5,"b":5}
        )

        return fig

    except Exception as e:
        print(e)
        return chartutils.create_notification_graph("An error occurred retrieving data")


@app.callback(
    Output(component_id='area-chart', component_property='figure'),
    [ 
        Input(component_id='area-chart-type', component_property='value')
    ]
)
def update_area_chart(chart_number):
    try:

        chart_type = AreaChartType(chart_number)

        if chart_type == AreaChartType.SAMPLE_COUNT_OVER_TIME:
            title = f"Organization sample contribution count from {start.month}/{start.year} to {end.month}/{end.year}"
            groupnorm = ""
            stackgroup = ""
        elif chart_type == AreaChartType.SAMPLE_PERCENTAGE_OVER_TIME:
            title = f"Organization sample contribution percentage from {start.month}/{start.year} to {end.month}/{end.year}"
            groupnorm = "percent"
            stackgroup = "one"
        else:
            title = "Invalid Dropdown Choice"
            groupnorm = ""
            stackgroup = ""

        df = summary_df

        # create our axis for the different traces
        cmc = []
        cbp = []
        times = []

        # Add year and month columns, then group by them to obtain counts
        df["Year"] = df["DateTime"].dt.year
        df["Month"] = df["DateTime"].dt.month
        gp = df.groupby(["Year", "Month", "Organization"])

        # loop through all valid date months and year to fill our axis
        for year in range(start.year, end.year+1):

            start_month = start.month if year == start.year else 1
            end_month = end.month if year == end.year else 12

            for month in range(start_month, end_month):

                times.append(f"{month}/{year}")
                try:
                    cmc.append(len(gp.get_group((year, month, Organization.CMC.value))))
                except:
                    cmc.append(0)

                try:
                    cbp.append(len(gp.get_group((year, month, Organization.CBP.value))))
                except:
                    cbp.append(0)

        # create a figure
        fig = go.Figure()

        #CMC
        fig.add_trace(go.Scatter(
            x=times, y=cmc,
            hoverinfo='x+y',
            mode='lines',
            name= "CMC",
            line=dict(width=0.5, color='red'),
            stackgroup=stackgroup, # define stack group
            groupnorm=groupnorm # sets the normalization for the sum of the stackgroup
        ))

        #CBP
        fig.add_trace(go.Scatter(
            x=times, y=cbp,
            hoverinfo='x+y',
            mode='lines',
            name= "CBP",
            line=dict(width=0.5, color='blue'),
            stackgroup=stackgroup
        ))

        # add a range slider at the bottom
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(
            title=title,
            height=500,
            margin={"r":5,"t":50,"l":5,"b":5}
        )

        return fig
    
    except Exception as e:
        print(e)
        return chartutils.create_notification_graph("An error occurred retrieving data"), ""


def create_menus():

    return [
        {
            'type':'buttons',
            'showactive':True,
            'x':0.045, 'y':-0.08,
            'buttons': [
                {
                    "args": [
                        None,
                        {
                            "frame":{
                                "duration": 500,
                                "redraw": True
                            },
                            "fromcurrent": True,
                            "transition": {
                                "duration": 300,
                                "easing": "quadratic-in-out"
                            }
                        }
                    ],
                    "label": "▶",
                    "method": "animate"
                },
                {
                    "args": [
                        [
                            None
                        ],
                        {
                            "frame": {
                                "duration": 0,
                                "redraw": False
                            },
                            "mode": "immediate",
                            "transition": {
                                "duration": 0
                            }
                        }
                    ],
                    "label": "❚❚",
                    "method": "animate"
                }
            ]
        }
    ]
