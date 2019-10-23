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
echo "package details for each packageVersionId found in listings" >> $output
echo "retreived with GET appstore/publisher/v1/artifacts/{packageVersionId}" >> $output
python3 mpctl.py -creds $1 -action get_listings | grep packageVersionId | grep -o [0-9]* | while read -r packageVersionId ; do python3 mpctl.py -creds $1 -action get_package -id $packageVersionId ; done >> $output
echo "************" >> $output
echo "packages for partner" >> $output
echo "retreived with GET appstore/publisher/v1/artifacts" >> $output
python3 mpctl.py -creds $1 -action get_packages >> $output;
echo "************" >> $output
echo "package details for each artifactId found in packages" >> $output
echo "retreived with GET appstore/publisher/v1/artifacts/{artifactId}" >> $output
python3 mpctl.py -creds $1 -action get_packages | grep artifactId | grep -o [0-9]* | while read -r artifactId ; do python3 mpctl.py -creds $1 -action get_package -id $artifactId ; done >> $output
echo "applicatoons for partner" >> $output ;
echo "retreived with GET appstore/publisher/v1/applications" >> $output
python3 mpctl.py -creds $1 -action get_applications >> $output;
echo "************" >> $output
echo "applications details for each listingVersionId" >> $output
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}" >> $output
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application -id $listingVersionId ; done >> $output
echo "************" >> $output
echo "packages for each listingVersionId" >> $output
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}/packages" >> $output
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application_package -id $listingVersionId ; done >> $output

