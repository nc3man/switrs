#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from geocodePelias import geocode_pelias
from geocodeGoogle import geocode_google
from geopy.distance import geodesic
from pull_ccrs import get_CCRS_processed
from max_distances import get_max_distance
import numpy as np
import time
import os

# User variables
geoTest = True  # True means just estimate what needs to be done for Google API costs. False calls Google API $$$
inpath = './CCRS_test/'
outpath = './CCRS_test_updated_geo/'  # not updated if geoTest = True

# bike-ped Unincorporated 3/27/2026
# collision_ids = [493204,452021,1263707,1796550,1207875,1783844,529485,997701,1013643,
#     4938053,592401,984663,529485,1860206]
# still had to repair 592401 (2017) and 1796550 (2022) manually


# Do not edit below this line ----------------------------------------------

# Helper functions ---------------------------------------------------------      

def add_geo_id(crashes, geoTest):
    # if geoTest=True, then only the number of google API geocode calls is printed to estimate cost
    
    # pull out lat, lon if recorded by CCRS
    crashes_update = [crash for crash in crashes if int(crash['CollisionId']) in collision_ids]
    nupdated = len(crashes_update)
    print(f"Updating {nupdated} total")
    
    nogeo = [] # return geolocation failures only
    if geoTest == False:
        
        for crash in crashes_update:
            geocode_google(crash)
            crash['GeoSrc'] = 'Google < CCRS'
            if crash['Latitude']=="NO MATCH":
                nogeo.append(crash['CollisionId'])
       
    return nogeo, nupdated
           
# End helper functions ---------------------------------------------------------

def main():
    
    begtime_all = time.perf_counter()
    geo_files = get_CCRS_processed(inpath, include=[], exclude=[])
    GEOCOUNT = 0
       
    for csvfile in geo_files:
 
        print(f"Updating geo: {csvfile}")
        begtime = time.perf_counter()

        crashes, crash_keys  = getListDictCsv(csvfile, ',')

        nogeo, nupdated = add_geo_id(crashes, geoTest)
        GEOCOUNT += nupdated
           
        # save dictionary with geocoded updates to same-named CSV file in outpath
        out_file = csvfile.replace(inpath, outpath)
        if geoTest == False:
            dumpListDictToCSV(crashes, out_file, ',', crash_keys)
            print(f"{nupdated} geolocations saved in {out_file}")
            if len(nogeo) > 0:
                nogeo_file = out_file.replace('.csv','_nogeo.csv')
                dumpListDictToCSV([crash for crash in crashes if crash['CollisionId'] in nogeo],\
                    nogeo_file, ',',  crash_keys)
                print(f"Collisions with no geo saved in {nogeo_file}")
            print(f"Time to update geolocations: {time.perf_counter()-begtime:.2f} sec\n")
    
    if geoTest:
        print(f"\nTESTING: Total # of new geocodings required = {GEOCOUNT}")
        print(f"\nTotal time to analyze {len(geo_files)} CCRS files: {time.perf_counter()-begtime_all:.4f} sec")
    else:
        print(f"\nTotal # of new geocodings calculated = {GEOCOUNT}")
        print(f"\nTotal time to update {len(geo_files)} CCRS files: {time.perf_counter()-begtime_all:.4f} sec")

   
# Main body
if __name__ == '__main__':
    main()