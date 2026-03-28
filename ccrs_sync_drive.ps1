# Gemini AI recommended rclone for syncing Windows folder to Google Drive folder
# Install rclone via PowerShell: winget install rclone.rclone
# Configure your Drive: Run rclone config 
#   - follow the prompts to authenticate your Google account (name the remote gdrive)
# Very helpful instructions for setting client_id and client_secret in Google Console
#   - https://rclone.org/drive/#making-your-own-client-id

rclone sync "C:\Users\karl\python\switrs\CCRS" gdrive:CCRS --progress
