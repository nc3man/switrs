#!/user/bin/env python3 -tt

# Imports
import sys
from getDataCsv import getDataCsv
from dumpDictToCSV import dumpListDictToCSV
from inpoly import inpoly
import numpy as np
from createCrashPlacemarks import createCrashPlacemarks
from PyQt5.QtWidgets import QApplication, QFileDialog
from collision_filter_map import select_polygon_map
from geopy.distance import geodesic

# Helper functions
def select_file():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select a CCRS csv file",
        "",
        "All Files (*);;CSV Files (*.csv)",
        options=options
    )
    return file_path

def scanGeo(crashes):
    # categorize lat,lon data per crash as good, non-existent, poor
    # poor is lat or lon differing by > 1.0 deg (~70 miles) from
    #    the median of all "goodGeo" data
    lat = [crash['Latitude'] for crash in crashes]
    lon = [crash['Longitude'] for crash in crashes]
    ncrashes = len(crashes)

    goodGeo = np.full(ncrashes, False, dtype='bool')
    noGeo   = np.full(ncrashes, False, dtype='bool')
    poorGeo = np.full(ncrashes, False, dtype='bool')

    # first find all non-nil (lat,lon)
    for n in range(ncrashes):
        if lat[n]=="NO MATCH" or lon[n]=="NO MATCH":
            noGeo[n] = True

    goodGeo = np.logical_not(noGeo)

    all_index = np.array(range(ncrashes), dtype=np.int32)
    geo_index = all_index[goodGeo]

    lat_array = np.array([float(lat[n]) for n in geo_index], dtype=float)
    lon_array = np.array([float(lon[n]) for n in geo_index], dtype=float)

    # find median of all the goodGeo (lat,lon)s, avoiding wild errors
    lat_center = np.median(lat_array)
    lon_center = np.median(lon_array)

    # declare any (lat, lon) "poor" if it differs from the center by > 70 miles
    for n in geo_index:
        try:
            if geodesic([float(lat[n]), float(lon[n])], [lat_center, lon_center]).mi > 70.0:
                poorGeo[n] = True
        except:
            print(f"Really bad latlon = {[float(lat[n]), float(lon[n])]}")
            poorGeo[n] = True

    # revise goodGeo by discarding any poor geolocations found
    goodGeo = np.logical_and(goodGeo, np.logical_not(poorGeo))

    qcGeo = {"good":goodGeo, "none":noGeo, "poor":poorGeo, "lat_center": lat_center, "lon_center": lon_center}
    return qcGeo

def edit_map_html(lat_center, lon_center):
    # center displayed map on the data for this set of crashes
    with open('map_template.html', 'r') as finput:
        lines = ''
        line = finput.readline()
        while line:
            lines += line
            line = finput.readline()

    # replace LAT_CENTER and LON_CENTER placeholders in template with computed values
    lines_out = lines.replace("LAT_CENTER", str(lat_center))
    lines_out = lines_out.replace("LON_CENTER", str(lon_center))
    foutput = open('map.html', 'w')
    foutput.write(lines_out)
    foutput.close()

def find_crashes_inside_polygon(crashes, coords):
    # set up polygon verices as numpy arrays
    xpoly = np.array([float(coord["lat"]) for coord in coords])
    ypoly = np.array([float(coord["lng"]) for coord in coords])

    # set up all (x,y) coordinates for (lat,lon) in crashes
    xtest = np.array([float(crash['Latitude']) for crash in crashes])
    ytest = np.array([float(crash['Longitude']) for crash in crashes])

    # Test all points at once for interior of polygon
    inside = inpoly( xtest, ytest, xpoly, ypoly )

    collision_ids = np.array([crash["CollisionId"] for crash in crashes])
    keep_CollisionIds = collision_ids[inside]

    return keep_CollisionIds

def main():
    # Load select CCRS csv file
    ccrs_csv = select_file()
    crashes, crash_keys = getDataCsv( ccrs_csv, ',', pivot=True)

    qcGeo = scanGeo(crashes)
    crash_array = np.array(crashes)
    geo_crashes = crash_array[qcGeo['good']]

    createCrashPlacemarks( geo_crashes, 'crash_placemarks.kml' )

    # display crash map and optionally select a subset
    edit_map_html(qcGeo['lat_center'], qcGeo['lon_center'])
    coords = select_polygon_map()

    # determine which crashes are inside the drawn polygon and save in csv
    if coords:
        keep_CollisionIds = find_crashes_inside_polygon(geo_crashes, coords)
        if len(keep_CollisionIds)>0:
            crashes_filtered = [crash for crash in crashes if crash['CollisionId'] in keep_CollisionIds]
            ccrs_filtered = ccrs_csv.replace('.csv', '_filtered.csv')
            dumpListDictToCSV(crashes_filtered, ccrs_filtered, ',', crash_keys)
            print(f'Crashes within the polygon area are saved in {ccrs_filtered}')
    # Original saved files below not needed as the geocoding functions take care of this.
    # Dump out separate CSV files for no geo and poor geo conditions for manual evaluation
    # if any(qcGeo['none']):
    #     ccrs_nogeo_file = ccrs_csv.replace('.csv', '_nogeo.csv')
    #     dumpListDictToCSV(crash_array[qcGeo['none']], ccrs_nogeo_file, ',', crash_keys)
    #     print(f'Crashes without geolocation saved in {ccrs_nogeo_file}')
    # if any(qcGeo['poor']):
    #     print(f"Still found {len([qc for qc in qcGeo if qc['poor']==True])}")

# Main body
if __name__ == '__main__':
    main()