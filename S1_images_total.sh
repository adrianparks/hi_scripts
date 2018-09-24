#!/usr/bin/bash

# List the number of S1 images we have on /mnt/ofviti for a particular year and track

if [ $# -ne 2 ]; then
    echo "Usage: $0 <track> <YYYY>"
    echo "Error: Provide the track, and year and month you want to list images for e.g. $0 T118 2018"
    exit 1
fi


track=$1
year=$2

# list all the images we have for a particular year in this track
imgs=$(ls /mnt/ofviti/Sentinel1/img/$track/*.zip | grep -P "S1._IW_SLC__1SDV_$year.*.zip" | awk -F "/" '{print substr($7, 1 ,length($7)-4)}')
numberofimgs=$(echo $imgs | wc -w)
echo $imgs | tr " " "\n"

# echo Found $numberofimgs images for track $track in $year
