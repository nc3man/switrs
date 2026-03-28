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
# inpath = './CCRS/CCRS_bike-ped'
inpath = './test_analysis/'
outpath = './test_analysis/'
summary_file = 'geosummary_test.csv'

# Global
DIST_THRESHOLD = 0  # set > 0 to override get_max_distance

# Helper functions -------------------------------------------------------------

def scanGeo(crashes):
    lat = [crash['Latitude'] for crash in crashes]
    lon = [crash['Longitude'] for crash in crashes]
    ncrashes = len(crashes)

    goodGeo = np.full(ncrashes, False, dtype='bool')
    noGeo   = np.full(ncrashes, False, dtype='bool')
    noMatch = np.full(ncrashes, False, dtype='bool')
    poorGeo = np.full(ncrashes, False, dtype='bool')
    ccrsGeo = np.full(ncrashes, False, dtype='bool')
    googleGeo   = np.full(ncrashes, False, dtype='bool')
    google_ccrsGeo = np.full(ncrashes, False, dtype='bool')
    manualGeo   = np.full(ncrashes, False, dtype='bool')
    peliasGeo   = np.full(ncrashes, False, dtype='bool')
    pelias_ccrsGeo  = np.full(ncrashes, False, dtype='bool')
    google_pelias_ccrsGeo = np.full(ncrashes, False, dtype='bool')

    # put each crash into the correct bin
    for n in range(ncrashes):
        if lat[n]=="" or lon[n]=="":
            noGeo[n] = True
        if lat[n]=="NO MATCH" or lon[n]=="NO MATCH":
            noMatch[n] = True
        if lat[n]=="NO MATCH" or lon[n]=="NO MATCH":
            noMatch[n] = True
        ccrsGeo[n] = (crashes[n]['GeoSrc']=="CCRS")
        googleGeo[n] = (crashes[n]['GeoSrc']=="Google")
        google_ccrsGeo[n] = (crashes[n]['GeoSrc']=="Google < CCRS")
        manualGeo[n] = ('Manual' in crashes[n]['GeoSrc'])
        peliasGeo[n] = (crashes[n]['GeoSrc']=="Pelias")
        pelias_ccrsGeo[n] = (crashes[n]['GeoSrc']=="Pelias < CCRS")
        google_pelias_ccrsGeo[n] = (crashes[n]['GeoSrc']=="Google < Pelias < CCRS")

        goodGeo = np.logical_not(np.logical_or(noGeo,noMatch))

    all_index = np.array(range(ncrashes), dtype=np.int32)
    geo_index = all_index[goodGeo]

    lat_array = np.array([float(lat[n]) for n in geo_index], dtype=float)
    lon_array = np.array([float(lon[n]) for n in geo_index], dtype=float)

    # find median of all the goodGeo (lat,lon)s, avoiding wild errors
    lat_center = np.median(lat_array)
    lon_center = np.median(lon_array)

    # declare any (lat, lon) "poor" if it differs from the center by > max distance threshold
    if DIST_THRESHOLD==0:
        distance_threshold = get_max_distance(crashes[0]['City']) / 2
    else:
        distance_threshold = DIST_THRESHOLD

    for n in geo_index:
        try:
            if geodesic([float(lat[n]), float(lon[n])], [lat_center, lon_center]).mi > distance_threshold:
                poorGeo[n] = True
        except:
            print(f"Really bad latlon = {[float(lat[n]), float(lon[n])]}")
            poorGeo[n] = True

    # revise goodGeo by discarding any poor geolocations found
    goodGeo = np.logical_and(goodGeo, np.logical_not(poorGeo))

    qcGeo = {
        "good":goodGeo,
        "none":noGeo,
        "noMatch":noMatch,
        "poor":poorGeo,
        "ccrs":ccrsGeo,
        "google":googleGeo,
        "google_ccrs":google_ccrsGeo,
        "manual":manualGeo,
        "pelias":peliasGeo,
        "pelias_ccrs":pelias_ccrsGeo,
        "google_pelias_ccrs":google_pelias_ccrsGeo,
        "lat_center": lat_center,
        "lon_center": lon_center
        }
    return qcGeo

# End helper functions ---------------------------------------------------------

def main():

    geo_files = get_CCRS_processed(inpath, include=[], exclude=['poorgeo','nogeo','nomatch','geosummary'])
    summary_list = []
    saved_qc_files = False

    for csvfile in geo_files:

        crashes, crash_keys  = getListDictCsv(csvfile, ',')
        ncrashes = len(crashes)

        # scan crashes to parse crashes into several bins for (lat, lon) "quality"
        qcGeo = scanGeo(crashes)

        ngeo_poorgeo = int(qcGeo['poor'].sum())
        ngeo_ccrs = int(qcGeo['ccrs'].sum())
        ngeo_nogeo = int(qcGeo['none'].sum())
        ngeo_NO_MATCH = int(qcGeo['noMatch'].sum())
        ngeo_google = int(qcGeo['google'].sum())
        ngeo_google_ccrs = int(qcGeo['google_ccrs'].sum())
        ngeo_manual = int(qcGeo['manual'].sum())
        ngeo_pelias = int(qcGeo['pelias'].sum())
        ngeo_pelias_ccrs = int(qcGeo['pelias_ccrs'].sum())
        ngeo_google_pelias_ccrs = int(qcGeo['google_pelias_ccrs'].sum())

        summary = {
            "CCRS file":csvfile,
            "Num Crashes":ncrashes,
            "# to update":ngeo_nogeo + ngeo_poorgeo + ngeo_NO_MATCH,
            "NoGeo":ngeo_nogeo,
            "NoMatch":ngeo_NO_MATCH,
            "PoorGeo":ngeo_poorgeo,
            "CCRS":ngeo_ccrs,
            "Google":ngeo_google,
            "Google < CCRS":ngeo_google_ccrs,
            "Manual":ngeo_manual,
            "Pelias":ngeo_pelias,
            "Pelias < CCRS":ngeo_pelias_ccrs,
            "Google < Pelias < CCRS":ngeo_google_pelias_ccrs,
            "lat_median":float(qcGeo['lat_center']),
            "lon_median":float(qcGeo['lon_center'])
        }

        summary_list.append(summary)

        # save crashes data according to nogeo, noMatch, poor if detected
        crash_array = np.array(crashes)

        if any(qcGeo['none']):
            nogeo_file = csvfile.replace('.csv', '_nogeo.csv')
            dumpListDictToCSV(crash_array[qcGeo['none']], nogeo_file, ',', crash_keys)
            print(f'Crashes with empty geolocation saved in {nogeo_file}')
            saved_qc_files = True
        if any(qcGeo['noMatch']):
            nomatch_file = csvfile.replace('.csv', '_nomatch.csv')
            dumpListDictToCSV(crash_array[qcGeo['noMatch']], nomatch_file, ',', crash_keys)
            print(f'Crashes with NO MATCH saved in {nomatch_file}')
            saved_qc_files = True
        if any(qcGeo['poor']):
            poorgeo_file = csvfile.replace('.csv', '_poorgeo.csv')
            dumpListDictToCSV(crash_array[qcGeo['poor']], poorgeo_file, ',', crash_keys)
            print(f'Crashes with poor geolocation saved in {poorgeo_file}')
            saved_qc_files = True

    # save analyzed dictionary to same-named CSV file in outpath
    out_file = outpath + summary_file
    dumpListDictToCSV(summary_list, out_file, ',', list(summary.keys()))
    print(f"Geocoding summary saved in {out_file}")
    if saved_qc_files:
        print(f"WARNING: qc files saved in input area. Should clean those out for analysis")


# Main body
if __name__ == '__main__':
    main()