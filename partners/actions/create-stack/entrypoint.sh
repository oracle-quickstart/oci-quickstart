#!/bin/bash
apt-get update
apt install -y build-essential zip

mkdir -p ${GITHUB_WORKSPACE}/upload

./${BUILD_SCRIPT_PATH}


