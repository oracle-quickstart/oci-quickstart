#!/bin/bash

echo "The OCID of the dummy image to be used in the listing update is: "
cat ${GITHUB_WORKSPACE}/ocid.txt

echo "The stack archive that contains the updated and tested Terraform code is: "
ls ${GITHUB_WORKSPACE}/upload/