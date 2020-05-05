# Actions

This collection of Github Actions helps partners test their terraform code against a OCI tenancy, create custom images that are ready for OCI Marketplace validation and also update their listings on the Marketplace.

The actions can be combined into a workflow that offers an automated way of updating a published marketplace listings.

## Requirements

A partner that wants to leverage the Quick Start Actions must have the following:

-   a Quick Start repo
-   the Terraform code must me placed under a 'terraform' directory in the repo root
-   The following OCI credentials must be saved as Github secrets in the repo. This requires admin privileges on the repo. The terraform code will be tested against this tenancy, so resources will be created and destroyed in this account. Also, with each run the "create-image" actions will create custom images in this tenancy, make sure to clean these up.
    -   TF_VAR_user_ocid
    -   TF_VAR_fingerprint
    -   TF_VAR_private_key
    -   TF_VAR_tenancy_ocid
    -   TF_VAR_compartment_ocid
    -   API_creds -- for Marketplace login
-   a Workflow file that must be stored in the repo under .github/workflows

A good example of such a repo is https://github.com/oracle-quickstart/oci-h2o

## terraform-apply
This action will test any Terraform code that is under the 'terraform' directory in the repo root. The action will create and then destroy all resources.  The action uses [Terratest](https://github.com/gruntwork-io/terratest). No other assertions are being performed currently.

## build-orm-zip
This action packages the terraform code from the partner repo into an archive that can be later submitted to the marketplace.

## create-image
This action creates a marketplace ready image that is based on an existing OCI platform image.

## update-listing
This actions takes as input a OCI custom image OCID and a stack archive (terraform provisioning code) and used the API_creds secret to update an existing Marketplace listing with the new code or software that has been updated in the repo.

## Example Workflow

```
on:
  push:
    branches:
      - 'master'
name:                          Marketplace
jobs:
  update-stack-listing:
    name:                      Update Stack Listing
    runs-on:                   ubuntu-latest
    env:
      TF_VAR_compartment_ocid: ${{ secrets.TF_VAR_compartment_ocid }}
      TF_VAR_fingerprint:      ${{ secrets.TF_VAR_fingerprint }}
      TF_VAR_private_key:      ${{ secrets.TF_VAR_private_key }}
      TF_VAR_private_key_path: $GITHUB_WORKSPACE/oci.pem
      TF_VAR_tenancy_ocid:     ${{ secrets.TF_VAR_tenancy_ocid }}
      TF_VAR_user_ocid:        ${{ secrets.TF_VAR_user_ocid }}
      API_CREDS:               ${{ secrets.API_CREDS }}
    steps:
    - name:                    Checkout
      uses:                    actions/checkout@master
    - name:                    Terraform Apply
      uses:                    "oci-quickstart/oci-quickstart/actions/terraform-apply@master"
    - name:                    Build ORM Zip
      uses:                    "oci-quickstart/oci-quickstart/actions/build-orm-zip@master"
      if:                      success()
    - name:                    Update Listing
      uses:                    "oci-quickstart/oci-quickstart/actions/update-listing@master"
```
