#!/bin/bash
#apt-get update
#apt install -y build-essential zip python3.6 python-yaml
#apt install -y PyYAML

echo "${API_CREDS}" > ${GITHUB_WORKSPACE}/api_creds.yaml

export LISTING_ID=$(cat ${GITHUB_WORKSPACE}/ListingId)
export VERSION_STRING=$(cat ${GITHUB_WORKSPACE}/Version)
export ZIP_NAME=$(ls ${GITHUB_WORKSPACE}/upload)

python /mpctl.py -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -action update_listing -listingVersionId $LISTING_ID -versionString "$VERSION_STRING" -fileName ${GITHUB_WORKSPACE}/$ZIP_NAME

#echo "The OCID of the dummy image to be used in the listing update is: "
#cat ${GITHUB_WORKSPACE}/ocid.txt

#echo "The stack archive that contains the updated and tested Terraform code is: "
#ls ${GITHUB_WORKSPACE}/upload/
