#!/usr/bin/bash

# S1_validate_data.sh <track> <year>

# Compare the list of images on the Copernicus Open Access Hub to what we
# have on /mnt/ofviti and list out what is missing

if [ $# -ne 2 ]; then
    echo "Usage: $0 <track> <YYYY>"
    echo "Compare the list of images on the Copernicus Open Access Hub to what"
    echo "we have on /mnt/ofviti/Sentinel1/img/<track>"
    echo "Provide the track and year for which you want to compare data"
    echo " e.g. $0 155 2018"
    exit 1
fi

track=$1
year=$2

workingdir="/home/adrian/tmp/T$track"

if ! [[ -d $workingdir ]]; then
    echo "Working directory $workingdir does not exist"
    echo "Create it and rerun script"
    exit 1
fi 

cd /home/adrian/tmp/T$track

# get the list of images we need from the Open Access Hub
# max 100 results are returned, so do half a year or quarter
# if in doubt do a quarter
/home/adrian/bin/S1_search_hub.sh "$track" "$year" "01" "03"
/home/adrian/bin/S1_search_hub.sh "$track" "$year" "04" "06"
/home/adrian/bin/S1_search_hub.sh "$track" "$year" "07" "09"
/home/adrian/bin/S1_search_hub.sh "$track" "$year" "10" "12"

# concat them all into a file for the year
cat T$track-$year-* > T$track-$year.txt

# this does a diff of the files we get from the previous step and a list of
# the images on dyngja, outputting the ones not in both places
echo "Missing images (also in T$track-$year-missing.txt):"
diff <(cat T$track-$year.txt | sort) <(~/bin/S1_images_total.sh T$track $year | sort) | tee T$track-$year-missing.txt
cat *missing.txt | grep S1 | sed 's/< //' > T$track-all-missing-images.txt
