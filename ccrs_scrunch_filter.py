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
cities = ['Encinitas', 'Carlsbad', 'Solana Beach', 'Oceanside', 'Del Mar', 'Vista']
search = ['bicy']  # keep crashes where ANY field matches a string in the search list

output_file_template = 'CCRS_bike_CITY_2015_to_2025-06-02.csv'
inpath = './CCRS_geo/'
outpath = './CCRS_bike/'

# Helper  ---------------------------------------------------------

def filter(row_search, crashes, crash_keys, nparty_max, keys_max):
    matched_crashes = []
    for crash in crashes:
        keepRow = False
        for key in crash_keys:
            for s in row_search:
                if s.lower() in crash[key].lower():
                    keepRow = True
        
        if keepRow:
            # fill in blanks for all keys between last party key and keys_max
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
    
    # remove unnecessary key-value pair from the dictionary list, in memory
    for crash in crashes:
        for key in removed_keys:
            del crash[key]
                        
    return keys
    
def date_sort(crashes):
    # need to do a time value sort, not a char sort on time string, so add a tmp key
    crashes_time = crashes
    for crash in crashes_time:
        date_value = datetime.strptime(crash['Date-Time'], '%m/%d/%Y %I:%M:%S %p')
        crash.update({'date_time':date_value})
        
    # sort on the temporary key - then delete it
    crash_sorted = sorted(crashes_time, key=itemgetter('date_time'))
    for crash in crash_sorted:
        del crash['date_time']
    
    return crash_sorted

# End helper functions ---------------------------------------------------------

def main():
    
    for city in cities:
        geo_files = get_CCRS_processed(inpath, [city], exclude=['nogeo','huge'])
        bikeRelated_all = []
 
        # first, need header to cover max # of parties
        nparty_max = 0
        for csvfile in geo_files:
            crashes, crash_keys  = getListDictCsv(csvfile, ',')
            for crash in crashes:
                if int(crash['Num Parties']) > nparty_max:
                    nparty_max = int(crash['Num Parties'])
                    keys_max = crash_keys

        for csvfile in geo_files:
            crashes, crash_keys  = getListDictCsv(csvfile, ',')
            bike_related_crashes = filter(search, crashes, crash_keys, nparty_max, keys_max)
            bikeRelated_all += bike_related_crashes
            
        # not all Party keys may be necessary after filtering    
        used_keys = trim_blank_parties(bikeRelated_all, keys_max, nparty_max)
        
        # sort the bike-related crashes by date
        bikeRelated_sorted = date_sort(bikeRelated_all)
            
        # save scrunched crashes only
        out_file = outpath + output_file_template.replace('CITY', city)
        dumpListDictToCSV(bikeRelated_sorted, out_file, ',', used_keys)
   
# Main body
if __name__ == '__main__':
    main()