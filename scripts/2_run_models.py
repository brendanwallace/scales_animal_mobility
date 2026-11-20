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


FOLDER = "../results/movebank/"
MAPS_FOLDER = "../results/movebank/maps/"

FILE_SUFFIX = ""
STOP_RADII = [30]
LABEL_SINGLETON = [True]
DOWNSAMPLE_RATE_MINUTES = [10, 60]


SAVE_MAPS = False
DROP_IDENTICAL_LAT_LON = True

START = 0


# Loads all the data using glob.glob.

movebank_csvs = glob.glob("../data/movebank/events/*.csv")

private_csvs = []

# Load private csvs by glob:
# private_csvs = glob.glob("../data/private/events/*.csv")

# Load private csvs explicitly:
private_csvs =  [
    # "??_elephant_seal.csv",
    # "oberscwhaben_storks.csv",
    # "oberscwhaben_storks_hourly.csv",
    # "gates_brown_bears.csv",
    "abrahms_syndromes.csv",
    # "abrahms_syndromes_mb.csv",
    "short_finned_pilot_whales.csv",
    # "??_polarbear.csv",
    # "joly_moose.csv",
    # "allert_seabirds.csv",
    "camrin_sharks.csv",
    # "gmaps.csv",
]

# Concat if needed:
all_csvs = private_csvs # private_csvs + movebank_csvs


# Applies downsample rates and runs once for each of these.
def main():

    for i in range(START, len(all_csvs)):
        df = pd.read_csv(all_csvs[i], low_memory=False)

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
                            indiv_model_output, final_series, stop_locations, final_sizes, _df = bw_util.run_model_on_individual(
                                df_individual, study_id, _species, _id, 
                                downsample_rate_minutes = downsample_rate,
                                stop_radius = stop_radius,
                                label_singleton = label_singleton)

                            model_outputs.append((f"(r={stop_radius} singleton={label_singleton})", final_series, stop_locations, stop_radius))
                            all_data.append(asdict(indiv_model_output))

            
                    # TODO: this is broken when DOWNSAMPLE_RATES isn't just [None].
                    if SAVE_MAPS:
                        filename = FOLDER + f"maps/{study_id}/{_species}/{_id}-{downsample_rate}.html"
                        utils.plot_multiple_on_world_map(model_outputs, _df, filename=filename)

        # save once per dataset.
        pd.DataFrame(all_data).to_csv(FOLDER + f"metrics/{study_id}{FILE_SUFFIX}.csv")
                
if __name__ == "__main__":
    main()