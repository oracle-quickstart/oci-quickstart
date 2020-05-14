# Marketplace Stack Schema
Oracle Cloud Infrastructure Marketplace is an online store that offers applications specifically for customers of Oracle Cloud Infrastructure. In the Oracle Cloud Infrastructure Marketplace catalog, customers can find and launch Images and Stacks from Oracle or trusted partners. These Marketplace Images or Stacks are deployed into the customer's tenancy.

Marketplace Images are templates of virtual hard drives that determine the operating system and software to run on an instance. Publishers will publish a [Custom Image](https://docs.cloud.oracle.com/iaas/Content/Compute/Tasks/managingcustomimages.htm) as an Artifact in the [Marketplace Partner Portal](https://partner.cloudmarketplace.oracle.com/partner/index.html).

[Marketplace Stacks](https://docs.oracle.com/en/cloud/marketplace/partner-portal/partp/how-do-i-publish-oracle-cloud-infrastructure-stack.html) are composed by Terraform configuration files (templates) and a YAML descriptor [file](https://docs.oracle.com/en/cloud/marketplace/partner-portal/partp/schema-stack-input-variables.html) containing the definition of Terraform Input variables, packaged all together in a zip file.  A Stack run as a job in the OCI [Resource Manager](https://docs.cloud.oracle.com/iaas/Content/ResourceManager/Concepts/resourcemanager.htm) service.

A configuration is a set of one or more Terraform configuration (.tf) file written in HCL,  that specify the Oracle Cloud Infrastructure resources, including resource metadata, and other important information, like data source definitions and variables declarations.

Terraform variables are defined as environment variables, command line arguments or placed into TFVars file when they are launched from Terraform CLI. Running a standalone ORM Stack (not Marketplace related) is possible to set variables at the time a Stack is created via OCI CLI, by specifying a json file.

In order to enable any user - technical or non-technical to launch a Marketplace Stack directly from the OCI console without depending on any CLI,  Marketplace/ORM provided a unique feature to enable publishers to create a custom UI for their Stacks where they can create a Form based on the same look and feel of OCI console and also can link the OCI created resources with the Marketplace listing that originated it. This UI is defined in the YAML descriptor file packaged along with the Terraform templates.

## Marketplace Stack Requirements

| #    | Description |
| :--- | :---------- |
| 1    | Schema file is based on [YAML](https://yaml.org/)  |
| 2    | All variables declared in the schema file MUST exist in the Terraform configuration.  |
| 3    | The `tenancy_ocid` and `region` variables must be declared as part of the schema, but placed in a hidden `variableGroups` section as their values are set automatically by ORM based on customer selections in the OCI console. |
| 4    | Variables not declared in the schema but declared in the Terraform root module will be displayed in the bottom of the Variables configuration page in ORM. If you don't want to display these variables in ORM, declare them within the `variableGroups` section as part of a group that is hidden from users. |
| 5    | You must create different sections within the `variableGroups` definition for grouping similar OCI Services, e.g. Network, Storage, Compute. That will make the user experience similar to standard OCI UI. For example, create a section to group Network resources and put all variables that manage network (VCN, Subnets, etc) into that group.  |

## YAML Schema Building Blocks

### 1. Marketplace Application Information Tab

This block contains general information related to the listing that is displayed in the Application Information tab in the OCI Console, e.g. application description, logo/icon URL, listing-id, content-language and  some boilerplate code related to the schema version.

#### Fields
| Name | Description |
| :--- | :---------- |
| title | Title of the listing displayed in the OCI console - Application Information tab |
| description | Sub Title shown in Application Information tab. |
| schemaVersion | YAML Schema version. Fixed Value = `1.1.0` |
| version | Marketplace API Version. Fixed Value = `20190404` |
| logoUrl (optional) | URL of Logo Icon used on Application Information tab. You can copy the `contentId` from the Marketplace listing logo URL in the Marketplace Partner portal. |
| source (optional)| This field is used by ORM to display the "View Instructions" section of the Marketplace listing.<br>`type: marketplace` is a fixed value<br>`reference:<application_id>` this is the listing idenfier and you can copy this information from the preview URL of the Marketplace listing `application_id=12345` URL parameter. |
| locale | Listing Locale, e.g. `en` for English |

#### Sample Code
```yaml
title: "My Super Application"
description: "This is the best application in the Marketplace"
schemaVersion: 1.1.0
version: "20190304"

logoUrl: "https://cloudmarketplace.oracle.com/marketplace/content?contentId=58352039"

source:
  type: marketplace
  reference: 47726045

locale: "en"
```

### 2. variableGroups

#### Fields

| Name | Description |
| :--- | :---------- |
| variableGroups | Top level identifier of `variableGroups` section |
| title | Title of the Group |
| variables | list of variables that are presented/hidden in this group |
| visible (optional) | set the visibility of variableGroups block - use a boolean or an expression. Visibility can be defined at variable level.|

#### Sample Code

```yaml
variableGroups:
  - title: "Hidden Variable Group"
    visible: false
    variables:
#variables used by Terraform but not necesarrily exposed exposed to end user
      - tenancy_ocid
      - region
      - mp_listing_id
      - mp_listing_resource_id
      - mp_listing_resource_version
      - availability_domain_number

  - title: "Compute Configuration"
    variables:
      - compute_compartment_ocid
      - vm_display_name
      - hostname_label
      - vm_compute_shape
      - availability_domain_name
      - ssh_public_key

  - title: "Virtual Cloud Network"
    variables:
      - network_compartment_ocid
      - network_strategy
      - network_configuration_strategy
      - vcn_id
      - vcn_display_name
      - vcn_dns_label
      - vcn_cidr_block

#Management subnet group contains logic to toggle the visibility of the group based on variables defined by customer during Stack configuration in the OCI console.
  - title: "Management Subnet"
    visible: #($network_strategy  == ""Use Existing VCN and Subnet"") OR (network_configuration_strategy ==  "Customize Network Configuration")
      or:
        - eq:
          - network_strategy
          - "Use Existing VCN and Subnet"
        - eq:
          - network_configuration_strategy
          - "Customize Network Configuration"
    variables:
      - mgmt_subnet_type
      - mgmt_subnet_id
      - mgmt_subnet_display_name
      - mgmt_subnet_cidr_block
      - mgmt_subnet_dns_label
      - mgmt_nsg_configuration_strategy

```

### 3. Terraform Variables

Use this section to declare all Terraform Input variables that are presented in your Template. All variables in the Terraform Root Module should be declared.

#### Variables

| Name | Description |
| :--- | :---------- |
| variables | Top level identifier of `variables` section |
| `<variable_name>` | The name of the input variable declared in the Terraform template. |
| type | Definition of the variable type supported by the schema. This is not a Terraform variable type as the OCI Marketplace schema support dynamic types that will automatically lookup for OCI resource types. See Dynamic types.|
| minLength | Minimum Length of the variable |
| maxLength | Maximum Length of the variable |
| pattern | Regex pattern |
| title | Label of the variable. In case a label is not specified, ORM will use the variable name as the title. |
| description | Tooltip with the description of the variable. ORM will look at the value provided within the variables definition of the Terraform template in case a description is not provided in the schema |
| default | Variable default value |
| required | set the variable requirement -  use a boolean or an expression |
| visible | set the visibility of a variable - use a boolean or an expression |

#### Variable Types

Variable Types in the Schema definition are statically or dynamically resolved based on customer's tenancy and OCI Console navigation. Default value defined in the terraform configuration is overwritten by the value specified in ORM.

| Static Types | Description |
| :----------- | :---------- |
| array | List of values |
| boolean | `true` or `false` |
| enum | List of static sorted values |
| integer | Integer  |
| number | Number |
| string | Text |
| password | Hidden Text*  |
| datetime | Current Date Time |

***Note**: variable is visible as plaintext in the terraform state file

| Dynamic Types | Description | Depends on | Filter |
| :------------ | :---------- | :--------- | :----- |
| oci:identity:region:name | OCI Region | | |
| oci:identity:compartment:id | Compartment Id | | |
| oci:core:image:id | List of values | | |
| oci:core:instanceshape:name | List of Compute Shapes | compartmentId  | imageId |
| oci:core:vcn:id | List of VCNs in the existing region  | compartmentId | |
| oci:core:subnet:id | List of Subnets | vcnId compartmentId | hidePublicSubnet hidePrivateSubnet hideRegionalSubnet hideAdSubnet |
| oci:identity:availabilitydomain:name | Region Availability Domain | compartmentId | |
| oci:identity:faultdomain:name | AD Fault Domains | compartmentId availabilityDomainName | |
| oci:database:dbsystem:id | Oracle DB Systems (Exadata, Bare Metal and VM) | | |
| oci:database:dbhome:id | Oracle DB Systems Home Folder | compartmentId dbSystemId | |
| oci:database:database:id | Oracle DB ID | | |
| oci:database:autonomousdatabase:id | Oracle Autonomous Database ID  | | |

#### Sample Code

```yaml
variables:
  # HIDDEN variables
  tenancy_ocid:
    type: string
    title: Tenancy ID
    description: The Oracle Cloud Identifier (OCID) for your tenancy
    required: true

  region:
    type: oci:identity:region:name
    title: Region
    description: The region in which to create all resources
    required: true

# MARKETPLACE VARIABLES
  mp_listing_id:
    type: string
    required: true
    description: Marketplace Listing ID

  mp_listing_resource_id:
    type: oci:core:image:id
    required: true
    description: Marketplace Image OCID
    dependsOn:
      compartmentId: compute_compartment_ocid

  mp_listing_resource_version:
    type: string
    required: true
    description: Marketplace Listing package version

  availability_domain_number:
    type: string
    required: false
    description: Availability Domain Number

# COMPUTE VARIABLES
  compute_compartment_ocid:
    type: oci:identity:compartment:id
    required: true
    title: Compute Compartment
    description: The compartment in which to create all Compute resources
    default: compartment_ocid

  availability_domain_name:
    type: oci:identity:availabilitydomain:name
    dependsOn:
      compartmentId: compute_compartment_ocid
    required: true
    default: 1
    title: Availability Domain
    description: Availability Domain

  ssh_public_key:
    type: string
    required: true
    title: Public SSH Key string
    description: Public SSH Key to access VM via SSH

  vm_display_name:
    type: string
    required: true
    title: Instance Name
    description: The name of the Instance

  vm_compute_shape:
    type: oci:core:instanceshape:name
    default: VM.Standard2.4
    title: Compute Shape
    required: true
    dependsOn:
      compartmentId: compute_compartment_ocid
      imageId: mp_listing_resource_id

  hostname_label:
    type: string
    required: false
    title: DNS Hostname Label


# NETWORK CONFIGURATION VARIABLES
  network_compartment_ocid:
    type: oci:identity:compartment:id
    required: true
    title: Network Compartment
    description: The compartment in which to create all Network resources
    default: compartment_ocid

  network_strategy:
    type: enum
    title: Network Strategy
    description: Create or use existing Network Stack (VCN and Subnet)
    enum:
      - "Create New VCN and Subnet"
      - "Use Existing VCN and Subnet"
    required: true
    default: "Create New VCN and Subnet"
  
  network_configuration_strategy:
    visible: #($network_strategy  == ""Create New VCN and Subnet"")
      eq:
        - network_strategy 
        - "Create New VCN and Subnet"
    type: enum
    title: Configuration Strategy
    description: Use recommended configuration or customize it
    enum:
      - "Use Recommended Configuration"
      - "Customize Network Configuration"
    required: true
    default: "Use Recommended Configuration"

# VCN VARIABLES
  vcn_display_name:
    visible: #($network_strategy  == ""Create New VCN and Subnet"") AND (network_configuration_strategy ==  "Customize Network Configuration")
      and:
        - eq:
          - network_strategy
          - "Create New VCN and Subnet"
        - eq:
          - network_configuration_strategy
          - "Customize Network Configuration"
    type: string
    required: true
    title: Name
    description: The name of the new Virtual Cloud Network (VCN)

  vcn_id:
    visible: #($network_strategy  == "Use Existing VCN and Subnet")
      eq:
        - network_strategy
        - "Use Existing VCN and Subnet"
    type: oci:core:vcn:id
    dependsOn:
      compartmentId: network_compartment_ocid
    required: true
    title: Existing VCN
    description: An existing Virtual Cloud Network (VCN) in which to create the compute instances, network resources, and load balancers. If not specified, a new VCN is created.

  vcn_cidr_block:
    visible: #($network_strategy  == ""Create New VCN and Subnet"") AND (network_configuration_strategy ==  "Customize Network Configuration")
      and:
        - eq:
          - network_strategy
          - "Create New VCN and Subnet"
        - eq:
          - network_configuration_strategy
          - "Customize Network Configuration"
    type: string
    required: true
    pattern: "^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\/(3[0-2]|[1-2]?[0-9])$"
    title: CIDR Block
    description: The CIDR of the new Virtual Cloud Network (VCN). If you plan to peer this VCN with another VCN, the VCNs must not have overlapping CIDRs.

  vcn_dns_label:
    visible: #($network_strategy  == ""Create New VCN and Subnet"") AND (network_configuration_strategy ==  "Customize Network Configuration")
      and:
        - eq:
          - network_strategy
          - "Create New VCN and Subnet"
        - eq:
          - network_configuration_strategy
          - "Customize Network Configuration"
    type: string
    required: true
    title: DNS Label
    maxLenght: 15
    description: VCN DNS Label. Only letters and numbers, starting with a letter. 15 characters max.

# MANAGEMENT SUBNET VARIABLES
  mgmt_subnet_type:
    visible: #($network_strategy  == ""Create New VCN and Subnet"")
      eq:
        - network_strategy
        - "Create New VCN and Subnet"
    type: enum
    title: Subnet Type
    description: Choose between private and public subnets
    enum:
      - "Private Subnet"
      - "Public Subnet"
    required: true
    default: "Public Subnet"

  mgmt_subnet_display_name:
    visible: #($network_strategy  == ""Create New VCN and Subnet"")
      eq:
        - network_strategy
        - "Create New VCN and Subnet"
    type: string
    required: true
    title: Name
    description: The name of the new Management Subnet

  mgmt_subnet_cidr_block:
    visible: #($network_strategy  == ""Create New VCN and Subnet"")
      eq:
        - network_strategy
        - "Create New VCN and Subnet"
    type: string
    pattern: "^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]).(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\/(3[0-2]|[1-2]?[0-9])$"
    required: true
    title: CIDR Block
    description: The CIDR of the new Subnet. The new subnet's CIDR should not overlap with any other subnet CIDRs.

  mgmt_subnet_id:
    visible: #($network_strategy  == "Use Existing VCN and Subnet")
      eq:
        - network_strategy
        - "Use Existing VCN and Subnet"
    type: oci:core:subnet:id
    dependsOn:
      vcnId: vcn_id
      compartmentId: network_compartment_ocid
      hidePublicSubnet: false
      hidePrivateSubnet: false
      hideRegionalSubnet: false
      hideAdSubnet: true
    default: ''
    required: true
    title: Existing Subnet
    description: An existing Management subnet. This subnet must already be present in the chosen VCN.

  mgmt_subnet_dns_label:
    visible: #($network_strategy  == ""Create New VCN and Subnet"")
      eq:
        - network_strategy 
        - "Create New VCN and Subnet"
    type: string
    required: true
    title: DNS Label
    maxLenght: 15
    description: Subnet DNS Label. Only letters and numbers, starting with a letter. 15 characters max.

```

### 4. Terraform Outputs

#### Fields

| Name | Description |
| :--- | :---------- |
| outputs | Top level identifier of Terraform `outputs` section |
| `<output_variable_name>` | The name of the output variable declared in the Terraform template.|
| type | Output Variable type: `link`, `csv`, `ocid` |
| title | Label of the Output variable |
| displayText | Tooltip with the description of the variable |
| visible | set the visibility of a variable - use a boolean or an expression |

#### Sample Code

```yaml
outputs:
  instance_mgmt_https_url:
    type: link
    title: Open Management URL
    visible: false

  instance_mgmt_public_ip:
    type: link
    title: Management Public IP
    visible: #($mgmt_subnet_type == "Public Subnet")
      eq:
      - mgmt_subnet_type
      - "Public Subnet"
  
  instance_mgmt_private_ip:
    type: link
    title: Management Private IP
    visible: true

  public_ips_csv:
    type: csv
    title: Public IPs

  load_balancer_ocid:
    type: ocid
    title: Load Balancer

```

### 5. Primary Output Button

#### Fields

| Name | Description |
| :--- | :----------|
| primaryOutputButton | Output Variable linked to the Marketplace Action Button in the Instance Tab (Compute UI) |

#### Sample Code

```yaml
primaryOutputButton: instance_mgmt_https_url
```

### 6.Output Groups

Use this section to declare all Terraform Output variables that are presented in your Template. All variables in the Terraform Root Module should be declared.


#### Fields

| Name | Description |
| :--- | :---------- |
| outputGroups | Top level identifier of `outputGroups` section |
| title | Title of the Output Variables Group  |
| outputs | Terraform output variables |
| `<output_variable>` | Name of the Output Variable |

#### Sample Code

```yaml
outputGroups:
  - title: Schema Registry
    outputs:
      - schemaRegistryUrl
      - schemaRegistryPublicIps
      - schemaRegistryInstances
      - schemaRegistryLoadBalancer


  - title: Broker / Connect
    outputs:
      - brokerPublicIps
      - brokerInstances
      - connectUrl
      - connectPublicIps
      - restUrl
```
