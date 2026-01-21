#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from pull_ccrs import get_CCRS_processed
from datetime import datetime
import os

# User variables
path = './CCRS_raw_update_api/'
log_suffix = '_api'
search_prefix = 'CCRS_parties_Carlsbad'
years = ['2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']

# Helper functions -------------------------------------------------------------
def diff_keys(keys_base, keys_compare):
    ndiffs = 0
    log = []

    # find common keys and log any differences
    use_keys, only_base, only_compare = intersect_keys(keys_base, keys_compare)
    if only_base:
        ndiffs += 1
        log.append(f"keys only in base: {only_base}")
    if only_compare:
        ndiffs += 1
        log.append(f"keys only in compare: {only_compare}")

    return use_keys, ndiffs, log

def intersect_keys(ka, kb):
    # convert to sets for intersect and complement
    seta = set(ka)
    setb = set(kb)
    kcommon = list(seta & setb)
    kaonly = ";".join(list(seta-setb))
    kbonly = ";".join(list(setb-seta))

    return kcommon, kaonly, kbonly

# End helper functions ---------------------------------------------------------

def main():

    logger = ['Compare CCRS keys for adjacent years']

    ndiffs_all = 0

    ncompare = len(years) - 1
    compare_years = years[1:]

    for n in range(ncompare):
        base_year = years[n]
        base_files = get_CCRS_processed(path, [f"{search_prefix}_{base_year}"], exclude=['nogeo','huge','poorgeo'])

        compare_year = compare_years[n]
        compare_files = get_CCRS_processed(path, [f"{search_prefix}_{compare_year}"], exclude=['nogeo','huge','poorgeo'])

        for file in base_files:
            logger.append(f"base file: {file}")
            compare_file = file.replace(base_year, compare_year)

            if compare_file in compare_files:
                logger.append(f"compare file: {compare_file}")

                dicts_base, keys_base  = getListDictCsv(file, ',')
                dicts_compare, keys_compare  = getListDictCsv(compare_file, ',')
                common_keys, ndiffs, log = diff_keys(keys_base, keys_compare)

                ndiffs_all += ndiffs
                logger.append(f"# key differences = {ndiffs}")
                logger.extend(log)

            else:
                print(f"No matched compare {file} ... skipping comparison")
                logger.append(f"Cannot find {compare_file}")

    # save logger details in file
    logfile = f"ccrs_compare_keys_years{log_suffix}_{search_prefix}_{datetime.now().strftime('%Y-%m-%d_%H.%M')}.log"

    with open(logfile, "w") as f:
        for line in logger:
            f.write(f"{line}\n")
        f.write(f"Num Differences total = {ndiffs_all}\n")
    f.close()

    print(f"Details in {logfile}")

# Main body
if __name__ == '__main__':
    main()