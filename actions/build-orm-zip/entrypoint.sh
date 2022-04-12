#!/bin/bash

apt-get update
apt install -y zip git

cd ${GITHUB_WORKSPACE}/marketplace
./build.sh
