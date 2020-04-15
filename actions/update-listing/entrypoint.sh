#!/bin/bash

pip install requests
pip install pyyaml

echo "${API_CREDS}" > ${GITHUB_WORKSPACE}/api_creds.yaml
export ZIP_FILE=${GITHUB_WORKSPACE}/marketplace/marketplace.zip

python /update-listing.py -action update_listing -credsFile ${GITHUB_WORKSPACE}/api_creds.yaml -fileName $ZIP_FILE
