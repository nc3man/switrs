# switrs
python source for distilling SWITRS and CCRS raw data

## Steps to Create Processed CCRS Files

| Script Name  | Function |
| --- | --- |
| ccrs_filter.py | Filters raw CSV files into manageable files by city and year |
| ccrs_distill.py | Distills output of ccrs_filter into csv file with one record per CollisionId |
| copy_geo_collisionID.py | Copies previous updated geolocations into the output of ccrs_distill |
| update_geo.py | For remaining missing or bad geolocations, update with Google Geolocation API |
| update_geo.py | For remaining missing or bad geolocations, update with Google Geolocation API |
| filter_ccrs_locations.py | For processed CCRS files, display crashes on a map, optionally selecting subset with mouse |

## Helper Function Source
| Source  | Description |
| --- | --- |
| getDataCsv.py | Pulls csv file into python structures |
| dumpDictToCSV.py | Dumps python structures to csv file |
| pull_ccrs.py | Traverses directory tree searching for requested CCRS files |
| geocodeGoogle.py | Calls Google Geolocation API to get (lat,lon) of crash |
| inpoly.py | Test if (lat,lon) point on map is in a closed (latitude,longitud) curve |
| createCrashPlacemarks.py | Creates a placemark for each crash to display on a map |

## Notes
Scripts have editable data at top to specify input/output locations and parameters.

For a windows environment, recommend using the pyzo IDE, for ease in editing prior to running.

To run filter_ccrs_locations.py see run_filter_ccrs_locations.ps1 to ensure a local http server is running.