#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from pull_ccrs import get_CCRS_processed
import os

# User variables

path_geo = './CCRS/CCRS_cities_all/'
path_to_update = './CCRS_new_format/'
path_updated = './CCRS_copied_geo/'

# Helper functions -------------------------------------------------------------
def copy_geo(update_geo, crash):
    geo_keys = ['Latitude','Longitude','GeoSrc','GeoMatchType','GeoConf','GeoAccuracy','GeoBbox']

    # copy previous geo update for this crash
    for key in geo_keys:
        crash[key] = update_geo[key]

    return None # immutable, crash is modified in place

def added_geo_collisionIds(geo_files):
    geo_added = dict()
    for file in geo_files:
        crashes, crash_keys  = getListDictCsv(file, ',')
        for crash in crashes:
            if crash['GeoSrc']!='CCRS' and crash['GeoSrc']!='':
                geo_added[crash['CollisionId']] = {
                    'Latitude':crash['Latitude'],
                    'Longitude':crash['Longitude'],
                    'GeoSrc':crash['GeoSrc'],
                    'GeoMatchType':crash['GeoMatchType'],
                    'GeoConf':crash['GeoConf'],
                    'GeoAccuracy':crash['GeoAccuracy'],
                    'GeoBbox':crash['GeoBbox']
                   }

    return geo_added

# End helper functons ---------------------------------------------------------

def main():

    update_files = get_CCRS_processed(path_to_update, ['CCRS'], exclude=['nogeo','huge','poorgeo'])
    geo_files = get_CCRS_processed(path_geo, ['CCRS'], exclude=['nogeo','huge','poorgeo'])

    # first get all CollisionIds that have updated geolocation
    geo_updated = added_geo_collisionIds(geo_files)
    geo_updated_collisionIds = geo_updated.keys()

    for file in update_files:
        crashes, crash_keys  = getListDictCsv(file, ',')
        ncopy = 0

        for crash in crashes:
            if crash['CollisionId'] in geo_updated_collisionIds:
                crash = copy_geo(geo_updated[crash['CollisionId']], crash)
                ncopy += 1

        if ncopy > 0:
            # save updated crashes
            out_file = file.replace(path_to_update, path_updated)
            dumpListDictToCSV(crashes, out_file, ',', crash_keys)
            print(f"\nAdded geo to {ncopy} crashes")
            print(f"Updated in {out_file}")

# Main body
if __name__ == '__main__':
    main()