#!/bin/bash
set -e

apt-get update
apt install -y build-essential zip

mkdir -p ${GITHUB_WORKSPACE}/upload

cd "${GITHUB_WORKSPACE}/${LISTING_DIR}/marketplace"
./${BUILD_SCRIPT}
export ZIP_FILE=$(ls *.zip 2> /dev/null)
echo "path"
echo "${GITHUB_WORKSPACE}/${LISTING_DIR}/marketplace/*.zip"
echo "ls"
echo $(ls "${GITHUB_WORKSPACE}/${LISTING_DIR}/marketplace/*.zip" 2> /dev/null)
echo "filename"
echo $ZIP_FILE
mv $ZIP_FILE ${GITHUB_WORKSPACE}/upload


