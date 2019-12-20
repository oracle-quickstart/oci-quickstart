#!/bin/bash

echo "${API_CREDS}" > ${GITHUB_WORKSPACE}/api_creds.yaml

export LISTING_ID=$(cat ${GITHUB_WORKSPACE}/ListingId 2> /dev/null)
export ZIP_FILE=$(ls ${GITHUB_WORKSPACE}/upload 2> /dev/null)
export ZIP_PATH=${GITHUB_WORKSPACE}/upload
export OCID=$(cat ${GITHUB_WORKSPACE}/ocid.txt 2> /dev/null)

if [ -z "$LISTING_ID" ]
then
    if [ -z "$OCID" ]
    then
        echo "python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action create_listing -fileName $ZIP_PATH/$ZIP_FILE"
        python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action create_listing -fileName $ZIP_PATH/$ZIP_FILE
    else
        echo "python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action create_listing -imageOcid $OCID"
        python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action create_listing -imageOcid $OCID
    fi
else
    if [ -z "$OCID" ]
    then
        echo "python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action update_listing -listingVersionId $LISTING_ID -fileName $ZIP_PATH/$ZIP_FILE"
        python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action update_listing -listingVersionId $LISTING_ID -fileName $ZIP_PATH/$ZIP_FILE
    else
        echo "python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action update_listing -listingVersionId $LISTING_ID -imageOcid $OCID"
        python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action update_listing -listingVersionId $LISTING_ID -imageOcid $OCID
    fi    
fi
