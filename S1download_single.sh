#!/bin/bash

# Fill in scihubcreds before use

if ! [[ "$1" =~ ^[1-9][0-9]{,2}$ ]] ; then
    echo "Error - give a valid orbit number as first parameter"
    echo ""
    echo "Usage : `basename $0` <track> <file-containing-list-of-images> "
    echo "e.g. `basename $0` 118 images.txt"
    exit 1;
fi


if ! [[ -f "$2" ]] ; then
    echo "Image list file $2 not found"
    exit 1;
fi

orbit=$1
filename="$2"

imgfolder="/mnt/ofviti/Sentinel1/img"
# format is user:password, use the S1auto Scihib creds
scihubcreds="" 

if ! [ -w $imgfolder/T$orbit/ ] ; then
    echo "Error - no write access to directory $imgfolder/T$orbit/"
    echo "Are you running this under the context of the S1auto user?"
    exit 1;
fi

while read -r img
do

    cd $imgfolder/T$orbit/

    # img S1A_IW_SLC__1SDV_20180810T185923_20180810T185958_023188_0284F6_668F
    # has ID 
    # https://scihub.copernicus.eu/dhus/odata/v1/Products('783d681b-c374-46a0-be7b-f6f5b5248bd5')/$value

    urlquery="https://scihub.copernicus.eu/dhus/odata/v1/Products?\$filter=Name%20eq%20%27${img}%27" 

    # get the details
    curl -u $scihubcreds -g "$urlquery" > /tmp/${img}.details.xml

    # get the ID
    id=$(awk -F'<id>|</id>' '{print $4}' /tmp/${img}.details.xml)

    if ! [[ "${id}" ]] ; then
        echo "Couldn't find this image on the Copernicus Open Access hub"
        exit 1;
    fi

    # download the image
    # note $value is actually just plain text used in the URL, not a value.
    # URL for download therefore something like
    # https://scihub.copernicus.eu/dhus/odata/v1/Products('783d681b-c374-46a0-be7b-f6f5b5248bd5')/$value
    downloadurl=$id/\$value
    echo $downloadurl
    exit 0

    echo "Downloading ${img}.zip to $imgfolder/T$orbit"
    curl -OkJL -u $scihubcreds -g "$downloadurl"

    echo "Extracting quicklook..."
    unzip -j "${img}.zip" "${img}.SAFE/preview/quick-look.png" -d "."
    mv quick-look.png ${img}.png

    # clean up interim file
    rm /tmp/${img}.details.xml

done < "$filename"

