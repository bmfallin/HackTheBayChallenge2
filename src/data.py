from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import geopandas as gpd
import multiprocessing as mp
import re
from typing import List
from enums import Properties, Organization
from os import path


def __add_features_to_geo_dataframe(df):
    df["geometry"] = df.geometry.simplify(tolerance=0.01, preserve_topology=True)
    return df


def __add_features_to_huc_gap_dataframe(df):
    df["PropertyName"] = df.apply(lambda row: Properties(row.PropertyValue).name, axis = 1)
    df["HUC12"] = df.apply(lambda row: f"0{row.HUC12_}", axis = 1)
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    df["Elapsed"] = df.apply(lambda row: row.Finish - row.Start, axis = 1)
    return df


def __add_features_to_station_gap_dataframe(df):
    df["PropertyName"] = df.apply(lambda row: Properties(row.PropertyValue).name, axis = 1)
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    df["Elapsed"] = df.apply(lambda row: row.Finish - row.Start, axis = 1)
    return df


def __add_features_to_water_dataframe(df):
    df["Property"] = df.apply(lambda row: int(__get_common_prop(row.ParameterName_CBP, row.ParameterName_CMC).value), axis = 1)
    df["DateTime"] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df["Organization"] = df.apply(lambda row: int(Organization.CMC.value) if row.Database == "CMC" else int(Organization.CBP.value) , axis = 1)
    return df


def __create_dataframes():

    water_df = load_water_dataframe()
    geo_df = load_geo_dataframe()

    start = min(water_df["DateTime"])
    end = max(water_df["DateTime"])
    join_df = water_df[["Station", "StationCode", "StationName", "Latitude", "Longitude", "HUC12_", "HUCNAME_", "COUNTY_", "STATE_", "Organization"]]

    huc_gaps_df = __create_dataframe_from_gaps(water_df, "HUC12_", geo_df["HUC12"], start, end, __add_features_to_huc_gap_dataframe)
    huc_join_df = join_df.groupby(["HUC12_"]).first().reset_index()
    huc_gaps_df = pd.merge(huc_gaps_df, huc_join_df, on="HUC12_", how="left")
    huc_gaps_df["Organization"] = huc_gaps_df["Organization"].fillna(0)
    huc_gaps_df["Organization"] = huc_gaps_df["Organization"].astype(int)
    huc_gaps_df = huc_gaps_df.rename(columns={
        "HUC12_": "HUC12",
        "HUCNAME_": "HUCName",
        "STATE_": "State",
        "COUNTY_": "County"
    })
    huc_gaps_df.to_csv("../data/huc12_gaps.csv")

    codes = water_df["StationCode"].unique()
    codes = [c for c in codes if str(c) != "nan"]
    station_gaps_df = __create_dataframe_from_gaps(water_df, "StationCode", codes, start, end, __add_features_to_station_gap_dataframe)
    station_join_df = join_df.groupby(["StationCode"]).first().reset_index()
    station_gaps_df = pd.merge(station_gaps_df, station_join_df, on="StationCode", how="left")
    station_gaps_df = station_gaps_df.rename(columns={
        "HUC12_": "HUC12",
        "HUCNAME_": "HUCName",
        "STATE_": "State",
        "COUNTY_": "County"
    })
    station_gaps_df.to_csv("../data/station_gaps.csv")

    stations_df = join_df.groupby(["StationCode"]).first().reset_index()
    stations_df = stations_df.rename(columns={
        "HUC12_": "HUC12",
        "HUCNAME_": "HUCName",
        "STATE_": "State",
        "COUNTY_": "County"
    })
    stations_df.to_csv("../data/stations.csv")


def __create_dataframe_from_gaps(df, field_name, unique_fields, start, end, add_features):
    print(f"Creating Dataframe from gaps in {field_name} from {start} - {end}")
    # query = (df["DateTime"] >= start) & (df["DateTime"] <= end)
    # df = df[query]

    # 
    gap_list = []
    funclist = []
    pool = mp.Pool(mp.cpu_count())

    # 
    for field in unique_fields:
        fdf = df[df[field_name] == field]
        f = pool.apply_async(__find_gaps, [fdf, start, end, field_name, field])
        funclist.append(f)

    # Combine our results
    for f in funclist:
        gap_list.extend(f.get())

    # Convert our list of gaps to a dataframe
    gaps_df = pd.DataFrame(gap_list)


    gaps_df = parallel_dataframe(gaps_df, add_features)
    print("Finished finding gaps")
    return gaps_df


def __create_gap(start, end, prop, name, value):
    return {
        "Start": start,
        "Finish": end,
        "PropertyValue": prop,
        name: value
    }


def __find_gaps(df, start, end, name, value):

    # Declare gaps we will return
    gap_list = []

    for prop in Properties:

        if prop == Properties.UNKNOWN:
            continue

        # Query 
        df = df[df["Property"] == prop]

        # Sort our DataFrame by the DateTime column
        df = df.sort_values(by="DateTime")

        # If we have no rows then there is no coverage for this property in this region
        if len(df) == 0:
            gap_list.append(__create_gap(start, end, prop, name, value))

        else:
            # Create a temporary dataframe to hold our start date
            temp_df = pd.DataFrame({})
            temp_df["DateTime"] = pd.to_datetime(start)

            # Add the temporary dataframe to the beginning of our data frame so we can calculate starting gaps
            df = pd.concat([temp_df, df], ignore_index=True)

            # Take the diff of the DateTime column (drop 1st row since it was temporary)
            deltas = df["DateTime"].diff()[1:]

            # Filter for deltas greater than our gap threshold
            time_gaps = deltas[deltas > timedelta(days=1)]

            # Add these gaps to the gaps list
            for index, gap in time_gaps.iteritems():
                start = df["DateTime"][index - 1]
                end = df["DateTime"][index]
                gap_list.append(__create_gap(start, end, prop, name, value))

    # return gaps to the caller
    return gap_list


def __get_common_prop(cbp_name: str, cmc_name: str) -> Properties:
    """Returns a common property from the CBP and CMC property names"""
    
    try: 
        names = [str(cbp_name), str(cmc_name)]

        if __multi_regex("air\stemp", names):
            return Properties.AIR_TEMPERATURE
    
        elif __multi_regex("alkalinity", names):
            return Properties.ALKALINITY

        elif __multi_regex("ammoni.*nitrogen", names):
            return Properties.AMMONIA_NITROGEN

        elif __multi_regex("chlorophyll", names):
            return Properties.CHLOROPHYLL

        elif __multi_regex("conductivity", names):
            return Properties.CONDUCTIVITY

        elif __multi_regex("oxygen|probe\sunits", names):
            return Properties.DISSOLVED_OXYGEN

        elif __multi_regex("bacteria", names):
            return Properties.E_COLI

        elif __multi_regex("enterococcus", names):
            return Properties.ENTEROCOCCUS

        elif __multi_regex("nitr.*nitr", names):
            return Properties.NITRATE_NITROGEN

        elif __multi_regex("orthophosphate", names):
            return Properties.ORTHOPHOSPHATE

        elif __multi_regex("ph[^A-Z]", names):
            return Properties.PH

        elif __multi_regex("phosphorus", names):
            return Properties.PHOSPHORUS

        elif __multi_regex("salinity", names):
            return Properties.SALINITY

        elif __multi_regex("total\sdepth", names):
            return Properties.TOTAL_DEPTH

        elif __multi_regex("total\sdissolved\ssolids", names):
            return Properties.TOTAL_DISSOLVED_SOLIDS

        elif __multi_regex("total.*nitrogen", names):
            return Properties.TOTAL_NITROGEN

        elif __multi_regex("total\ssuspended\ssolids", names):
            return Properties.TOTAL_SUSPENDED_SOLIDS

        elif __multi_regex("turbidity|clarity|secchi", names):
            return Properties.TURBIDITY

        elif __multi_regex("water\stemp", names):
            return Properties.WATER_TEMPERATURE

    except Exception as ex:
        print(ex)

    return Properties.UNKNOWN


def __multi_regex(regex: str, strings: List[str]) -> bool:
    """Performs a regex search on all of the strings in the list and returns true if there are any matches"""
    return any(re.search(regex, value, re.I | re.M) for value in strings)


def parallel_dataframe(df, func, num_cores=mp.cpu_count()):
    df_split = np.array_split(df, num_cores)
    pool = mp.Pool(num_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


def load_water_dataframe():
    
    # Declare the columns and types we will load from Water_FINAL.csv
    columns = {
        "Database": str,
        "Station": str,
        "StationCode": str,
        "StationName": str,
        "ParameterName_CBP": str,
        "ParameterName_CMC": str,
        "Latitude": "float64",
        "Longitude": "float64",
        "HUC12_": "int64",
        "HUCNAME_": str,
        "COUNTY_": str,
        "STATE_": str,
        "Date": str,
        "Time": str,
    }

    # Read the Water_FINAL.csv into a dataframe 
    print("Loading Water_FINAL.csv...")
    df = pd.read_csv("../data/Water_FINAL.csv", usecols=columns.keys(), dtype=columns)

    # Add features to our dataframe
    print("Adding features to DataFrame...")
    df = parallel_dataframe(df, __add_features_to_water_dataframe)

    print("Finished loading and processing dataframe")
    return df


def load_geo_dataframe():
    # Read in the HUC12 data as a GeoDataFrame
    print("Loading mid_atlantic.gdf...")
    gdf = gpd.read_file("../data/huc12/mid_atlantic.gdf")
    gdf["HUC12"] = gdf["HUC12"].astype("int64")

    print("Adding features to DataFrame...")
    gdf = parallel_dataframe(gdf, __add_features_to_geo_dataframe)

    print("Finished loading and processing dataframe")
    return gdf


def load_huc_gaps():
    
    print("Loading huc12_gaps.csv...")
    columns = {
        "HUC12": str,
        "HUCName": str,
        "Station": str,
        "StationCode": str,
        "State": str,
        "County": str,
        "Latitude": "float64",
        "Longitude": "float64",
        "Organization": "int64",
        "PropertyValue": "int64",
        "PropertyName": str,
        "Start": str,
        "Finish": str,
        "Elapsed": str
    }

    df = pd.read_csv("../data/huc12_gaps.csv", usecols=columns.keys(), dtype=columns)

    print("Adding features to DataFrame...")
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    df["Elapsed"] = pd.to_timedelta(df["Elapsed"])
    df["HUC12Number"] = pd.to_numeric(df["HUC12"])

    print("Finished loading and processing dataframe")
    return df


def load_station_gaps():
    
    print("Loading station_gaps.csv...")
    columns = {
        "HUC12": str,
        "HUCName": str,
        "Station": str,
        "StationCode": str,
        "State": str,
        "County": str,
        "Latitude": "float64",
        "Longitude": "float64",
        "Organization": "int64",
        "PropertyValue": "int64",
        "PropertyName": str,
        "Start": str,
        "Finish": str,
        "Elapsed": str
    }

    df = pd.read_csv("../data/station_gaps.csv", usecols=columns.keys(), dtype=columns)

    print("Adding features to DataFrame...")
    df["Start"] = pd.to_datetime(df["Start"])
    df["Finish"] = pd.to_datetime(df["Finish"])
    df["Elapsed"] = pd.to_timedelta(df["Elapsed"])
    df["HUC12Number"] = pd.to_numeric(df["HUC12"])

    print("Finished loading and processing dataframe")
    return df


def load_stations():
    
    print("Loading stations.csv...")
    columns = {
        "HUC12": str,
        "HUCName": str,
        "Station": str,
        "StationCode": str,
        "State": str,
        "County": str,
        "Latitude": "float64",
        "Longitude": "float64",
        "Organization": "int64"
    }

    df = pd.read_csv("../data/stations.csv", usecols=columns.keys(), dtype=columns)

    print("Adding features to DataFrame...")
    df["HUC12Number"] = pd.to_numeric(df["HUC12"])

    print("Finished loading and processing dataframe")
    return df


if __name__ == "__main__":

    __create_dataframes()