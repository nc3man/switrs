#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from ccrs_resource_IDs import CCRS_resource_IDs

# User variables
years = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
search_cities = ['Del Mar', 'Solana Beach', 'Encinitas', 'Carlsbad', 'Vista', 'Oceanside']

path_api = './CCRS_raw_update_api/'
path_dnld = './CCRS_raw_update_csv/'

CCRS_TEMPLATE = 'CCRS_crashes_CITY_YEAR.csv'
DNLD_TEMPLATE = 'hq1d-p-app52dopendataexportYEARcrashes.csv'

def main():

    summary_list = []
    for year in years:
        for city in search_cities:

            api_file = f"{path_api}{CCRS_TEMPLATE.replace('CITY',city).replace('YEAR',year)}"
            dnld_file = api_file.replace(path_api,path_dnld)

            crashes_resource, parties_resource, injuries_resource = CCRS_resource_IDs(year)

            crashes_api, crash_keys_api = getListDictCsv(api_file, ',')
            crashes_dnld, crash_keys_dnld = getListDictCsv(dnld_file, ',')
            if crash_keys_api != crash_keys_dnld:
                print(f"CRAP! something seriously wrong with {CCRS_TEMPLATE.replace('CITY',city).replace('YEAR',year)}")
                exit()

            summary = {
                "Search [City Name][Year]":f"[{city}][{year}]",
                "#Collisions API":len(crashes_api),
                "#Collisions Download":len(crashes_dnld),
                "API Resource":crashes_resource,
                "Download Source": DNLD_TEMPLATE.replace('YEAR',year)
            }

            summary_list.append(summary)

    # save analyzed dictionary to same-named CSV file in outpath
    out_file = path_api + 'api_counts_summary.csv'
    dumpListDictToCSV(summary_list, out_file, ',', list(summary.keys()))


# Main body
if __name__ == '__main__':
    main()