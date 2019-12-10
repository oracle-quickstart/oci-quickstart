#!/bin/bash

echo "${API_CREDS}" > ${GITHUB_WORKSPACE}/api_creds.yaml

export LISTING_ID=$(cat ${GITHUB_WORKSPACE}/ListingId)
export VERSION_STRING=$(cat ${GITHUB_WORKSPACE}/Version)
export ZIP_FILE=$(ls ${GITHUB_WORKSPACE}/upload)
export ZIP_PATH=${GITHUB_WORKSPACE}/upload

if [ -z "$LISTING_ID" ]
then
    echo "python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action create_listing -versionString '$VERSION_STRING' -fileName $ZIP_PATH/$ZIP_FILE"
    python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action create_listing -versionString "$VERSION_STRING" -fileName $ZIP_PATH/$ZIP_FILE
else
    echo "python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action update_listing -listingVersionId $LISTING_ID -versionString '$VERSION_STRING' -fileName $ZIP_PATH/$ZIP_FILE"
    python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action update_listing -listingVersionId $LISTING_ID -versionString "$VERSION_STRING" -fileName $ZIP_PATH/$ZIP_FILE
fi