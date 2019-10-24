#!/bin/bash

output="output.txt"
if [ "$2" != "" ]; then output=$2; fi
echo "listings for partner" > $output ;
echo "retreived with GET appstore/publisher/v1/listings" >> $output
python3 mpctl.py -creds $1 -action get_listings >> $output;
echo "************" >> $output
echo "listing details for each listingVersionId" >> $output
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}" >> $output
python3 mpctl.py -creds $1 -action get_listings | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_listing -id $listingVersionId ; done >> $output
echo "************" >> $output
echo "applications for partner" >> $output ;
echo "retreived with GET appstore/publisher/v1/applications" >> $output
python3 mpctl.py -creds $1 -action get_applications >> $output;
echo "************" >> $output
echo "packages for each listingVersionId" >> $output
echo "retreived with GET appstore/publisher/v2/applications/{listingVersionId}/packages" >> $output
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application_packages -id $listingVersionId ; done >> $output
echo "************" >> $output
echo "package details for each packageVersionId found in each listingVersionId" >> $output
echo "retreived with GET appstore/publisher/v2/applications/{listingVersionId}/packages/{packageVersionId}" >> $output
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application_packages -id $listingVersionId |  grep '\"id\": [0-9]' | grep -o [0-9]* | while read -r packageVersionId; do python3 mpctl.py -creds $1 -action get_application_package -id $listingVersionId -id2 $packageVersionId ; done ; done >> $output
echo "************" >> $output
echo "artifacts for partner" >> $output
echo "retreived with GET appstore/publisher/v1/artifacts" >> $output
python3 mpctl.py -creds $1 -action get_artifacts >> $output;
echo "************" >> $output
echo "artifact details for each artifactId found in packages" >> $output
echo "retreived with GET appstore/publisher/v1/artifacts/{artifactId}" >> $output
python3 mpctl.py -creds $1 -action get_artifacts | grep artifactId | grep -o [0-9]* | while read -r artifactId ; do python3 mpctl.py -creds $1 -action get_artifact -id $artifactId ; done >> $output

