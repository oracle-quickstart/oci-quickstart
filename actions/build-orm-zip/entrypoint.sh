#!/bin/bash

apt-get update
apt install -y zip

cd ${GITHUB_WORKSPACE}/marketplace
./build.sh
