# scripts
This directory contains utility scripts intended to be run on their own.

## `mkpl_setup.sh`

Used to setup the compartment and policy in a new publisher's tenancy in cloud-shell
in the OCI console. **Note: these commands must be run in the home region of your tenancy.**

Can be run with:

```
curl -s https://raw.githubusercontent.com/oracle-quickstart/oci-quickstart/master/scripts/mkpl_setup.sh | bash
```

Running the script will create in the root compartment:
- a compartment called `marketplace`

- a policy called `marketplace`

- id values are printed at the end to be used in tenancy setup in the partner portal

### Options/Info:

- If you add `export TESTING='true';` before the curl it will create resources with
random names then delete as a test.

- Run `unset <var-name>` to remove either override.

- Command may be run twice with no effect. If the policy exists it is deleted and recreated under the same name. A `409 ResourceExists` error returned which can be ignored.

- Note, the command may be run locally if desired, provided the `oci` CLI is installed
and configured.
