#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from pull_ccrs import get_CCRS_processed
from datetime import datetime
import os

# User variables
# path_left = './CCRS_new_format/'
# path_right = './CCRS_from_raw_api/'
# # path_right = './CCRS/'
# search_prefix = 'CCRS_Carlsbad'
# compare_type = 'crashes'
# only_check_keys = False
#
# exclude_keys = ['Crash Date-Time', 'CreatedDate', 'ModifiedDate']
# geo_keys = ['Latitude','Longitude','GeoSrc','GeoMatchType','GeoConf','GeoAccuracy','GeoBbox']
# exclude_keys.extend(geo_keys)

path_left = './CCRS_raw_update_csv/'
path_right = './CCRS_raw_update_api/'
search_prefix = 'CCRS_crashes_Carlsbad'
compare_type = 'crashes'
only_check_keys = False

exclude_keys = ['Crash Date Time',
    'CreatedDate', 'ModifiedDate', 'ReviewedDate', 'PreparedDate', 'NotificationDate',
    'Crash Time Description', 'Beat',]

# Helper functions -------------------------------------------------------------
def diff_keys(keys_left, keys_right, exclude_keys):
    ndiffs = 0
    log = []

    # find common keys and log any differences
    use_keys, only_left, only_right = intersect_keys(keys_left, keys_right)
    if only_left:
        ndiffs += 1
        log.append(f"keys only in left: {only_left}")
    if only_right:
        ndiffs += 1
        log.append(f"keys only in right: {only_right}")
    use_keys = list(set(use_keys) - set(exclude_keys))

    return use_keys, ndiffs, log

def diff_ccrs(crashes_left, crashes_right, use_keys, compare_type):
    ndiffs = 0
    log = []

    # depending on compare_type, records need to be aligned by a unique ID
    if compare_type == 'crashes':
        # key='Collision Id' has slightly different format for raw and distilled files
        for key in crashes_left[0].keys():
            if 'Collision' in key:
                unique_key = key
                break
    elif compare_type == 'parties':
        unique_key = 'PartyId'
    elif compare_type == 'injured':
        unique_key = 'InjuredWitPassId'

    for crash in crashes_left:
        primaryID = crash[unique_key]
        crash_right = next((item for item in crashes_right if item[unique_key] == primaryID), None)
        if crash_right==None:
            ndiffs += 1
            log.append(f"ID({compare_type})={primaryID} not found on right")
        else:
            for key in use_keys:
                if (key == 'Latitude') or (key == 'Longitude') or (key == 'MilepostDistance'):
                    if crash[key]:
                        crash[key] = float(crash[key])
                    if crash_right[key]:
                        crash_right[key] = float(crash_right[key])
                if crash_right[key]!=crash[key]:
                    ndiffs += 1
                    log.append(f"diff: ID({compare_type})={primaryID} key={key} vleft={crash[key]}  vright={crash_right[key]}")


    return ndiffs, log

def intersect_keys(ka, kb):
    # convert to sets for intersect and complement
    seta = set(ka)
    setb = set(kb)
    kcommon = list(seta & setb)
    kaonly = "; ".join(list(seta-setb))
    kbonly = "; ".join(list(setb-seta))

    return kcommon, kaonly, kbonly

# End helper functions ---------------------------------------------------------

def main():

    logger = ['Compare two folders of CCRS files']
    logger.append(f"left:  {path_left}")
    logger.append(f"right: {path_right}")

    ndiffs_all = 0

    left_files = get_CCRS_processed(path_left, [search_prefix], exclude=['2015','nogeo','huge','poorgeo'])

    for file in left_files:
        logger.append(f"left: {file}")

        crashes_left, keys_left  = getListDictCsv(file, ',')

        right_file = file.replace(path_left, path_right)

        if os.path.exists(right_file):

            crashes_right, keys_right  = getListDictCsv(right_file, ',')
            use_keys, ndiffs_keys, log_keys = diff_keys(keys_left, keys_right, exclude_keys)

            if only_check_keys:
                ndiffs = 0
                log = []
            else:
                ndiffs, log = diff_ccrs(crashes_left, crashes_right, use_keys, compare_type)

            if ndiffs + ndiffs_keys == 0:
                logger.append('EQUAL')
            else:
                ndiffs_all += ndiffs + ndiffs_keys
                logger.append(f"ndiffs = {ndiffs + ndiffs_keys}")
                logger.extend(log_keys)
                logger.extend(log)

        else:
            print(f"No matched right {file} ... skipping comparison")
            logger.append(f"right: no match")

    # save logger details in file
    logfile = f"ccrs_compare_{search_prefix}_{datetime.now().strftime('%Y-%m-%d_%H.%M')}.log"
    if only_check_keys:
        logfile = logfile.replace('ccrs_compare_', 'ccrs_compare_keys_')

    with open(logfile, "w") as f:
        for line in logger:
            f.write(f"{line}\n")
        f.write(f"Num Differences = {ndiffs_all}\n")
    f.close()

    print(f"Details in {logfile}")

# Main body
if __name__ == '__main__':
    main()