#!/user/bin/env python3 -tt

# Imports
from dumpDictToCSV import dumpListDictToCSV
from getDataCsv import getListDictCsv
from geocodePelias import geocode_pelias
from geocodeGoogle import geocode_google
from geopy.distance import geodesic
import time
import os

# User variables
inpath = '/home/karl/xps13/python/switrs/CCRS_geo/'
outpath = '/home/karl/xps13/python/switrs/CCRS_pelias_ccrs/'
# update = "ccrs"
# update = "all_to_pelias"
update = "ccrs_to_pelias"
# update = "all_to_google"
# update = "ccrs_to_google"

# Do not edit below this line ----------------------------------------------

# Helper functions ---------------------------------------------------------
def get_CCRS_processed(root_dir):
    file_list = []
    counter = 1
    
    for root, directories, filenames in os.walk(root_dir):
        for filename in filenames:
            if '.csv' in filename and filename.find('nogeo')<0:
                file_list.append(os.path.join(root, filename))
                
    return file_list            

def add_geo(crashes):
    # pull out lat, lon if recorded by CCRS (geolocations from Pelias & Google not wild)
    crash_geos = [crash for crash in crashes if crash['GeoSrc']=='CCRS']
    crash_empty = [crash for crash in crashes if crash['GeoSrc']==""]
        
        
    # Geolocation check: If lat,lon empty, go to Pelias > if poor match, go to Google
    for crash in crash_empty:
        geocode_pelias(crash)
        if crash['Latitude']=="NO MATCH" or float(crash['GeoConf'])<0.95:
            geocode_google(crash)
        
    lats = [crash['Latitude'] for crash in crash_geos]
    lons = [crash['Longitude'] for crash in crash_geos]

    lat_array = np.array([float(lat) for lat in lats], dtype=float)
    lon_array = np.array([float(lon) for lon in lons], dtype=float)

    # find median of all the goodGeo (lat,lon)s, avoiding wild errors
    center = [np.median(lat_array), np.median(lon_array)]
    
    # save collision IDs for any lat,lon more than 70 miles from the center
    poor_geo_crashes = []
    for crash in crash_geos:
        latlon = [float(crash['Latitude']), float(crash['Longitude'])]
        try:
            if geodesic(latlon, center).mi > 70.0:
                poor_geo_crashes.append(crash)
        except:
            print(f"Really bad latlon = {latlon}")
            poor_geo_crashes.append(crash)       

    nogeo = []
    for crash in poor_geo_crashes:
        # first try Pelias, if looks poor use Google
        geocode_pelias(crash)
        crash['GeoSrc'] = 'Pelias < CCRS'
        if crash['Latitude']=="NO MATCH" or float(crash['GeoConf'])<0.8:
            geocode_google(crash)
            crash['GeoSrc'] = 'Google < Pelias < CCRS'
            
        if crash['Latitude']=="NO MATCH":
            nogeo.append(crash['CollisionId'])
        
    return nogeo
    
def update_ccrs_to_pelias(crashes):
    crash_CCRS = [crash for crash in crashes if crash['GeoSrc']=='CCRS']
        
    # Geocode all CCRS geolocations with Pelias
    for crash in crash_CCRS:
        geocode_pelias(crash)
        crash['GeoSrc'] = 'Pelias < CCRS'
        if crash['Latitude']=="NO MATCH":
            nogeo.append(crash['CollisionId'])
        
    return nogeo
    
def update_ccrs_to_google(crashes):
    crash_CCRS = [crash for crash in crashes if crash['GeoSrc'].find('CCRS')>0]
        
    # Geocode all CCRS geolocations with Google Maps API
    for crash in crash_CCRS:
        geocode_google(crash)
        crash['GeoSrc'] = 'Google < CCRS'
        if crash['Latitude']=="NO MATCH":
            nogeo.append(crash['CollisionId'])
        
    return nogeo
   
def update_geo_pelias(crashes):
    # skip collisions already updated with pelias
    update_crashes = [crash for crash in crashes if \
        (crash['GeoSrc']!="Pelias" and crash['GeoSrc']!="Pelias < CCRS")]
 
    for crash in update_crashes:
        # geocode with Pelias
        geocode_pelias(crash)
        if crash['Latitude']=="NO MATCH":
            nogeo.append(crash['CollisionId'])
        
    return nogeo
    
def update_geo_google(crashes):
    # skip collisions already updated with Google Maps API ($)
    update_crashes = [crash for crash in crashes if crash['GeoSrc'].find('Google') < 0]
 
    for crash in update_crashes:
        
        # geocode with Google Maps API
        geocode_pelias(crash)
        if crash['Latitude']=="NO MATCH":
            nogeo.append(crash['CollisionId'])
        
    return nogeo
 
     
# End helper functions ---------------------------------------------------------

def main():
    
    begtime_all = time.perf_counter()
    geo_files = get_CCRS_processed(inpath)
    
    for csvfile in geo_files:
 
        print(f"Updating geo {update}: {csvfile}")
        begtime = time.perf_counter()

        crashes, crash_keys  = getListDictCsv(csvfile, ',')

        if update == "ccrs":
            nogeo = add_geo(crashes)
            
        elif update == "ccrs_to_pelias":
            nogeo = update_ccrs_to_pelias(crashes)
            
        elif update == "ccrs_to_google":
            nogeo = update_ccrs_to_google(crashes)
            
        elif update == "all_to_pelias":
            nogeo = update_geo_pelias(crashes)
            
        elif update == "all_to_google":
            nogeo = update_geo_google(crashes)
            
        # save analyzed dictionary to same-named CSV file in outpath
        out_file = csvfile.replace(inpath, outpath)
        dumpListDictToCSV(analyzed, out_file, ',', crash_keys)
        print(f"\nOutput saved in {out_file}")
        if len(nogeo) > 0:
            nogeo_file = out_file.replace('.csv','_nogeo.csv')
            dumpListDictToCSV([crash for crash in analyzed if crash['CollisionId'] in nogeo],\
                nogeo_file, ',',  crash_keys)
            print(f"Collisions with no geo saved in {nogeo_file}")
        print(f"Time to update {update} geocoding: {time.perf_counter()-begtime:.2f} sec\n")
                
    print(f"\nTotal time to update {update} for {len(geofiles)} CCRS files: {time.perf_counter()-begtime_all:.4f} sec")

   
# Main body
if __name__ == '__main__':
    main()