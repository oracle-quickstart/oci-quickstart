#!/usr/bin/env bash

# To test run: export TESTING="true"
# To clear: unset TESTING

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get tenancy id via CLI
tenancy_id=$(oci iam availability-domain list | jq -r ' .data[0]."compartment-id"')
# Alternatives that work now, but may not in the future
# tenancy_id=$(grep tenancy $OCI_CLI_CONFIG_FILE | head -n 1 | cut -d'=' -f2)
# oci iam compartment list | jq -cr '[.data[] | select(."compartment-id" | contains("tenancy"))] | .[0]."compartment-id"'

# Alternative without jq is tenancy_id=$(oci iam availability-domain list --query 'data[0]."compartment-id"' --raw-output)

if [ -z "$tenancy_id" ]
then
  echo "Error: Unable to discover tenancy ocid, exiting"
  exit 1
else
  echo -e "${GREEN}SUCCESS: teancy ocid discovered: $tenancy_id${NC}"
fi


comp_name="marketplace_images"
policy_name="marketplace"

# testing override
if [ -n "$TESTING" ]
then
  rand=$RANDOM
  comp_name="clitest$rand"
  policy_name="clitest$rand"
  echo -e "${CYAN}INFO: in test mode.${NC}"
fi

echo -e "${CYAN}INFO: will create compartment and policy named $comp_name and $policy_name${NC}"

policy='[
  "ALLOW SERVICE marketplace to manage App-catalog-publisher-listing IN TENANCY",
  "ALLOW SERVICE marketplace to read tenant IN TENANCY",
  "ALLOW SERVICE marketplace to read compartments IN TENANCY",
  "ALLOW SERVICE marketplace to inspect instance-images IN TENANCY",
  "ALLOW SERVICE marketplace to inspect instances IN TENANCY"
]'

# new policy override
if [ -n "$NEW" ]
then
  echo -e "${CYAN}INFO: override set, using new policy/name.${NC}"
  policy='[
    "ALLOW SERVICE marketplace to read tenant IN TENANCY",
    "ALLOW SERVICE marketplace to read compartments IN TENANCY",
    "ALLOW SERVICE marketplace to read instance-images IN TENANCY",
    "ALLOW SERVICE marketplace to inspect instances IN TENANCY",
    "ALLOW SERVICE marketplace to manage App-catalog-publisher-listing IN TENANCY"
  ]'
  policy_name="marketplace_new"
fi

echo $policy > tmp_mkpl_policy.json

# Create compartment under root compartment
echo -e "${CYAN}INFO: Creating compartment...${NC}"
comp_json="$(oci iam compartment create \
  --compartment-id $tenancy_id \
  --description "To contain custom images read by the marketplace service" \
  --name $comp_name)"
comp_return=$?
echo $comp_json | jq -M .

if [[ $comp_return -eq 0 ]]
then
  echo -e "${GREEN}SUCCESS: compatment $comp_name created.${NC}"
  comp_id = ${echo $comp_json | jq -r .data.id}
else
  echo -e "${RED}ERROR: compartment not created.${NC}"
fi

# Create policy under root compartment
echo -e "${CYAN}INFO: Creating policy...${NC}"
policy_json=$(oci iam policy create \
  --compartment-id $tenancy_id \
  --description "Allow marketplace service to read images" \
  --name $policy_name \
  --statements file://./tmp_mkpl_policy.json)
policy_return=$?
echo $policy_json | jq -M .

if [[ $policy_return -eq 0 ]]
then
  echo -e "${GREEN}SUCCESS: policy $policy_name created.${NC}"
else
  echo -e "${RED}ERROR: policy not created.${NC}"
fi

echo -e "${CYAN}INFO: cleaning policy tmp file...${NC}"
rm -f tmp_mkpl_policy.json

echo -e "${CYAN}INFO: script is idempotent, 409 errors are ignorable.${NC}"

echo -e "\n\n\n"
echo -e "${CYAN}INFO: values to setup tenancy in partner portal"
echo -e "${CYAN}tenancy_id: $tenancy_id"
echo -e "${CYAN}compartment_id: $comp_id"

# testing override
if [ -n "$TESTING" ]
then
  echo -e "${CYAN}INFO: deleting testing resources...${NC}"
  id=$(echo $comp_json | jq -r '.data.id')
  echo -e "${CYAN}INFO: deleting $id ...${NC}"
  oci iam compartment delete --force --compartment-id $id
  id=$(echo $policy_json | jq -r '.data.id')
  echo -e "${CYAN}INFO: deleting $id ...${NC}"
  oci iam policy delete --force --policy-id $id
fi
