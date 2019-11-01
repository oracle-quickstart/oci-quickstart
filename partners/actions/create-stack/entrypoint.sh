#!/bin/bash
apt-get update
apt install -y build-essential zip

mkdir -p ${GITHUB_WORKSPACE}/upload
cd ${GITHUB_WORKSPACE}/terraform
export FILENAME=$(echo ${GITHUB_REPOSITORY} |cut -d'/' -f 2).$(date +"%Y%m%d_%H%M%S")
zip -r ${GITHUB_WORKSPACE}/upload/$FILENAME.zip ./ -x ".terraform/*" -x "*tfstate*"
