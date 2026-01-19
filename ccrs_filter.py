#!/user/bin/env python3 -tt

# Imports
from collections import defaultdict
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
import time

# User variables
# years = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025',]
# search_cities = ['Encinitas', 'Carlsbad', 'Solana Beach', 'Oceanside', 'Del Mar', 'Vista']
years = ['2015']
search_cities = ['San Diego']

inpath = 'C:/Users/karl/python/switrs/CCRS_raw/'
outpath = 'C:/Users/karl/python/switrs/CCRS_raw_update_csv/'

# Do not edit below this line --------------------------------------------------

def run_filters(city_search,year, crashes_all, parties_all, injureds_all, crash_keys, party_keys, injured_keys):

    # while large datasets for a single year are in memory, run through each city

    for city in city_search:
        print(f"\nTrimming full CCRS raw data for {year} and {city}")
        begtime = time.perf_counter()

        # filter crashes based on City Name
        crashes = [crash for crash in crashes_all if crash["City Name"]==city]
        # remove crashes not in API search: NCIC=3700 ???
        # crashes = [crash for crash in crashes if crash["NCIC Code"]!="3700"]
        collision_ids = [crash["Collision Id"] for crash in crashes]
        print(f"\nTime to filter {city} crashes: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        # now filter parties based on matched "CollisionId"
        parties = [party for party in parties_all if party["CollisionId"] in collision_ids]
        print(f"Time to trim parties by {city} crash[CollisionID]s: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        # then filter injureds based on matched "Collision_Id"
        injureds = [injured for injured in injureds_all if ( (injured["CollisionId"] in collision_ids) and \
                    (len(injured['InjuredPersonType'])>0) and (len(injured["ExtentOfInjuryCode"])>0) )]
        print(f"Time to trim injureds to {city} crash[CollisionID]s: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        # save filtered dictionaries to CSV files
        out_file_suffix = f'{city}_{year}.csv'

        crash_out = outpath + 'CCRS_crashes_' + out_file_suffix
        dumpListDictToCSV(crashes, crash_out, ',',  crash_keys)  # , encoding='cp850'
        print(f"\n{len(crashes)} Filtered Crashes saved in {crash_out}")

        party_out = outpath + 'CCRS_parties_' + out_file_suffix
        dumpListDictToCSV(parties, party_out, ',',  party_keys) # , encoding='cp850'
        print(f"{len(parties)} Filtered parties saved in {party_out}")

        injured_out = outpath + 'CCRS_injured_' + out_file_suffix
        dumpListDictToCSV(injureds, injured_out, ',',  injured_keys) # , encoding='cp850'
        print(f"{len(injureds)} Filtered injureds saved in {injured_out}")

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
        crashes, crash_keys  = getListDictCsv(crashes_file, ',') # , encoding = 'cp850'
        print(f"\nTime to load all crashes: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        parties, party_keys  = getListDictCsv(parties_file, ',') # , encoding = 'cp850'
        print(f"Time to load all parties: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        injureds, injured_keys = getListDictCsv(injureds_file, ',') # , encoding = 'cp850'
        print(f"Time to load all injuries: {time.perf_counter()-begtime:.4f} sec")
        begtime = time.perf_counter()

        run_filters(search_cities, year, crashes, parties, injureds, crash_keys, party_keys, injured_keys)

    print(f"\nTotal time to pull CCRS records for {len(years)} years and {len(search_cities)} cities: {time.perf_counter()-begtime_all:.4f} sec")

# Main body
if __name__ == '__main__':
    main()