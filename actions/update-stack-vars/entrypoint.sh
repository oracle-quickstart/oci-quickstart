#!/bin/bash
set -e

export OCID=$(cat ${GITHUB_WORKSPACE}/ocid.txt 2> /dev/null)

sed -i 's/ocid1\.image\.oc1\.[a-z]*\.[a-z0-9]*/'"$OCID"'/' "${GITHUB_WORKSPACE}/${STACK_VARS_FILE}"

git config --local user.name "Automated Publisher"
git config --local user.email "actions@users.noreply.github.com"
git add "${GITHUB_WORKSPACE}/${STACK_VARS_FILE}"
git commit -m "automated publish from update in ${GITHUB_WORKSPACE}/${LISTING_DIR}"
git push "https://cmp-deploy:${PAT}@github.com/${GITHUB_REPOSITORY}.git" HEAD:${branch}
