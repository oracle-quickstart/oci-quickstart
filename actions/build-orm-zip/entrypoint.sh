#!/bin/bash

apt-get update
apt install -y build-essential zip

mkdir -p ${GITHUB_WORKSPACE}/upload

cd ${GITHUB_WORKSPACE}/util
./${BUILD_SCRIPT}
export ZIP_FILE=$(ls ${GITHUB_WORKSPACE}/util/*.zip 2> /dev/null)
mv $ZIP_FILE ${GITHUB_WORKSPACE}/upload
