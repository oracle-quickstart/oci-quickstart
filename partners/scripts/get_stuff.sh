#!/bin/bash
echo "listings for partner" > output.txt ;
echo "retreived with GET appstore/publisher/v1/listings" >> output.txt
python3 mpctl.py -creds $1 -action get_listings >> output.txt;
echo "************" >> output.txt
echo "listing details for each listingVersionId" >> output.txt
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}" >> output.txt
python3 mpctl.py -creds $1 -action get_listings | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_listing -id $listingVersionId ; done >> output.txt
echo "************" >> output.txt
echo "package details for each packageVersionId found in listings" >> output.txt
echo "retreived with GET appstore/publisher/v1/artifacts/{packageVersionId}" >> output.txt
python3 mpctl.py -creds $1 -action get_listings | grep packageVersionId | grep -o [0-9]* | while read -r packageVersionId ; do python3 mpctl.py -creds $1 -action get_package -id $packageVersionId ; done >> output.txt
echo "************" >> output.txt
echo "packages for partner" >> output.txt
echo "retreived with GET appstore/publisher/v1/artifacts" >> output.txt
python3 mpctl.py -creds $1 -action get_packages >> output.txt;
echo "************" >> output.txt
echo "package details for each artifactId found in packages" >> output.txt
echo "retreived with GET appstore/publisher/v1/artifacts/{artifactId}" >> output.txt
python3 mpctl.py -creds $1 -action get_packages | grep artifactId | grep -o [0-9]* | while read -r artifactId ; do python3 mpctl.py -creds $1 -action get_package -id $artifactId ; done >> output.txt
echo "applicatoons for partner" >> output.txt ;
echo "retreived with GET appstore/publisher/v1/applications" >> output.txt
python3 mpctl.py -creds $1 -action get_applications >> output.txt;
echo "************" >> output.txt
echo "applications details for each listingVersionId" >> output.txt
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}" >> output.txt
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application -id $listingVersionId ; done >> output.txt
echo "************" >> output.txt
echo "packages for each listingVersionId" >> output.txt
echo "retreived with GET appstore/publisher/v1/applications/{listingVersionId}/packages" >> output.txt
python3 mpctl.py -creds $1 -action get_applications | grep listingVersionId | grep -o [0-9]* | while read -r listingVersionId ; do python3 mpctl.py -creds $1 -action get_application_package -id $listingVersionId ; done >> output.txt

