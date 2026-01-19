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
# years = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
# search_cities = ['Del Mar', 'Solana Beach', 'Encinitas', 'Carlsbad', 'Vista', 'Oceanside']
years = ['2025']
search_cities = ['Encinitas']
outpath = 'C:/Users/karl/python/switrs/CCRS_get_raw_api/'

# Do not edit below this line --------------------------------------------------


def main():

    begtime_all = time.perf_counter()

    for year in years:
        for city in search_cities:

            print(f"Trimming full CCRS raw data for {year} and {city}")
            begtime = time.perf_counter()

            # Set up CCRS API endpoint URLs
            crashes_resource, parties_resource, injuries_resource = CCRS_resource_IDs(year)

            # fetch crashes data via CCRS API filtered by 'City Name'=city
            crashes = query_city_ccrs(city, crashes_resource, mode="odata")
            collision_ids = [crash['Collision Id'] for crash in crashes]

            # fetch parties data filtered by selected collision_ids
            parties = query_ccrs_by_collision_ids(collision_ids, parties_resource, "CollisionId")

            # fetch injuries data filtered by selected collision_ids
            injureds = query_ccrs_by_collision_ids(collision_ids, injuries_resource, "CollisionId")
            # only save the real injured, excluding witnesses primarily
            injureds = [injured for injured in injureds if \
                    injured['InjuredPersonType'] and injured["ExtentOfInjuryCode"] and \
                    len(injured['InjuredPersonType'])>0 and len(injured["ExtentOfInjuryCode"])>0 ]

            # save filtered dictionaries to CSV files
            if crashes:
                crash_out = outpath + f'CCRS_crashes_{city}_{year}.csv'
                dumpListDictToCSV(crashes, crash_out, ',',  list(crashes[0].keys()) )
                print(f"\n{len(crashes)} Filtered Crashes saved in {crash_out}")

                party_out = outpath + f'CCRS_parties_{city}_{year}.csv'
                dumpListDictToCSV(parties, party_out, ',',  list(parties[0].keys()) )
                print(f"{len(parties)} Filtered parties saved in {party_out}")

                injured_out = outpath + f'CCRS_injured_{city}_{year}.csv'
                dumpListDictToCSV(injureds, injured_out, ',',  list(injureds[0].keys()) )
                print(f"{len(injureds)} Filtered injuries saved in {injured_out}")

                print(f"Time to fetch and save CCRS data for {city} {year}: {time.perf_counter()-begtime:.4f} sec\n")
            else:
                (f"No CCRS crashes for {city} {year}!!\n")

    print(f"\nTotal time to pull CCRS records for {len(years)} years and {len(search_cities)} cities: {time.perf_counter()-begtime_all:.4f} sec")


# Main body
if __name__ == '__main__':
    main()