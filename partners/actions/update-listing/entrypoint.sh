#!/bin/bash
apt-get update
apt install -y build-essential zip python3 pyyaml

echo "${API_CREDS}" > ${GITHUB_WORKSPACE}/api.creds

export LISTING_ID=$(cat /listingId)
export VERSION_STRING=$(cat /newVersionName)
export ZIP_NAME=$(ls ${GITHUB_WORKSPACE}/upload

python3 /mpctl.py -action update_listing -listingVersionId $LISTING_ID -versionString $VERSION_STRING -fileName $ZIP_NAME

#echo "The OCID of the dummy image to be used in the listing update is: "
#cat ${GITHUB_WORKSPACE}/ocid.txt

#echo "The stack archive that contains the updated and tested Terraform code is: "
#ls ${GITHUB_WORKSPACE}/upload/
