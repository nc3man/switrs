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
inpath = './CCRS_geo/'
outpath = './'

# Helper functions ---------------------------------------------------------
def get_CCRS_processed(root_dir):
    file_list = []
    counter = 1
    
    for root, directories, filenames in os.walk(root_dir):
        for filename in filenames:
            if '.csv' in filename and filename.find('nogeo')<0:
                file_list.append(os.path.join(root, filename))
                
    return file_list            

# End helper functions ---------------------------------------------------------

def main():
    
    geo_files = get_CCRS_processed(inpath)
    summary_list = []
    
    for csvfile in geo_files:
 
        crashes, crash_keys  = getListDictCsv(csvfile, ',')
        ncrashes = len(crashes)
        ngeo_ccrs = len([crash for crash in crashes if crash['GeoSrc']=="CCRS"])
        ngeo_pelias = len([crash for crash in crashes if crash['GeoSrc']=="Pelias"])
        ngeo_google = len([crash for crash in crashes if crash['GeoSrc']=="Google"])
        ngeo_pelias_ccrs = len([crash for crash in crashes if crash['GeoSrc']=="Pelias < CCRS"])
        ngeo_google_pelias_ccrs = len([crash for crash in crashes if crash['GeoSrc']=="Google < Pelias < CCRS"])
        
        summary = {
            "CCRS file":csvfile,
            "Num Crashes":ncrashes,
            "CCRS":ngeo_ccrs,
            "Pelias":ngeo_pelias,
            "Google":ngeo_google,
            "Pelias < CCRS":ngeo_pelias_ccrs,
            "Google < Pelias < CCRS":ngeo_google_pelias_ccrs
        }
        
        summary_list.append(summary)
        
    # save analyzed dictionary to same-named CSV file in outpath
    out_file = outpath + 'geo_summary.csv'
    dumpListDictToCSV(summary_list, out_file, ',', list(summary.keys()))
            
   
# Main body
if __name__ == '__main__':
    main()