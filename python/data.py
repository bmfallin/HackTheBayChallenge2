from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import geopandas as gpd
import multiprocessing as mp
import re
from typing import List
from enums import Properties


def __add_features_to_result(df):
    df["PropertyName"] = df.apply(lambda row: Properties(row.PropertyValue).name, axis = 1)
    df["HUC12"] = df.apply(lambda row: f"0{row.HUC12}", axis = 1)
    return df


def __add_features_to_source(df):
    df["Property"] = df.apply(lambda row: __get_common_prop(row.ParameterName_CBP, row.ParameterName_CMC).value, axis = 1)
    df["DateTime"] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    return df


def __create_gap(start, end, prop, huc):
    return {
        "Start": start,
        "Finish": end,
        "PropertyValue": prop,
        "HUC12": huc
    }


def __find_gaps_in_region(df, start, end, huc, gap):

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
            gap_list.append(__create_gap(start, end, prop, huc))

        else:
            # Create a temporary dataframe to hold our start date
            temp_df = pd.DataFrame({})
            temp_df["DateTime"] = pd.to_datetime(start)

            # Add the temporary dataframe to the beginning of our data frame so we can calculate starting gaps
            df = pd.concat([temp_df, df], ignore_index=True)

            # Take the diff of the DateTime column (drop 1st row since it was temporary)
            deltas = df["DateTime"].diff()[1:]

            # Filter for deltas greater than our gap threshold
            time_gaps = deltas[deltas > timedelta(days=gap)]

            # Add these gaps to the gaps list
            for index, gap in time_gaps.iteritems():
                start = df["DateTime"][index - 1]
                end = df["DateTime"][index]
                gap_list.append(__create_gap(start, end, prop, huc))

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


def load_water_final():
    
    # Declare the columns and types we will load from Water_FINAL.csv
    columns = {
        "ParameterName_CBP": str,
        "ParameterName_CMC": str,
        "HUC12_": 'int64',
        "Date": str,
        "Time": str,
    }

    # Read the Water_FINAL.csv into a dataframe 
    print("Loading Water_FINAL.csv...")
    df = pd.read_csv("..\\data\\Water_FINAL.csv", usecols=columns.keys(), dtype=columns)

    # Add features to our dataframe
    print("Adding features to DataFrame...")
    df = parallel_dataframe(df, __add_features_to_source)

    print("Finished loading and processing dataframe")
    return df


def load_huc12():
    # Read in the HUC12 data as a GeoDataFrame
    print("Loading mid_atlantic.gdf...")
    gdf = gpd.read_file("..\\data\\huc12\\mid_atlantic.gdf")
    gdf["HUC12"] = gdf["HUC12"].astype("int64")
    print("Finished Loading mid_atlantic.gdf")
    return gdf


def find_time_gaps(df, regions, start, end, gap_threshold):
    print(f"Finding {gap_threshold} day gaps in {len(regions)} regions from {start} - {end}")
    query = (df["DateTime"] >= start) & (df["DateTime"] <= end)
    df = df[query]

    # 
    gap_list = []
    funclist = []
    pool = mp.Pool(mp.cpu_count())

    # 
    for huc in regions:
        fdf = df[df["HUC12_"] == huc]
        f = pool.apply_async(__find_gaps_in_region, [fdf, start, end, huc, gap_threshold])
        funclist.append(f)

    # Combine our results
    for f in funclist:
        gap_list.extend(f.get())

    # Convert our list of gaps to a dataframe
    gaps_df = pd.DataFrame(gap_list)
    gaps_df = parallel_dataframe(gaps_df, __add_features_to_result)
    print("Finished finding gaps")
    return gaps_df



if __name__ == "__main__":

    start = '01-01-2016'
    end = '01-01-2020'
    gap_threshold = 30

    df = load_water_final()
    gdf = load_huc12()
    gaps_df = find_time_gaps(df, gdf["HUC12"], start, end, gap_threshold)
    gaps_df.to_csv("..\\data\\temp1.csv")
