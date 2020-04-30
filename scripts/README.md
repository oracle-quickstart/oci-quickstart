This directory contains utility scripts intended to be run on their own.

## `mkpl_setup.sh`

Used to setup the compartment and policy in a new publisher's tenancy in cloud-shell
in the OCI console. Can be run with either:

```
curl -sL https://git.io/JfOlY | bash
# or
curl -s https://raw.githubusercontent.com/oracle-quickstart/oci-quickstart/master/scripts/mkpl_setup.sh | bash
```

Running the script will create in the root compartment:
- a compartment called `marketplace_images`

- a policy called `marketplace` or `marketplace_new`

### Options/Info:
- If you add `export NEW='true';` before the curl it will create the policy for
the new validation service.

- If you add `export TESTING='true';` before the curl it will create resources with
random names then delete as a test.

- Command may be run twice with no effect. If resources exist, they are unchanged
and a 409 error returned which can be ignored.

- Note, the command may be run locally if desired, provided the `oci` CLI is installed
and configured.
