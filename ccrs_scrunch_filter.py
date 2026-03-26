
#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from pull_ccrs import get_CCRS_processed
from operator import itemgetter
from datetime import datetime
import sys
import time
import os

# User variables
FILENAME_SEARCH = ['Encinitas', 'Carlsbad', 'Solana Beach', 'Oceanside', 'Del Mar', '_Vista_', '_San Diego_',
    'Chula Vista','Escondido','Santee','Poway','Lemon Grove','La Mesa','Imperial Beach','El Cajon','Coronado',
    'National City','San Marcos','San Diego Harbor','San Diego State Univ','Uc San Diego','Unincorporated']
inpath = './CCRS/'

search_types = ['bike','bike-ped','cities_all']
output_file_template = 'CCRS_SEARCHTYPE_FILENAME_2016_to_2025-12-31.csv'
output_path_template = './CCRS/CCRS_SEARCHTYPE/'

# Globals
SEARCH_KEYS = ['Motor Vehicle Involved With','Type'] # search only keys containing these strings
BICY_INJURY = ['Bicyclist-Fatal','Bicyclist-SuspectSerious','Bicyclist-SuspectMinor','Bicyclist-PossibleInjury']
PED_INJURY = ['Pedestrian-Fatal','Pedestrian-SuspectSerious','Pedestrian-SuspectMinor','Pedestrian-PossibleInjury']

# Helper  ---------------------------------------------------------

def filter(search_type, crashes, crash_keys, keys_max):
    matched_crashes = []
    
    if search_type == 'cities_all':
        row_search = 'all'
    elif search_type == 'bike-ped':
        row_search = ['bicy','pedestrian']
    elif search_type == 'bike':
        row_search = ['bicy']
    else:
        print(f"Unknown search_type = {search_type}")
        sys.exit()
    
    # only check these keys for row_search substrings
    check_keys = [k for k in crash_keys if any(s in k for s in SEARCH_KEYS)]

    for crash in crashes:
        if search_type == 'cities_all':
            keepRow = True
        else:
            keepRow = False
            for key in check_keys:
                for s in row_search:
                    if s.lower() in crash[key].lower():
                        keepRow = True
                        break
                if keepRow:
                        break
                        
            # check injury table if necessary
            if keepRow == False:
                count_injured = 0
                for inj in BICY_INJURY:
                    count_injured += int(crash[inj])
                if search_type == 'bike-ped':
                    for inj in PED_INJURY:
                        count_injured += int(crash[inj])
                if count_injured > 0:
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
    
    for search_type in search_types:
        outpath = output_path_template.replace('SEARCHTYPE', search_type)
        
        for string in FILENAME_SEARCH:
            found_files = get_CCRS_processed(inpath, [string], exclude=['poorgeo','nogeo','huge','_all_','_bike_','_bike-ped_'])
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
                search_matched_crashes = filter(search_type, crashes, crash_keys, keys_max)
                matched_crashes_all += search_matched_crashes
                
            # not all Party keys may be necessary after filtering    
            used_keys = trim_blank_parties(matched_crashes_all, keys_max, nparty_max)
            
            # sort the search-matched crashes by date
            matched_crashes_sorted = date_sort(matched_crashes_all)
                
            # save scrunched crashes only
            if search_type == 'cities_all':
                out_file = outpath + output_file_template.replace('FILENAME', string).replace('SEARCHTYPE', 'all')
            else:
                out_file = outpath + output_file_template.replace('FILENAME', string).replace('SEARCHTYPE', search_type)
            out_file = out_file.replace('__','_')  # if underscore used to unique filename: eg 'Vista' vs 'Chula Vista', replace '__')
            dumpListDictToCSV(matched_crashes_sorted, out_file, ',', used_keys)
            
            print(f"Scrunched file: {out_file}")
   
# Main body
if __name__ == '__main__':
    main()