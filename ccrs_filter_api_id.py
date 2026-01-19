#!/user/bin/env python3 -tt

# Imports
from collections import defaultdict
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getDataCsv
from ccrs_resource_IDs import CCRS_resource_IDs
from ccrs_query_utils import query_city_ccrs
from ccrs_query_utils import query_ccrs_by_collision_ids

import time

# User variables
# search_cities = ['Del Mar']
outpath = 'C:/Users/karl/python/switrs/CCRS_test_raw/'

# year = '2016'
# collision_ids = [
#     248850,
#     3793369,
#     3793314,
#     3803034,
#     3803031,
#     3803028,
#     3841216,
#     3841212,
#     3841179,
#     3887516,
#     3898787,
#     3898491,
#     3898428,
#     3898812,
#     3915928,
#     3911838,
#     3928795,
#     3928777,
#     3935799,
#     3935797,
#     3935615,
#     3939666,
#     3967653,
#     3967649,
#     3967447,
#     3967433,
#     3967430
# ]

year = '2018'
collision_ids = [
    748152,
    810919,
    817997,
    830625,
    829883,
    883061,
    3305559,
    3303432,
    3303428,
    3303266,
    3309925,
    3321813,
    3348196,
    3347819,
    3347816,
    3347813,
    3347754,
    3347750,
    3378778,
    3377800,
    3377796,
    3389297,
    3396396,
    3396391,
    3396289,
    3396283,
    3395418,
    3395368,
    3392993,
    3402041,
    3401913,
    3438289,
    3438286,
    3441656,
    3441653,
    3441648,
    3441646,
    3467532,
    3463786,
    3477100,
    3476635,
    3500102,
    3510476,
    3510473
]
collision_ids = [str(id) for id in collision_ids]


# Do not edit below this line --------------------------------------------------

def main():

    begtime = time.perf_counter()

    # Set up CCRS API endpoint URLs
    crashes_resource, parties_resource, injuries_resource = CCRS_resource_IDs(year)

    # fetch crashes selected collision_ids
    crashes = query_ccrs_by_collision_ids(collision_ids, crashes_resource, "Collision Id")
    parties = query_ccrs_by_collision_ids(collision_ids, parties_resource, "CollisionId")
    injuries = query_ccrs_by_collision_ids(collision_ids, injuries_resource, "CollisionId")

    # save filtered dictionaries to CSV files
    if crashes:
        crash_out = outpath + f'CCRS_crashes_by_ID_{year}.csv'
        dumpListDictToCSV(crashes, crash_out, ',',  list(crashes[0].keys()) )
        print(f"\n{len(crashes)} Filtered Crashes saved in {crash_out}")

        crash_out = outpath + f'CCRS_crashes_by_ID_{year}.csv'
        dumpListDictToCSV(crashes, crash_out, ',',  list(crashes[0].keys()) )
        print(f"\n{len(crashes)} Filtered Crashes saved in {crash_out}")

        crash_out = outpath + f'CCRS_crashes_by_ID_{year}.csv'
        dumpListDictToCSV(crashes, crash_out, ',',  list(crashes[0].keys()) )
        print(f"\n{len(crashes)} Filtered Crashes saved in {crash_out}")

        print(f"{len(injureds)} Filtered injuries saved in {injured_out}")

        print(f"Time to fetch and save CCRS data for {len(collision_ids)}: {time.perf_counter()-begtime:.4f} sec\n")
    else:
        (f"No CCRS crashes for requested Collision IDs!!\n")


# Main body
if __name__ == '__main__':
    main()