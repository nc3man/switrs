
#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from pull_ccrs import get_CCRS_processed
from operator import itemgetter
from datetime import datetime
import time
import os

# User variables
FILENAME_SEARCH = ['Encinitas', 'Carlsbad', 'Solana Beach', 'Oceanside', 'Del Mar', 'Vista', 'San Diego']
inpath = './CCRS_new_format/'

search = ['bicy']
output_file_template = 'CCRS_bike_FILENAME_2015_to_2025-12-31.csv'
outpath = './CCRS/CCRS_bike/'

# search = ['bicy','pedestrian']
# output_file_template = 'CCRS_bike-ped_FILENAME_2015_to_2025-12-31.csv'
# outpath = './CCRS/CCRS_bike-ped/'

# search = ['all']
# output_file_template = 'CCRS_all_FILENAME_2015_to_2025-12-31.csv'
# outpath = './CCRS/CCRS_cities_all/'

# FILENAME_SEARCH = ['bike']
# search = ['bicy']  # keep crashes where ANY field matches a string in the search list
# google-fixed geos
# search = [
#     3527695,
#     3539815,
#     3544675,
#     3556063,
#     3175147,
#     2925405,
#     2969742,
#     30616,
#     30633,
#     3602755,
#     3595607,
#     3623379,
#     3725593,
#     3702093,
#     3740411,
#     3707401,
#     3751878,
#     3754691,
#     3747963,
#     3758398,
#     748703,
#     3078441,
#     81381
# ]
# search = [str(s) for s in search]
# pelias-fixed geos
# search = [
#     2893930,
#     3566002,
#     3582257,
#     3661133,
#     3696689,
#     3726301,
#     3757786,
#     3753531,
#     3076266,
#     3087900,
#     3106713,
# ]
# search = [str(s) for s in search]

# Helper  ---------------------------------------------------------

def filter(row_search, crashes, crash_keys, keys_max):
    matched_crashes = []

    for crash in crashes:
        keepRow = False
        for key in crash_keys:
            # exclude 'Pedestrian Action' column (almost always has string 'PEDESTRIAN')
            if key == 'Pedestrian Action':
                continue
            for s in row_search:
                if s.lower() in crash[key].lower() or s=='all':
                    keepRow = True
        
        if keepRow:
            # fill in blanks for all keys between last party key and end of keys_max
            last_key = crash_keys[-1]
            extend = {k:"" for k in keys_max[keys_max.index(last_key)+1:]}
            crash.update(extend)           
            matched_crashes.append(crash)
            
    return matched_crashes
    
def trim_blank_parties(crashes, keys, nparty_max):
    
    removed_keys = []

    for n in range(nparty_max, 1, -1):
        prefix = f"P{n}"
        ptype_key = f"{prefix} Party"
        values = [crash[f"{prefix} Party"] for crash in crashes]
        if all(v=="" for v in values):
            to_remove = [k for k in keys if prefix in k]
            for key in to_remove:
                keys.remove(key)
            removed_keys += to_remove
        else:
            break
    
    # remove unnecessary key-value pairs from the dictionary list, in memory
    for crash in crashes:
        for key in removed_keys:
            del crash[key]
                        
    return keys
    
def date_sort(crashes):
    # need to do a date-time value sort, not a char sort on date-time string, so add a tmp key
    crashes_time = crashes
    for crash in crashes_time:
        try:
            date_value = datetime.strptime(crash['Crash Date-Time'], '%m/%d/%Y %I:%M:%S %p')
        except:
            date_value = datetime.strptime(crash['Crash Date-Time'], '%m/%d/%Y %H:%M')

        crash.update({'date_time':date_value})
        
    # sort on the temporary key - then delete it
    crash_sorted = sorted(crashes_time, key=itemgetter('date_time'))
    for crash in crash_sorted:
        del crash['date_time']
    
    return crash_sorted

# End helper functions ---------------------------------------------------------

def main():
    
    for string in FILENAME_SEARCH:
        found_files = get_CCRS_processed(inpath, [string], exclude=['poorgeo','nogeo','huge','all','_bike_','_bike-ped_'])
        matched_crashes_all = []
 
        # first, need header to cover max # of parties
        nparty_max = 0
        for csvfile in found_files:
            crashes, crash_keys  = getListDictCsv(csvfile, ',')
            for crash in crashes:
                if int(crash['Num Parties']) > nparty_max:
                    nparty_max = int(crash['Num Parties'])
                    keys_max = crash_keys

        for csvfile in found_files:
            crashes, crash_keys  = getListDictCsv(csvfile, ',')
            search_matched_crashes = filter(search, crashes, crash_keys, keys_max)
            matched_crashes_all += search_matched_crashes
            
        # not all Party keys may be necessary after filtering    
        used_keys = trim_blank_parties(matched_crashes_all, keys_max, nparty_max)
        
        # sort the search-matched crashes by date
        matched_crashes_sorted = date_sort(matched_crashes_all)
            
        # save scrunched crashes only
        out_file = outpath + output_file_template.replace('FILENAME', string)
        dumpListDictToCSV(matched_crashes_sorted, out_file, ',', used_keys)
   
# Main body
if __name__ == '__main__':
    main()