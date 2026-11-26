import numpy as np
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field, asdict
import requests
import hashlib
from io import StringIO

from scales_human_mobility.utils import utils
from scales_human_mobility.utils import scales_of_mobility


def downsampled(dataframe, rate_minutes):
    """
    Returns a copy of `dataframe` with rows removed so that no sequential
    rows have timestamps closer than `rate_minutes` apart.

    Assumes that the dataframe has a column "time", with timestamps in seconds.
    """
    if rate_minutes is None:
        return dataframe.copy()

    dataframe = dataframe.copy().sort_values(by = 'time').reset_index(drop = True)

    indices_to_save = []
    previous_time = -1 * rate_minutes * 60
    for i, r in dataframe.iterrows():
        time = r["time"]
        if time - previous_time >= rate_minutes * 60:
            indices_to_save.append(i)
            previous_time = time
    return dataframe.iloc[indices_to_save].reset_index(drop=True)


def test_downsampled():
    TEST_DF_1 = pd.DataFrame({"time": [m * 60 for m in [0, 10, 20, 30, 40, 50, 60]]})
    TEST_DF_2 = pd.DataFrame({"time": [m * 60 for m in [0, 1, 2, 5, 20, 60]]})

    pd.testing.assert_frame_equal(downsampled(TEST_DF_1, None), TEST_DF_1)
    pd.testing.assert_frame_equal(downsampled(TEST_DF_1, 10), TEST_DF_1)
    pd.testing.assert_frame_equal(downsampled(TEST_DF_1, 20), 
                                  pd.DataFrame({"time": [m * 60 for m in [0, 20, 40, 60]]}))
    pd.testing.assert_frame_equal(downsampled(TEST_DF_2, 15), 
                                  pd.DataFrame({"time": [m * 60 for m in [0, 20, 60]]}))
    pd.testing.assert_frame_equal(downsampled(TEST_DF_2, 3), 
                                  pd.DataFrame({"time": [m * 60 for m in [0, 5, 20, 60]]}))



def drop_identical_lat_lon(dataframe):
    """
    Returns a copy of `dataframe` with rows removed so that no sequential
    rows have identical lat lons.

    Assumes that the dataframe has a column "time", with timestamps in seconds, and
    "latitude", "longitude" columns.
    """
    dataframe = dataframe.copy().sort_values(by = 'time').reset_index(drop = True)

    indices_to_save = []
    previous_lat, previous_lon = 0, 0
    for i, r in dataframe.iterrows():
        
        lat, lon = r["latitude"], r["longitude"]
        if not(lat == previous_lat and lon == previous_lon):
            indices_to_save.append(i)
        previous_lat, previous_lon = lat, lon
    return dataframe.iloc[indices_to_save].reset_index(drop=True)


def test_drop_identical_lat_lon():
    TEST_DF_1 = pd.DataFrame(
        {"time": [100, 200, 300, 400],
         "latitude": [1, 2, 3, 3],
        "longitude": [10, 11, 12, 12],}
    )
    TEST_DF_2 = pd.DataFrame(
        {"time": [100, 200, 300],
         "latitude": [1, 2, 3],
        "longitude": [10, 11, 12],}
    )
    pd.testing.assert_frame_equal(drop_identical_lat_lon(TEST_DF_1), TEST_DF_2)


def median_minutes_between_gps(gps_df):
    _times = gps_df.sort_values(by = 'time')["time"].to_numpy()
    return np.median(_times[1:] - _times[:-1]) / 60


def test_median_minutes_between_gps():
    TEST_DF = pd.DataFrame({"time": [0, 60, 120, 180]})
        

    assert median_minutes_between_gps(pd.DataFrame({"time": [0, 60, 120, 180]})) == 1.0
    assert median_minutes_between_gps(pd.DataFrame({"time": [0, 600, 1200, 1000000]})) == 10.0
    # make sure that sorting works
    assert median_minutes_between_gps(pd.DataFrame({"time": [0, 120, 60, 180]})) == 1.0



def mean_minutes_between_gps(gps_df):
    _times = gps_df.sort_values(by = 'time')["time"].to_numpy()
    return np.mean(_times[1:] - _times[:-1]) / 60


def test_mean_minutes_between_gps():
    assert mean_minutes_between_gps(pd.DataFrame({"time": [0, 60, 120, 180]})) == 1.0
    assert mean_minutes_between_gps(pd.DataFrame({"time": [0, 120, 60, 180]})) == 1.0
    assert mean_minutes_between_gps(pd.DataFrame({"time": [0, 600, 600]})) == 5.0


def downsampled(dataframe, rate_minutes):
    """
    Returns a copy of `dataframe` with rows removed so that no sequential
    rows have timestamps closer than `rate_minutes` apart.

    Assumes that the dataframe has a column "time", with timestamps in seconds.
    """
    if rate_minutes is None:
        return dataframe.copy()

    dataframe = dataframe.copy().sort_values(by = 'time').reset_index(drop = True)

    indices_to_save = []
    previous_time = -1 * rate_minutes * 60
    for i, r in dataframe.iterrows():
        time = r["time"]
        if time - previous_time >= rate_minutes * 60:
            indices_to_save.append(i)
            previous_time = time
    return dataframe.iloc[indices_to_save].reset_index(drop=True)
    

def test_downsampled():

    TEST_DF_1 = pd.DataFrame({"time": [m * 60 for m in [0, 10, 20, 30, 40, 50, 60]]})
    TEST_DF_2 = pd.DataFrame({"time": [m * 60 for m in [0, 1, 2, 5, 20, 60]]})

    pd.testing.assert_frame_equal(downsampled(TEST_DF_1, None), TEST_DF_1)
    pd.testing.assert_frame_equal(downsampled(TEST_DF_1, 10), TEST_DF_1)
    pd.testing.assert_frame_equal(downsampled(TEST_DF_1, 20), 
                                  pd.DataFrame({"time": [m * 60 for m in [0, 20, 40, 60]]}))
    pd.testing.assert_frame_equal(downsampled(TEST_DF_2, 15), 
                                  pd.DataFrame({"time": [m * 60 for m in [0, 20, 60]]}))
    pd.testing.assert_frame_equal(downsampled(TEST_DF_2, 3), 
                                  pd.DataFrame({"time": [m * 60 for m in [0, 5, 20, 60]]}))




def get_event(study_id, BASE_URL, AUTH, full=False):
    """
    Queries movebank for all the study data for `study_id`.

    Expects the following to be defined in the environment.

    BASE_URL = "https://www.movebank.org/movebank/service/direct-read"
    AUTH = ([username], [password]) # movebank credentials.

    You should set these in your notebook and not here.
    """
    params = {
        "entity_type": "event",
        "study_id": study_id,
    }
    if not full:
        # Prebuilt event filter to get only the last 30 days of events.
        params["event_reduction_profile"] = "EURING_03"

    else:
        params["attributes"] = "all"
    
    # We have to do this whole stupid double-request to accept the response.
    # We request the data once here, then hash the response text, which is about
    # accepting use terms, and then we send it back.
    response = requests.get(
        BASE_URL,
        params=params,
        auth=AUTH,
    )
    # I'm not totally sure what this line does.
    response.raise_for_status()

    # Make a hash of the response text to show that we read it and accept the terms.
    params["license-md5"] = hashlib.md5(response.text.encode("utf-8")).hexdigest()

    response = requests.get(
        BASE_URL,
        params=params,
        auth=AUTH,
    )
    response.raise_for_status()
    
    event = pd.read_csv(StringIO(response.text))
    return event


def run_models(df, r=30, label_singleton=False, skip_model=False):
    """
    Runs the scales of mobility models.

    This is code pulled from the `scales of human mobility` notebooks.
    """
        
    #Sort by time
    #Find stop locations
    
    labels, stop_locations = None, None
    try:
        labels, stop_locations = scales_of_mobility.labels_stop_locations(df, r=r, label_singleton=label_singleton)
        # print(f"found {len(stop_locations)} stops")
    except Exception as e:
        pass
        # print("error finding stops -- ", e)

    final_series, likelihoods, final_sizes = None, None, None
    if labels is not None and stop_locations is not None and not skip_model:
        try:
            final_series, _, likelihoods, _, final_sizes, _, _ = scales_of_mobility.best_scale(labels, stop_locations)
            final_series = np.array(final_series)
        except Exception as e:
            pass
            # print("error finding scales -- ", e)
    return final_series, stop_locations, final_sizes, 

# utils.plot_solution_on_world_map(final_series, stop_locations, _df, stop_radius=r, filename=f"")#, final_series, likelihoods, final_sizes


@dataclass
class ModelOutput:
    """
    Model output to save.
    """
    dataset: str
    species: str
    individual: str
    stop_radius: float
    stop_radius_description: str
    label_singleton: bool
    downsample_rate_minutes: float
    median_minutes_between_gps: float
    mean_minutes_between_gps: float
    median_speed: float
    mean_speed: float
    num_gps_points: int
    data_starts: datetime
    data_ends: datetime
    days_spanned: float
    max_speed: float = 0
    num_stops: int = 0
    num_scales: int = 0
    final_sizes: list[float] = field(default_factory=list)
    final_size_2: float = 0
    final_size_3: float = 0
    final_size_4: float = 0


def run_model_on_individual(
    df_individual: pd.DataFrame,
    study_name: str,
    species_name: str,
    individual: str,
    downsample_rate_minutes : int = 60,
    stop_radius : int = 30,
    stop_radius_description : str = "30m",
    label_singleton : bool = True,
) -> ModelOutput:
    """
    Runs the model on the data in `df` representing one individual animal.
    """

    # TODO -- correct/rename time, latitude and longitude.

    _df = downsampled(df_individual, downsample_rate_minutes)

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
 
    output = ModelOutput(
        dataset=study_name,
        species=species_name,
        individual=individual,
        label_singleton=label_singleton,
        stop_radius=stop_radius,
        stop_radius_description=stop_radius_description,
        downsample_rate_minutes=downsample_rate_minutes,
        median_minutes_between_gps=median_minutes_between_gps(_df),
        mean_minutes_between_gps=mean_minutes_between_gps(_df),
        median_speed=np.nanmedian(speeds_ms),
        mean_speed=np.nanmean(speeds_ms),
        num_gps_points=len(_df),
        data_starts=datetime.fromtimestamp(_df.iloc[0]["time"]),
        data_ends=datetime.fromtimestamp(_df.iloc[-1]["time"]),
        days_spanned=(_df.iloc[-1]["time"] - _df.iloc[0]["time"]) / 86400, # seconds per day
    )

    
    if len(speeds_ms) > 0:
        output.max_speed = np.nanmax(speeds_ms)

    
    final_series, stop_locations, final_sizes = run_models(
        _df, r=stop_radius, label_singleton=label_singleton, skip_model=False)

    if stop_locations is not None:
        output.num_stops = len(stop_locations)
        # we're at at least 1 now.
        output.num_scales = 1

    # If we can't find scales, this dictionary is set to None.
    if final_sizes is not None:
        # we don't get a size for scale 1 (just the stops).
        output.num_scales = len(final_sizes) + 1
    
        output.final_sizes = final_sizes
        if len(final_sizes) >= 1:
            output.final_size_2 = final_sizes[2]
        if len(final_sizes) >= 2:
            output.final_size_3 = final_sizes[3]
        if len(final_sizes) >= 3:
            output.final_size_4 = final_sizes[4]
        if len(final_sizes) >= 4:
            output.final_size_5 = final_sizes[5]
            # row[f"Final Size {scale_number}"] = final_sizes[scale_number]

    return output, final_series, stop_locations, final_sizes, _df


def test_run_model_on_input():

    assert type(run_model_on_individual(pd.DataFrame({
        "time": [0, 60*60, 60*60*2, 60*60*3],
        "latitude": [0, 0, 0, 0],
        "longitude": [0, 0, 1, 1],
    }),
                "study_name",
                "species_name",
                "individual_name",
                                       )[0]) is ModelOutput

    # tests no speeds, no stops.
    assert type(run_model_on_individual(pd.DataFrame({
        "time": [0],
        "latitude": [0],
        "longitude": [0],
    }),
                "study_name",
                "species_name",
                "individual_name",
                                       )[0]) is ModelOutput
