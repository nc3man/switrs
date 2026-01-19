#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from pull_ccrs import get_CCRS_processed
import os

# User variables
path_geo = './CCRS_test_updated_geo/'
path_to_update = './CCRS_test/'
path_updated = './CCRS_test/'
string_search = ['San Diego'] # in case path_geo files don't match update_files, use all crashes in geo_files matching strings

# path_geo = './CCRS/'
# path_to_update = './CCRS_new_format/'
# path_updated = './CCRS_new_format/'

# Helper functions -------------------------------------------------------------
def copy_geo(crashes, crashes_geo, geo_keys):
    # update crash records if a CollisionID match occurs in crashes_geo
    for crash in crashes:
        crash_geo = None
        for cr in crashes_geo:
            if cr['CollisionId']==crash['CollisionId']:
                crash_geo = cr
                break
        if crash_geo:
            for key in geo_keys:
                crash[key] = crash_geo[key]

    return None # crashes has been modified in place (mutable)


# End helper functions ---------------------------------------------------------

def main():

    update_files = get_CCRS_processed(path_to_update, ['CCRS'], exclude=['nogeo','huge','poorgeo'])
    geo_files = get_CCRS_processed(path_geo, ['CCRS'], exclude=['nogeo','huge','poorgeo'])

    geo_keys = ['Latitude','Longitude','GeoSrc','GeoMatchType','GeoConf','GeoAccuracy','GeoBbox']


    for file in update_files:
        matched_geo_file = file.replace(path_to_update, path_geo)
        crashes, crash_keys  = getListDictCsv(file, ',')

        if os.path.exists(matched_geo_file):

            crashes_geo, crash_keys_geo  = getListDictCsv(matched_geo_file, ',')
            copy_geo(crashes, crashes_geo, geo_keys)
            print(f"Updated geocoding for {file}")

        else:
            # first, build crashes_geo by concatenating all string_search matches' crash dicts
            crashes_geo = []
            for s in string_search:
                for fname in geo_files:
                    if s in fname:
                        load_geo, keys = getListDictCsv(fname, ',')
                        crashes_geo += load_geo

            if len(crashes_geo) > 0:
                copy_geo(crashes, crashes_geo, geo_keys)
                print(f"Updated geocoding for {file}")

            else:
                print(f"No matched geo {file} ... will just copy as is")

        # save updated crashes (or copy if not updated)
        out_file = file.replace(path_to_update, path_updated)
        dumpListDictToCSV(crashes, out_file, ',', crash_keys)

# Main body
if __name__ == '__main__':
    main()