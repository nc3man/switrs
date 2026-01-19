@echo off
set MAP_PATH="C:\Users\karl\python\switrs"
cd %MAP_PATH%
"C:\Program Files\PowerShell\7\pwsh.exe" -NoExit -File "%MAP_PATH%\run_filter_ccrs_locations.ps1"
