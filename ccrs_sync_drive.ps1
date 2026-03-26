# Gemini AI recommended rclone for syncing Windows folder to Google Drive folder
# Install rclone via PowerShell: winget install rclone.rclone
# Configure your Drive: Run rclone config 
#   - follow the prompts to authenticate your Google account (name the remote gdrive)
# Very helpful instructions for setting client_id and client_secret in Google Console
#   - https://rclone.org/drive/#making-your-own-client-id

rclone sync "C:\Users\karl\python\switrs\CCRS\CCRS_bike" gdrive:CCRS/CCRS_bike --progress
rclone sync "C:\Users\karl\python\switrs\CCRS\CCRS_bike-ped" gdrive:CCRS/CCRS_bike-ped --progress
rclone sync "C:\Users\karl\python\switrs\CCRS\CCRS_cities_all" gdrive:CCRS/CCRS_cities_all --progress
rclone sync "C:\Users\karl\python\switrs\CCRS\logs" gdrive:CCRS/logs --progress
rclone sync "C:\Users\karl\python\switrs\CCRS" gdrive:CCRS --include "CCRS_*.csv" --progress
rclone sync "C:\Users\karl\python\switrs\CCRS_raw_update_api" gdrive:CCRS/CCRS_raw_update_api --progress
