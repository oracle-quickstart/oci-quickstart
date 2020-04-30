#!/bin/bash
set -e

export OCID=$(cat ${GITHUB_WORKSPACE}/ocid.txt 2> /dev/null)
sed -i 's/ocid1\.image\.oc1\.\.[a-z0-9]*/'"$OCID"'/' "${GITHUB_WORKSPACE}/${STACK_VARS_FILE}"

git config user.name "Automated Publisher"
git config user.email "actions@users.noreply.github.com"
git add "${GITHUB_WORKSPACE}/${STACK_VARS_FILE}"
git commit -m 'automated publish from update in ${GITHUB_WORKSPACE}/${LISTING_DIR}'
git push
