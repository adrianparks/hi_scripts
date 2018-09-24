#!/usr/bin/bash

# Search Copernicus hub for S1 image filenames based on track, between two dates
# A list of the IDs for that time period is output

# make sure you fill in the scihib creds with the ones for S1auto before running
# scihubcreds="user:password"

if [ $# -ne 4 ]; then
    echo "Usage: $0 <track> <YYYY> <MM> <MM>"
    echo "Error: Provide the track, year, start month and end month you want to see images for e.g. $0 155 2018 01 03"
    exit 1
fi

# track=155
# year=2018
# startmonth=01
# endmonth=03

# make sure you fill in the scihib creds for cURL
# format is user:password
scihubcreds=""

track=$1
year=$2
startmonth=$3
endmonth=$4

queryendmonth=$(echo "$endmonth + 1" | bc)
if [ ${#queryendmonth} -ne 2 ]; then
    queryendmonth="0"$queryendmonth
fi

# dates="NOW-60DAY%20TO%20NOW-30DAY"
dates="$year-$startmonth-01T00:00:00.000Z%20TO%20$year-$queryendmonth-01T00:00:00.000Z"

# search areas, by track
declare -A area=(
   ["9"]="-20.5%2063.39,-16.6%2063.39,-16.6%2066.54,-20.5%2066.54,-20.5%2063.39"
   ["16"]="-24.1%2063.39,-18.5%2063.39,-18.5%2066.47,-24.1%2066.47,-24.1%2063.39"
   ["111"]="-19.5%2063.39,-13.5%2063.39,-13.5%2066.54,-19.5%2066.54,-19.5%2063.39"
   ["118"]="-22.0%2063.39,-14.0%2063.39,-14.0%2066.47,-22.0%2066.47,-22.0%2063.39"
   ["147"]="-17.3%2063.75,-16.3%2063.75,-16.3%2066.54,-17.3%2066.54,-17.3%2063.75"
   ["155"]="-24.1%2063.7,-20.3%2063.7,-20.3%2066.47,-24.1%2066.47,-24.1%2063.7")

if [ -z "${area[$track]}" ]; then
   echo "Track $track is not valid for search here"
   exit 1
fi

searcharea=${area[$track]}

# Ingestion date
# urlquery="https://scihub.copernicus.eu/dhus/search?rows=100&q=platformname:Sentinel-1%20AND%20producttype:SLC%20AND%20sensoroperationalmode:IW%20AND%20relativeorbitnumber:$track%20AND%20ingestionDate:[$dates]%20AND%20footprint:%22Intersects(POLYGON((-24.1%2063.7,-20.3%2063.7,-20.3%2066.47,-24.1%2066.47,-24.1%2063.7)))%22"

# Sensing date
urlquery="https://scihub.copernicus.eu/dhus/search?rows=100&q=platformname:Sentinel-1%20AND%20producttype:SLC%20AND%20sensoroperationalmode:IW%20AND%20relativeorbitnumber:$track%20AND%20beginposition:[$dates]%20AND%20footprint:%22Intersects(POLYGON(($searcharea)))%22"

# echo $urlquery

echo "Images on Copernicus Open Access hub for track $track between $year-$startmonth and $year-$endmonth:"
curl -s -u "$scihubcreds" -g "$urlquery" | grep \"identifier\" | sed 's/\(<str name="identifier">\|<\/str>\)//g' | tee T$track-$year-$startmonth-$endmonth.txt
# echo $(wc -l < T$track-$year-$startmonth-$endmonth.txt) in total
