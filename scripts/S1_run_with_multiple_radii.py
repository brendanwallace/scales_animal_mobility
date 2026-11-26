#!/usr/bin/env python
# coding: utf-8

# In[1]:


import infostop
import pandas as pd
import utm
import numpy as np
import os
import glob
from datetime import datetime
from dataclasses import asdict
# pd.set_option('display.max_rows', None)
import argparse

import util as bw_util

from scales_human_mobility.utils import scale_by_scale_optim
from scales_human_mobility.utils import compute_intervals
from scales_human_mobility.utils import scales_of_mobility
from scales_human_mobility.utils import scale_fitter_no_grid
from scales_human_mobility.utils import utils

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start', default=0, type=int)      # option that takes a value

args = parser.parse_args()
# In[20]:


FOLDER = "../results/S1_three_best_radii/"
EVENTS_FOLDER = "../data/movebank/events/"

FILE_SUFFIX = ""
LABEL_SINGLETON = [True]
DOWNSAMPLE_RATE_MINUTES = [60]

START = args.start
SAVE_MAPS = False
DROP_IDENTICAL_LAT_LON = True


# If this is True, ignore movebank csvs and load the specific studies in
# STUDIES_TO_RUN instead.
RUN_LISTED_STUDIES = False

movebank_csvs = glob.glob(EVENTS_FOLDER + "*.csv")
LISTED_STUDIES = [
    "736029750", # african bush elephant, low temporal
    "190490326", # tortoise
    "492444603", # gray wolf, high temporal
    "1426277950", # american barn owls (3)
    "501903109", # red kite
    "1605799506", # eurasian oystercatcher
    "1480583194", # caspian tern
    "1936932457", # manatee
    "1420256397", # walrus
]

if RUN_LISTED_STUDIES:
    END = len(LISTED_STUDIES)
else:
    END = len(movebank_csvs)

radii_df = pd.read_csv("../results/radii_to_use.csv")
BASE_STOP_RADII = {
    # "10m": 10,
    "30m": 30,
    # "90m": 90,
}
RADII_TO_LOAD = [
    "best_radius",
    "0.9_radius",
    "0.7_radius",
    "30_percentile_step",
    "20_percentile_step",
    "10_percentile_step",
]




# In[21]:


# Applies downsample rates and runs once for each of these.
def main():
    
    for i in range(START, END):
        if RUN_LISTED_STUDIES:
            study_id = LISTED_STUDIES[i]
            df = pd.read_csv(EVENTS_FOLDER + f"{study_id}.csv", low_memory=False)
        else:
            df = pd.read_csv(movebank_csvs[i], low_memory=False)
        # There should only be one study id.
            if len(df) < 1 or "study_id" not in df.columns:
                continue
            assert(len(df["study_id"].unique()) == 1)
            study_id = df["study_id"].unique()[0]


        all_data = []

        SPECIES = df["species"].unique()


        for _species in SPECIES:
            df_species = df[df["species"] == _species]

            print(f"\r{i}/{len(movebank_csvs)} evaluating {study_id} {_species}")

            # set up folders for maps
            if SAVE_MAPS:
                os.makedirs(FOLDER + f"maps/{study_id}/{_species}", exist_ok=True)

            # base stop radii:
            STOP_RADII = BASE_STOP_RADII.copy()
            # add from the dataframe.
            for radius_desc in RADII_TO_LOAD:
                try:
                    STOP_RADII[radius_desc] = radii_df[radii_df["species"] == _species].iloc[0][radius_desc]    
                except IndexError:
                    print(f"skipping {_species} -- no radii")
                    continue

            individuals = df_species["individual"].unique()
            
            num_to_run = len(individuals) #min(len(individuals), 10)
            for j in range(num_to_run):
                _id = individuals[j]
                # This is just a fun little progress bar.
                print(f"\r[{'.' * (j + 1) + ' '*(num_to_run - (j + 1))}]", end="")

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
                    for stop_radius_description, stop_radius in STOP_RADII.items():
                        
                        for label_singleton in LABEL_SINGLETON:
                            indiv_model_output, final_series, stop_locations, final_sizes, _df = bw_util.run_model_on_individual(
                                df_individual, study_id, _species, _id, 
                                downsample_rate_minutes = downsample_rate,
                                stop_radius_description = stop_radius_description,
                                stop_radius = stop_radius,
                                label_singleton = label_singleton)

                            model_outputs.append((f"(r={stop_radius_description} singleton={label_singleton})", final_series, stop_locations, stop_radius))
                            all_data.append(asdict(indiv_model_output))

            
                    # TODO: this is broken when DOWNSAMPLE_RATES isn't just [None].
                    if SAVE_MAPS:
                        filename = FOLDER + f"maps/{study_id}/{_species}/{_id}-{downsample_rate}.html"
                        utils.plot_multiple_on_world_map(model_outputs, _df, filename=filename)

        # save once per dataset.
        pd.DataFrame(all_data).to_csv(FOLDER + f"metrics/{study_id}{FILE_SUFFIX}.csv")
                
if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:




