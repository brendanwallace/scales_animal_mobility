#!/usr/bin/env python
# coding: utf-8

# In[39]:


import infostop
import pandas as pd
import utm
import numpy as np
import os
import glob
from datetime import datetime
from dataclasses import asdict
# pd.set_option('display.max_rows', None)

import util as bw_util

from scales_human_mobility.utils import scale_by_scale_optim
from scales_human_mobility.utils import compute_intervals
from scales_human_mobility.utils import scales_of_mobility
from scales_human_mobility.utils import scale_fitter_no_grid
from scales_human_mobility.utils import utils

import seaborn as sns


FOLDER = "../results/S1_stop_radii/stops_at_different_radii/"

FILE_SUFFIX = ""
STOP_RADII = [1, 2, 3, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200]
LABEL_SINGLETON = [True]
DOWNSAMPLE_RATE_MINUTES = [60]

DROP_IDENTICAL_LAT_LON = True

START = 0


# In[36]:


# Loads all the data using glob.glob.

movebank_csvs = glob.glob("../data/movebank/events/*.csv")

# private_csvs = []

# Load private csvs by glob:
# private_csvs = glob.glob("../data/private/events/*.csv")

# Load private csvs explicitly:
PRIVATE_FOLDER = "../data/private/events/"
private_csvs = [PRIVATE_FOLDER + f for f in [
    # "??_elephant_seal.csv",
    # "oberscwhaben_storks.csv",
    # "oberscwhaben_storks_hourly.csv",
    # "gates_brown_bears.csv",
    # "abrahms_syndromes.csv",
    # "abrahms_syndromes_mb.csv",
    "short_finned_pilot_whales.csv",
    # "??_polarbear.csv",
    # "joly_moose.csv",
    # "allert_seabirds.csv",
    "camrin_sharks.csv",
    # "gmaps.csv",
]]

# Concat if needed:
all_csvs = private_csvs + movebank_csvs


def find_stops(
    df_individual: pd.DataFrame,
    study_name: str,
    species_name: str,
    individual: str,
    downsample_rate_minutes : int = 60,
    stop_radius : int = 30,
    label_singleton : bool = True,
):
    _df = bw_util.downsampled(df_individual, downsample_rate_minutes)
    
    _df = _df[['latitude','longitude','time']].dropna()
    _df = _df.sort_values(by = 'time').reset_index(drop = True)
    
    # Computes pairwise time intervals, in seconds.
    _times = _df.sort_values(by = 'time')["time"].to_numpy()
    intervals_seconds = (_times[1:] - _times[:-1])
    
    
    # Uses haversine formula in numpy to very quickly find distances between lat/long.
    # There are more accurate libraries, but this is generally best practice, and 
    # was already implemented by the scales of human mobility library.
    points = _df[['latitude', 'longitude']].to_numpy()
    distances_meters = utils.haversine(points[:-1], points[1:])
    
    speeds_ms = distances_meters / intervals_seconds
    
    output = bw_util.ModelOutput(
        dataset=study_name,
        species=species_name,
        individual=individual,
        label_singleton=label_singleton,
        stop_radius=stop_radius,
        downsample_rate_minutes=downsample_rate_minutes,
        median_minutes_between_gps=bw_util.median_minutes_between_gps(_df),
        mean_minutes_between_gps=bw_util.mean_minutes_between_gps(_df),
        median_speed=np.nanmedian(speeds_ms),
        mean_speed=np.nanmean(speeds_ms),
        num_gps_points=len(_df),
        data_starts=datetime.fromtimestamp(_df.iloc[0]["time"]),
        data_ends=datetime.fromtimestamp(_df.iloc[-1]["time"]),
        days_spanned=(_df.iloc[-1]["time"] - _df.iloc[0]["time"]) / 86400, # seconds per day
    )
    
    
    if len(speeds_ms) > 0:
        output.max_speed = np.nanmax(speeds_ms)
    
    labels, stop_locations = None, None
    try:
        labels, stop_locations = scales_of_mobility.labels_stop_locations(_df, r=stop_radius, label_singleton=label_singleton)
        # print(f"found {len(stop_locations)} stops")
        if stop_locations is not None:
            output.num_stops = len(stop_locations)
            # we're at at least 1 now.
            output.num_scales = 1
    except Exception as e:
        pass
        # print("error finding stops -- ", e)
    return output


# Applies downsample rates and runs once for each of these.
def main():
    for i in range(START, len(all_csvs)):
        all_data = []

        df = pd.read_csv(all_csvs[i], low_memory=False)

        # There should only be one study id.
        if len(df) < 1 or "study_id" not in df.columns:
            continue
        assert(len(df["study_id"].unique()) == 1)
        study_id = df["study_id"].unique()[0]


        SPECIES = df["species"].unique()


        for _species in SPECIES:
            df_species = df[df["species"] == _species]

            print(f"\r{i}/{len(movebank_csvs)} evaluating {study_id} {_species}")

            individuals = df_species["individual"].unique()
            
            for j in range(len(individuals)):
                _id = individuals[j]
                # This is just a fun little progress bar.
                print(f"\r[{'.' * (j + 1) + ' '*(len(individuals) - (j + 1))}]", end="")

                df_individual = df_species[df_species["individual"] == _id]

                for downsample_rate in DOWNSAMPLE_RATE_MINUTES:

                    _df = bw_util.downsampled(df_individual, downsample_rate)
                    if DROP_IDENTICAL_LAT_LON:
                        _df = bw_util.drop_identical_lat_lon(_df)
                    
                    _df = _df[['latitude','longitude','time']].dropna()
                    _df = _df.sort_values(by = 'time').reset_index(drop = True)
        
                    # Computes pairwise time intervals, in seconds.
                    _times = _df.sort_values(by = 'time')["time"].to_numpy()
                    intervals_seconds = (_times[1:] - _times[:-1])
        
                    # Uses haversine formula in numpy to very quickly find distances between lat/long.
                    # There are more accurate libraries, but this is generally best practice, and 
                    # was already implemented by the scales of human mobility library.
                    points = _df[['latitude', 'longitude']].to_numpy()
                    distances_meters = utils.haversine(points[:-1], points[1:])
        
                    speeds_ms = distances_meters / intervals_seconds
        
                    model_outputs = []
                    for stop_radius in STOP_RADII:
                        for label_singleton in LABEL_SINGLETON:

                            indiv_model_output = find_stops(_df, study_id, _species, _id, downsample_rate, stop_radius)
                            
                            # indiv_model_output, final_series, stop_locations, final_sizes, _df = bw_util.run_model_on_individual(
                            #     df_individual, study_id, _species, _id, 
                            #     downsample_rate_minutes = downsample_rate,
                            #     stop_radius = stop_radius,
                            #     label_singleton = label_singleton)

                            all_data.append(asdict(indiv_model_output))

          
        # save once per run
        stops_df = pd.DataFrame(all_data)
        stops_df.to_csv(FOLDER + f"{study_id}.csv")


if __name__ == "__main__":
    main()



