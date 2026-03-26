# Runs all scripts in order for the last 2 provisional years, all 22 SD City Codes

# run from switrs/ root for all scripts and local data storage
cd C:\Users\karl\python\switrs

# Initialization Step: clean out target output directories
Remove-Item -Path ".\CCRS_raw_update_api\CCRS_*.csv" -Force
Remove-Item -Path ".\CCRS_from_raw_api\CCRS_*.csv" -Force
Remove-Item -Path ".\CCRS_copied_geo\CCRS_*.csv" -Force

# Step 1: query CCRS database for raw data for provisional years only (~4 minutes)
# run ccrs_filter_api --> ./CCRS_raw_update_api
# copy ./CCRS_raw_update_api to ./CCRS/CCRS_raw_update_api
python -m ccrs_filter_api
Copy-Item -Path ".\CCRS_raw_update_api\CCRS_*.csv" -Destination ".\CCRS\CCRS_raw_update_api\"

# Step 2: distill raw data into CCRS analysis files, 1 row per CollisionId (~2 minutes)
# on ./CCRS_raw_update_api run ccrs_distill --> ./CCRS_from_raw_api
# copy ./CCRS_from_raw_api to ./CCRS including any logs/ warnings
python -m ccrs_distill
Copy-Item -Path ".\CCRS_from_raw_api\CCRS_*.csv" -Destination ".\CCRS\"
Copy-Item -Path ".\CCRS_from_raw_api\logs\warnings_*.log" -Destination ".\CCRS\logs\"

# Step 3: copy previously added geolocations to newly distilled CCRS files 
# on ./CCRS_from_raw_api run copy_geo_CollisionID --> ./CCRS_copied_geo
# copy ./CCRS_copied_geo to ./CCRS
python -m copy_geo_collisionID
Copy-Item -Path ".\CCRS_copied_geo\CCRS_*.csv" -Destination ".\CCRS\"

# Step 4: Concatenate and filter all files to update CCRS_[bike,bike-ped,cities_all]
# on ./CCRS run ccrs_scrunch_filter on search_types = [bike,bike-ped,cities_all]
python -m ccrs_scrunch_filter

# Step 5: Sync all locally updated data to shared Google Drive
.\ccrs_sync_drive.ps1 # only uploads newer files

# Later: run update_geo with geoTest=True to see how much needs to geolocated
# Assess output at CCRS/CCRS_bike-ped and CCRS/CCRS_cities_all to decide on what to run with geoTest=False
# If we run update_geo with geoTest=False, copy ./CCRS_updated_geo to ./CCRS and rerun Steps 4 and 5

