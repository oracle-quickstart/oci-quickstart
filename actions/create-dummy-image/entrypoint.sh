#!/bin/bash
apt-get update
apt install -y jq unzip

# Installing Packer
export VER="1.4.4"
wget -q https://releases.hashicorp.com/packer/${VER}/packer_${VER}_linux_amd64.zip
unzip packer_${VER}_linux_amd64.zip -d /usr/bin

# Set up environment
echo "${TF_VAR_private_key}" > ${GITHUB_WORKSPACE}/oci.pem
export TF_VAR_private_key_path=${GITHUB_WORKSPACE}/oci.pem

# Replace values with credentials for tenancy where image is being built
echo "Use Packer to create OCI image with cleanup-script"
jq '.builders[].user_ocid |= "'$TF_VAR_user_ocid'" |
    .builders[].tenancy_ocid |= "'$TF_VAR_tenancy_ocid'" |
    .builders[].fingerprint |= "'$TF_VAR_fingerprint'" |
    .builders[].key_file |= "'$TF_VAR_private_key_path'" |
    .builders[].compartment_ocid |= "'$TF_VAR_compartment_ocid'" |
    .builders[].image_name |= "'$(echo $GITHUB_REPOSITORY |cut -d'/' -f 2).$(date +"%Y%m%d_%H%M%S")'"' /marketplace_image.json > dummy_image.json
packer build dummy_image.json
cat manifest.json | jq -r .builds[0].artifact_id |  cut -d':' -f2 > ${GITHUB_WORKSPACE}/ocid.txt
