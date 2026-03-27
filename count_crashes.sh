#!/bin/bash
cd ./CCRS/CCRS_cities_all

for file in *; do
    # Check if it's actually a file (not a directory)
    if [ -f "$file" ]; then
        word_count=`wc -l "$file"`
        line_count="${word_count%% *}"
        crash_count=$((line_count - 1))
        city=$(echo "$file" | cut -d'_' -f3)
        echo $city", "$crash_count
    fi
done