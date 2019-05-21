# Best Practices

## What is a Quickstart?
A Quickstart allow a customer to deploy some ISV's software product (e.g. Couchbase, Cloudera, Datastax).  It deploys an appropriate architecture and installs the software in their tenancy.  A Quickstart has defaults that deploy a simple example of the software.  It requires as few parameters as possible and does not depend on any existing resources. It is parameterized in such a way that the same Quickstart can be used for more complicated deployments.

## Core Principle - Usability First
Quickstart deployments are intended to give our users a quick start running some piece of software.  As a result we prioritize usability above all else.  A user who knows little to nothing about OCI should be able to stumble in, hit deploy and get a running thing in 5-10 minutes.  Some might argue the system isn't production grade.  That's ok.  It can be improved.  Additional Terraform for more complex systems can be provided.  But, the base version needs to be braindead simple.

## Packages exist for a reason.  Use them.
Yes, there may be a tgz or zip.  Don't use it!  Use the package.  Somebody who knows about the application at hand built a package.  It includes lots of logic you don't want to rewrite.  Follow the three virtues and be lazy!

## We don't use bastions.
Bastion hosts are a broken security model that some incredibly risk averse people in the AWS well architected group came up with.  Those people never had to use any software in production, much less develop anything.  The result is they are an unusable model requiring terminal sessions and more to hop between multiple machines.  As a general rule we don't put them in a Quickstart.  There would have to be a very good reason to break this rule.

## We use cloud-init.  We do use not remote-exec or local-exec.
Yes, those are nifty features of Terraform.  That doesn't mean you have to use them.  Before Terraform there was cloud-init.  It's more scalable than SSH'ing into each node.  It's more robust to connectivity issues (like closing your laptop before deploy is done) and it runs asynchronously.  Beyond that, it's the model every other cloud uses.  We use it whereever we can.  If there's some reason we can, then fine, drop down to SSH'ing to a node.

## We do not copy code from other Quickstarts on AWS and Azure
This should go without saying.  Just don't do it!

## Reference oci-quickstart-prerequisites or oke-quickstart-prerequisites
Don't create individual env-vars files.  Don't provide an oci how to in each repo.  Otherwise we're going to end up maintaining many copies of the same thing.

## Repo Structure
* A Quickstart will always be some collection of TF and shell.
* At a minimum a Quickstart will create a VCN and some set of instances.
* A style guide or a generic example template(s) should be developed.
* Since loops and conditionals in TF aren't fully developed (and there are open features/issues around this) we should have standard examples for common constructs.
* For MVP Quickstarts they should deploy to one region and instances requiring HA should be mapped to FD's.
* TF allows at least 3 ways to execute shell on an instance we should standardize on one. The best combination of flexibility and readability may be using user_data resolving TF vars as shell vars inline. Use of remote-exec precludes the use of ORM. ORM can use remote-exec, but that comes with the same issues as running it locally, plus needing to deal with keys differently than locally.
* Gathering information in the shell is in general preferred over passing in a parameter.
* Since referencing a generic module (e.g. a VCN template) in multiple Quickstarts requires CI/CD of the module, at first all Quickstarts should contain all required resources.
* We should conditionalize the use of either NVME or block storage based on shape.

## Documentation
Documentation of a Quickstart should be standardized and contain the same sections:

* Introduction on what the software is and what it's used for.
* Architecture diagram and description of default deployment and any required parameters.
* Detailed description of all parameters.
* Examples of more complicated deployments with arch diagrams if necessary.
* Any necessary post-deploy actions. Note, these should be minimized and ideally there are none.

## Security
* Passwords are set to a non-default value.
* Only required ports are opened.
* Connections allowed only from the user's CIDR block optional.
* No HTTP allowed for management consoles, HTTP ports may be open if they redirect to HTTPS.
* For software that manages the install/config private keys should not be held by OCI. They should be generated on the fly and the public key passed via object storage to instances that need it.
