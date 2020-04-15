# OCI Marketplace Github Actions

This collection of Github Actions helps partners test their terraform code against a OCI tenancy, create custom images that are ready for OCI Marketplace validation and also update their listings on the Marketplace.

The actions can be combined into a workflow that offers an automated way of updating a published marketplace listings.

## Requirements
A partner that wants to leverage the Quickstart Actions must have the following:

- a Quickstart repo
- the Terraform code must me placed under a 'terraform' directory in the repo root
- The following OCI credentials must be saved as Github secrets in the repo. This requires admin privileges on the repo. The terraform code will be tested against this tenancy, so resources will be created and destroyed in this account. Also, with each run the "create-image" actions will create custom images in this tenancy, make sure to clean these up.
  - TF_VAR_user_ocid
  - TF_VAR_fingerprint
  - TF_VAR_private_key
  - TF_VAR_tenancy_ocid
  - TF_VAR_compartment_ocid
  - API_creds -- for Marketplace login
- a Workflow file that must be stored in the repo under .github/workflows

A good example of such a repo is oci-quickstart/oci-h20

## Available actions

Currently there is a limited number of actions available, which can support the automated update of an existing marketplace listing.

#### terraform-test
This action will test any Terraform code that is under the 'terraform' directory in the repo root. The action will create and then destroy all resources.
The action uses [Terratest](https://github.com/gruntwork-io/terratest). No other assertions are being performed currently.

#### create-stack
This action packages the terraform code from the partner repo into an archive that can be later submitted to the marketplace.

#### create-dummy-image
This action will a marketplace-ready image that is based on an existing OCI platform image.

#### create-partner-image
Similar to the above actions, but this action accepts an OCI image OCID as input. Partners can use their own custom images as baseline and create marketplace-ready images that include their software.

See below workflow example for synthax.

#### update-listings
This actions takes as input a OCI custom image OCID and a stack archive (terraform provisioning code) and used the API_creds secret to update an existing Marketplace listing with the new code or software that has been updated in the repo.


## Example workflow

```
on:
  push:
    branches:
      - 'development'
name: OCI-Marketplace
jobs:
  test-terraform-code:
    name: Update Marketplace Stack Listing
    runs-on: ubuntu-latest
    env:
      TF_VAR_compartment_ocid: ${{ secrets.TF_VAR_compartment_ocid }}
      TF_VAR_fingerprint: ${{ secrets.TF_VAR_fingerprint }}
      TF_VAR_private_key: ${{ secrets.TF_VAR_private_key }}
      TF_VAR_private_key_path: $GITHUB_WORKSPACE/oci.pem
      TF_VAR_tenancy_ocid: ${{ secrets.TF_VAR_tenancy_ocid }}
      TF_VAR_user_ocid: ${{ secrets.TF_VAR_user_ocid }}
    steps:
    - uses: actions/checkout@master
      name: Checkout Quickstart Repo
      with:
              ref: development
    - uses: "oci-quickstart/oci-quickstart/partners/actions/terraform-test@v0.91"
      name: Test Terraform Code
    - uses: "oci-quickstart/oci-quickstart/partners/actions/create-stack@v0.91"
      name: Create Stack Archive
      if: success()
    #- user: "oci-quickstart/oci-quickstart/partners/actions/create-dummy-image@v0.91"
    #  name: Create Dummy Image
    - uses: "oci-quickstart/oci-quickstart/partners/actions/create-partner-image@v0.91"
      name: Create Partner Marketplace-ready Image
      with:
        base-image: 'ocid1.image.oc1.iad.aaaaaaaavxqdkuyamlnrdo3q7qa7q3tsd6vnyrxjy3nmdbpv7fs7um53zh5q'
    - uses: "oci-quickstart/oci-quickstart/partners/actions/update-listing@v0.91"
      name: Update Marketplace Listing

```
