#!/user/bin/env python3 -tt

# Imports
from collections import defaultdict
from dumpDictToCSV import dumpDictToCSV
from getDataCsv import getDataCsv
import time
import sys

# User variables
years = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025',]
search_cities = ['Encinitas', 'Carlsbad', 'Solana Beach', 'Oceanside', 'Del Mar']
inpath = 'C:/Users/karl/python/switrs/CCRS/'

# Do not edit below this line --------------------------------------------------

# Helper functions

def get_crashes(crashes, crash_keys, city_name):
    crashes_trim = defaultdict(list)
    collision_ids = []
    ncrashes = len(crashes['Collision Id'])

    # trim large dataset down to desired city
    for n in range(ncrashes):
        if crashes["City Name"][n] == city_name:
            collision_ids.append(crashes['Collision Id'][n])
            for key in crash_keys:
                crashes_trim[key].append(crashes[key][n])

    return crashes_trim, collision_ids

def get_parties(parties, party_keys, collision_ids):
    parties_trim = defaultdict(list)
    nparties = len(parties['CollisionId'])

    # trim large dataset down to those with matching CollisionID
    for n in range(nparties):
        if parties["CollisionId"][n] in collision_ids:
            for key in party_keys:
                parties_trim[key].append(parties[key][n])

    return parties_trim

def get_injureds(injureds, injured_keys, collision_ids):
    injureds_trim = defaultdict(list)
    ninjureds = len(injureds['CollisionId'])

    # trim large dataset down to those with matching CollisionID and with injuries
    for n in range(ninjureds):
        if injureds["CollisionId"][n] in collision_ids:
            if len(injureds['InjuredPersonType'][n])>0 and len(injureds["ExtentOfInjuryCode"][n])>0:
                for key in injured_keys:
                    injureds_trim[key].append(injureds[key][n])

    return injureds_trim

# End helper functions ---------------------------------------------------------

def run_filters(city_search,year, crashes_year,parties_year,injureds_year,crash_keys,party_keys,injured_keys):

    # while large datasets for a single year are in memory, run through each city

    for city in city_search:
        print(f"\nTrimming full CCRS raw data for {year} and {city}")
        begtime = time.perf_counter()

        # filter crashes based on City Name
        crashes, collision_ids = get_crashes(crashes_year, crash_keys, city)
        print(f"\nTime to filter {city} crashes: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        # now filter parties based on matched collision_ids
        parties = get_parties(parties_year, party_keys, collision_ids)
        print(f"Time to trim parties by {city} crash[CollisionID]s: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        # now filter injureds based on matched collision_ids
        injureds = get_injureds(injureds_year, injured_keys, collision_ids)
        print(f"Time to trim injureds to {city} crash[CollisionID]s: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        # save filtered dictionaries to CSV files
        out_file_suffix = f'{city}_' + year + '.csv'

        crash_out = inpath + 'CCRS_crashes_' + out_file_suffix
        dumpDictToCSV(crashes, crash_out, ',',  crash_keys, encoding='cp850')
        print(f"\n{len(crashes['Collision Id'])} Filtered Crashes saved in {crash_out}")

        party_out = inpath + 'CCRS_parties_' + out_file_suffix
        dumpDictToCSV(parties, party_out, ',',  party_keys, encoding='cp850')
        print(f"{len(parties['CollisionId'])} Filtered parties saved in {party_out}")

        injured_out = inpath + 'CCRS_injured_' + out_file_suffix
        dumpDictToCSV(injureds, injured_out, ',',  injured_keys, encoding='cp850')
        print(f"{len(injureds['CollisionId'])} Filtered injureds saved in {injured_out}")

        print(f"Time to save filtered data: {time.perf_counter()-begtime:.4f} sec")

def main():

    begtime_all = time.perf_counter()

    for year in years:
        print(f"\nLoading full CCRS raw data for {year}")
        begtime = time.perf_counter()

        crashes_file = inpath + 'hq1d-p-app52dopendataexport' + year + 'crashes.csv'
        parties_file = inpath + 'hq1d-p-app52dopendataexport' + year + 'parties.csv'
        injureds_file = inpath + 'hq1d-p-app52dopendataexport' + year + 'injuredwitnesspassengers.csv'

        # read data from CCRS raw data files
        begtime = time.perf_counter()
        crashes, crash_keys  = getDataCsv(crashes_file, ',', encoding = 'cp850')
        print(f"\nTime to load all crashes: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        parties, party_keys  = getDataCsv(parties_file, ',', encoding = 'cp850')
        print(f"Time to load all parties: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        injureds, injured_keys = getDataCsv(injureds_file, ',', encoding = 'cp850')
        print(f"Time to load all injuries: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        run_filters(search_cities, year, crashes, parties, injureds, crash_keys, party_keys, injured_keys)

    print(f"\nTotal time to distill all {len(years)*len(search_cities)} years & cities: {time.perf_counter()-begtime_all:.4f} sec")

# Main body
if __name__ == '__main__':
    main()