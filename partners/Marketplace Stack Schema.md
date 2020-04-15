# Marketplace Stack Schema
Oracle Cloud Infrastructure Marketplace is an online store that offers applications specifically for customers of Oracle Cloud Infrastructure. In the Oracle Cloud Infrastructure Marketplace catalog, customers can find and launch Images and Stacks from Oracle or trusted partners. These Marketplace Images or Stacks are deployed into the customer's tenancy.

Marketplace Images are templates of virtual hard drives that determine the operating system and software to run on an instance. Publishers will publish a [Custom Image](https://docs.cloud.oracle.com/iaas/Content/Compute/Tasks/managingcustomimages.htm) as an Artifact in the [Marketplace Partner Portal](https://partner.cloudmarketplace.oracle.com/partner/index.html).

Marketplace Stacks are composed by Terraform configuration files (templates) and a JSON/Yaml variable schema file packaged all together in a zip file.  A Stack run as a job in the OCI [Resource Manager](https://docs.cloud.oracle.com/iaas/Content/ResourceManager/Concepts/resourcemanager.htm) service.

A configuration is a set of one or more Terraform configuration (.tf) file written in HCL,  that specify the Oracle Cloud Infrastructure resources, including resource metadata, and other important information, like data source definitions and variables declarations.

Terraform variables are defined as environment variables, command line arguments or placed into TFVars file when they are launched from Terraform CLI. Running a standalone ORM Stack (not Marketplace related) is possible to set variables at the time a Stack is created via OCI CLI, by specifying a json file.

In order to enable any user - technical or non-technical to launch a Marketplace Stack directly from the OCI console without depending on any CLI,  Marketplace/ORM provided a unique feature to enable publishers to create a custom UI for their Stacks where they can create a Form based on the same look and feel of OCI console and also can link the OCI created resources with the Marketplace listing that originated it.

## Marketplace Stack Requirements

| #    | Description |
| :--- |    :----    |
| 1    | Schema file is baed on [YAML](https://yaml.org/)  |
| 2    | All variables declared in the schema file MUST exist in the Terraform configuration.   |
| 3    | The `tenancy_ocid` and `region` variables must be declared as part of the schema, but placed in a hidden `variableGroups` section as their values are set automatically by ORM based on customer selections in the OCI console. |
| 4    | You must create a different VariablesGroups section for grouping similar OCI Services, e.g. Network, Storage, Compute. That will make the user experience similar to standard OCI UI. For example, create a `variableGroups` section for Network resources and put all variables that manage network (VCN, Subnets, etc) into that group.   |

## YAML Schema Building Blocks

### 1.Marketplace Application Information tab

This block contains general information related to the listing that is displayed in the Application Information tab in the OCI Console, e.g. application description, logo/icon URL, listing-id, content-language and  some boilerplate code related to the schema version.

#### Fields
| Name   | Description |
| :--- |    :----    |
| title    | Title of the listing displayed in the OCI console - Application Information tab |
| description    | Sub Title shown in Application Information tab. |
| schemaVersion  | YAML Schema version. Fixed Value = `1.1.0` |
| version    | Marktetplace API Version. Fixed Value = `20190404` |
| logoUrl    | URL of Logo Icon used on Application Information tab. Logo must be 130x130 pixels. |
| source    | Used in Application Information tab to Hyperlink Title and Logo to the Marketplace Listing. Also used to link to Listing Usage section for "View Instructions".|
| locale    | Listing Locale, e.g. `en` for English |

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

### 2.VariableGroups

#### Fields

| Name   | Description |
| :--- |    :----    |
| variableGroups    | Top level identifier of `variableGroups` section |
| title | Title of the Group |
| variables | list of variables that are presented/hidden in this group |
| visible | set the visibility of variableGroups block - use a boolean or an expression|

#### Sample Code

```yaml
variableGroups:
  - title: "Instance"
    variables:
      - ${nodeCount}
      - ${nodeShapes}
      - ${availability}
    visible: true
  - title: "Subnet"
    variables:
      - ${myVcn}
    visible:
      or:
        - ${useExistingVcn}
        - and:
          - and:
            - true
            - true
          - not:
            - false
```

### 3.Terraform Variables

Use this section to declare all Terraform Input variables that are presented in your Template. All variables in the Terraform Root Module should be declared.

#### Fields

 Name   | Description |
| :--- |    :----    |
| variables    | Top level identifier of `variables` section |
| `<variable_name>` | The name of the input variable declared in the Terraform template. |
| type | Definition of the variable type supported by the schema. This is not a Terraform variable type as the OCI Marketplace schema support dynamic types that will automatically lookup for OCI resource types. See Dynamic types.|
| minLenght | Minimum Lenght of the Variable |
| maxLenght | Maximum Lenght of the Variable |
| pattern | Regex pattern |
| title | Label of the variable |
| description | Tooltip with the description of the variable |
| default | Variable default value |
| required | set the variable requirement -  use a boolean or an expression |
| visible | set the visibility of a variable - use a boolean or an expression |

#### Variable Types

Variable Types in the Schema definition are statically or dynamically resolved based on customer's tenancy and OCI Console navigation.

| Static Types | Description |
| :--- |    :----    |
| array    | List of values |
| boolean    | `true` or `false` |
| enum    | List of static sorted values |
| integer    | Integer  |
| number    | Number |
| string    | Text |
| password    | Hidden Text |
| datetime    | Current Date Time |


| Dynamic Types | Description | Depends on | Filter |
| :--- |    :----    | :---- |  :---- |
| oci:identity:region:name    | OCI Region | | |
| oci:identity:compartment:id    | Compartment Id | | |
| oci:core:image:id    | List of values | | |
| oci:core:instanceshape:name    | List of Compute Shapes | compartmentId  | imageId |
| oci:core:vcn:id    | List of VCNs in the existing region  | compartmentId | |
| oci:core:subnet:id    | List of Subnets | vcnId compartmentId| hidePublicSubnet hidePrivateSubnet hideRegionalSubnet hideAdSubnet   |
| oci:identity:availabilitydomain:name    | Region Availability Domain | compartmentId | |
| oci:identity:faultdomain:name    | AD Fault Domains | compartmentId availabilityDomainName | |
| oci:database:dbsystem:id    | Oracle DB Systems (Exadata, Bare Metal and VM) | | |
| oci:database:dbhome:id    | Oracle DB Systems Home Folder | compartmentId dbSystemId | |
| oci:database:database:id    | Oracle DB ID | | |
| oci:database:autonomousdatabase:id    | Oracle Autonomous Database ID  | | |



#### Sample Code

```yaml
variables:
  # string field
  username:
    type: string
    minLength: 1
    maxLength: 255
    pattern: "^[a-z][a-zA-Z0-9]+$"
    # title is used as the label if present
    title: Username
    # description used as the tooltip if present
    description: Enter your username
    default: admin
    required: true

myVcn:
    type: oci:core:vcn:id
    dependsOn:
      compartmentId: ${vcnCompartment}
    visible:
      or:
        - ${useExistingVcn}
        - and:
          - and:
            - true
            - true
          - not:
            - false

  subnetCompartment:
    type: oci:identity:compartment:id
    visible: ${useExistingVcn}

  mySubnet:
    type: oci:core:subnet:id
    dependsOn:
      compartmentId: ${subnetCompartment}
      vcnId: ${myVcn}
    visible: ${useExistingVcn}

  mySubnetWithFilter:
    type: oci:core:subnet:id
    dependsOn:
      compartmentId: ${subnetCompartment}
      vcnId: ${myVcn}
      hidePublicSubnet: ${hide_public_subnet}
      hidePrivateSubnet: ${hide_private_subnet}
      hideRegionalSubnet: ${hide_regional_subnet}
      hideAdSubnet: ${hide_ad_subnet}
    visible: ${useExistingVcn}
```

### 4.Terraform Outputs

#### Fields

 Name   | Description |
| :--- |    :----    |
| outputs    | Top level identifier of Terraform `outputs` section |
| `<output_variable_name>`    | The name of the output variable declared in the Terraform template.|
| type    | Output Variable type: `link`, `csv`, `ocid` |
| title | Label of the Output variable |
| displayText | Tooltip with the description of the variable |
| visible    | set the visibility of a variable - use a boolean or an expression |


#### Sample Code

```yaml
outputs:
  controlCenterUrl:
    type: link
    title: Control Center
    displayText: Control Center
    visible: false


  schemaRegistryUrl:
    type: link
    title: Schema Registry
    displayText: Schema Registry

  schemaRegistryPublicIps:
    type: csv
    title: Public IPs

  schameRegistryLoadBalancer:
    type: ocid
    title: Load Balancer

  brokerPublicIps:
    type: csv

  connectUrl:
    type: link
    title: Connect
    displayText: Connect

  connectPublicIps:
    type: csv
    title: Public IPs

  restUrl:
    type: link
    title: Rest API
```

### 5.Primary Output Button

#### Fields

 Name   | Description |
| :--- |    :----    |
| primaryOutputButton    | Output Variable linked to the Marketplace Action Button in the Instance Tab (Compute UI) |


#### Sample Code

```yaml
primaryOutputButton: ${controlCenterUrl}
```

### 6.Output Groups

Use this section to declare all Terraform Output variables that are presented in your Template. All variables in the Terraform Root Module should be declared.


#### Fields

 Name   | Description |
| :--- |    :----    |
| outputGroups    | Top level identifier of `outputGroups` section |
| title    | Title of the Output Variables Group  |
| outputs    | Terraform output variables |
| `<output_variable>` | Name of the Output Variable |

#### Sample Code

```yaml
outputGroups:
  - title: Schema Registry
    outputs:
      - ${schemaRegistryUrl}
      - ${schemaRegistryPublicIps}
      - ${schemaRegistryInstances}
      - ${schemaRegistryLoadBalancer}


  - title: Broker / Connect
    outputs:
      - ${brokerPublicIps}
      - ${brokerInstances}
      - ${connectUrl}
      - ${connectPublicIps}
      - ${restUrl}
```
