#!/bin/bash

output="output.txt"
if [ "$2" != "" ]; then output=$2; fi
echo $output
echo "listings for partner" > $2 ;
echo "retreived with GET appstore/publisher/v1/listings" >> $2
python3 mpctl.py -creds $1 -action get_listings >> $2;
echo "************" >> $2
echo "listing details for each listingVersionId" >> $2
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}" >> $2
python3 mpctl.py -creds $1 -action get_listings | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_listing -id $listingVersionId ; done >> $2
echo "************" >> $2
echo "package details for each packageVersionId found in listings" >> $2
echo "retreived with GET appstore/publisher/v1/artifacts/{packageVersionId}" >> $2
python3 mpctl.py -creds $1 -action get_listings | grep packageVersionId | grep -o [0-9]* | while read -r packageVersionId ; do python3 mpctl.py -creds $1 -action get_package -id $packageVersionId ; done >> $2
echo "************" >> $2
echo "packages for partner" >> $2
echo "retreived with GET appstore/publisher/v1/artifacts" >> $2
python3 mpctl.py -creds $1 -action get_packages >> $2;
echo "************" >> $2
echo "package details for each artifactId found in packages" >> $2
echo "retreived with GET appstore/publisher/v1/artifacts/{artifactId}" >> $2
python3 mpctl.py -creds $1 -action get_packages | grep artifactId | grep -o [0-9]* | while read -r artifactId ; do python3 mpctl.py -creds $1 -action get_package -id $artifactId ; done >> $2
echo "applicatoons for partner" >> $2 ;
echo "retreived with GET appstore/publisher/v1/applications" >> $2
python3 mpctl.py -creds $1 -action get_applications >> $2;
echo "************" >> $2
echo "applications details for each listingVersionId" >> $2
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}" >> $2
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application -id $listingVersionId ; done >> $2
echo "************" >> $2
echo "packages for each listingVersionId" >> $2
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}/packages" >> $2
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application_package -id $listingVersionId ; done >> $2

