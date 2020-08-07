import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import geopandas as gpd
import re

def prop_name(cbp, cmc):
    
    value = "UNKNOWN"

    try: 

        cbp = str(cbp)
        cmc = str(cmc)
    
        if re.search("air\stemp", cbp, re.I | re.M) or re.search("air\stemp", cmc, re.I | re.M):
            value = "AIR_TEMP"
    
        elif re.search("alkalinity", cbp, re.I | re.M) or re.search("alkalinity", cmc, re.I | re.M):
            value = "ALKALINITY"

        elif re.search("bacteria|enterococcus", cbp, re.I | re.M) or re.search("bacteria|enterococcus", cmc, re.I | re.M):
            value = "BACTERIA"

        elif re.search("chlorophyll", cbp, re.I | re.M) or re.search("chlorophyll", cmc, re.I | re.M):
            value = "CHLOROPHYLL"

        elif re.search("conductivity", cbp, re.I | re.M) or re.search("conductivity", cmc, re.I | re.M):
            value = "CONDUCTIVITY"

        elif re.search("total\sdepth", cbp, re.I | re.M) or re.search("total\sdepth", cmc, re.I | re.M):
            value = "DEPTH"

        elif re.search("total\sdissolved\ssolids", cbp, re.I | re.M) or re.search("total\sdissolved\ssolids", cmc, re.I | re.M):
            value = "DISSOLVED_SOLIDS"

        elif re.search("nitrogen|nitrate", cbp, re.I | re.M) or re.search("nitrogen|nitrate", cmc, re.I | re.M):
            value = "NITROGEN"

        elif re.search("oxygen|probe\sunits", cbp, re.I | re.M) or re.search("oxygen|probe\sunits", cmc, re.I | re.M):
            value = "OXYGEN"

        elif re.search("ph[^A-Z]", cbp, re.I | re.M) or re.search("ph[^A-Z]", cmc, re.I | re.M):
            value = "PH"

        elif re.search("phosph", cbp, re.I | re.M) or re.search("phosph", cmc, re.I | re.M):
            value = "PHOSPHORUS"

        elif re.search("salinity", cbp, re.I | re.M) or re.search("salinity", cmc, re.I | re.M):
            value = "SALINITY"

        elif re.search("total\ssuspended\ssolids", cbp, re.I | re.M) or re.search("total\ssuspended\ssolids", cmc, re.I | re.M):
            value = "SUSPENDED_SOLIDS"

        elif re.search("turbidity|clarity|secchi", cbp, re.I | re.M) or re.search("turbidity|clarity|secchi", cmc, re.I | re.M):
            value = "TURBIDITY"

        elif re.search("water\stemp", cbp, re.I | re.M) or re.search("water\stemp", cmc, re.I | re.M):
            value = "WATER_TEMP"

    except Exception as ex:
        print(ex)

    return value

columns = {
    "ParameterName_CBP": str,
    "ParameterName_CMC": str,
    "HUC12_": str,
    "Date": str,
    "Time": str,
    "Latitude": float,
    "Longitude": float,
}

# Read the CSV into a dataframe 
df = pd.read_csv("..\\data\\Water_FINAL.csv", usecols=columns.keys(), dtype=columns)

# Add a column to the DataFrame for the property that is being tracked
df["Property"] = df.apply(lambda row: prop_name(row.ParameterName_CBP, row.ParameterName_CMC), axis = 1)

# Add a DateTime column to the DataFrameCombine Date and Time columns into a single DateTime column as the DateTime type
df["DateTime"] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

# Create a new dataframe that is filtered from the original (by time)
fdf = df[df["DateTime"] >= '01-01-2019']

# Add a column titled huc as a string since it is being shown as an integer in the plot.
# This causes problems displaying correctly as the plot groups them
fdf["huc"] = fdf.apply(lambda row: "huc" + row.HUC12_, axis = 1)

# Create a 3D Scatter chart for our data
fig = px.scatter_3d(fdf, x='huc', y='Property', z='DateTime', color='Property')

# Display the Scatter Chart
fig.show()