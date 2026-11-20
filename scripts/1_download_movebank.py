#!/usr/bin/env python
# coding: utf-8

# In[16]:


"""
This script downloads all the events for the movebank studies in 
studies_to_use and does a bit of data cleaning.
"""

import os
import pandas as pd
import numpy as np
from dataclasses import asdict
import requests
from io import StringIO
import seaborn as sns
import hashlib
import timeout_decorator
from pathlib import Path

pd.set_option('display.max_columns', None)

import util as bw_utils

from scales_human_mobility.utils import scale_by_scale_optim
from scales_human_mobility.utils import compute_intervals
from scales_human_mobility.utils import scales_of_mobility
from scales_human_mobility.utils import scale_fitter_no_grid
from scales_human_mobility.utils import utils



BASE_URL = "https://www.movebank.org/movebank/service/direct-read"
AUTH = ('bxwallace', 'House41!?')
FOLDER = "../data/movebank/events/"

STUDIES_TO_USE = "../data/movebank/studies/studies_to_use.csv"


# In[40]:


# Download the data.

studies = pd.read_csv(STUDIES_TO_USE)


# In[46]:


import time

@timeout_decorator.timeout(60*5)
def load_study(study_id, study_name):
    df = bw_utils.get_event(study_id, BASE_URL, AUTH, full=True)

    df = df.rename(columns={
        "individual_local_identifier": "individual",
        "location_lat": "latitude",
        "location_long": "longitude", 
        "individual_taxon_canonical_name": "species",
    })
    
    df = df.dropna(subset=[
        "latitude",
        "longitude",
        "timestamp",
        "individual",
        "species"], ignore_index=True)
    
    df["time"] = (pd.to_datetime(df["timestamp"]) - pd.Timestamp("1970-01-01")) / pd.Timedelta("1s")

    df.to_csv(FOLDER + f"{study_id}.csv")


exists, added, missing = 0, 0, 0
for i in range(150, len(studies)):
    study_id = studies.iloc[i]["id"]
    study_name = studies.iloc[i]["name"].replace("/", "") # remove the /s

    file = FOLDER + f"{study_id}-{study_name}.csv"

    if Path(file).exists():
        print(f"{i}/{len(studies)} already downloaded")
        
        exists += 1
    else:
        print(f"\r{i}/{len(studies)} {file}", end="...\n")

        if "stork" in study_name.lower():
            print("skipping stork row")
            continue
        
        try:
            load_study(study_id, study_name)
            print("downloaded")
            added += 1
        except Exception as e:
            print(e)
            missing += 1

print(f"{exists} already downloaded, {added} added, {missing} still missing")


# In[ ]:




