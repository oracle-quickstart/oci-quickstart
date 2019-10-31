import yaml
import io
import base64
import requests
import json
import argparse

####################################
#
# usage:
#
#
#
#
#
#
#
#
#
#
#
####################################

action_api_uri_dic = []

parser = argparse.ArgumentParser()
parser.add_argument('-creds',
                    help='the name of the creds file to use')
parser.add_argument('-action',
                    help='the action to perform')
parser.add_argument('-listingVersionId', type=int,
                    help='the listing version to act on')
parser.add_argument('-packageVersionId', type=int,
                    help='the package version to act on')
parser.add_argument('-termsId', type=int,
                    help='the terms to act on')
parser.add_argument('-termsVersionId', type=int,
                    help='the terms version to act on')
parser.add_argument('-artifactId', type=int,
                    help='the artifact to act on')
parser.add_argument('-filename',
                    help='the name of the TF file')
parser.add_argument('-version_string',
                    help='the new version for update')

args = parser.parse_args()
access_token = ''
creds = []

def bind_action_dic():
    global action_api_uri_dic
    action_api_uri_dic = {
        "get_listings" : "appstore/publisher/v1/listings",
        "get_listing" : f"appstore/publisher/v1/applications/{args.listingVersionId}",
        "get_artifacts" : "appstore/publisher/v1/artifacts",
        "get_artifact" : f"appstore/publisher/v1/artifacts/{args.artifactId}",
        "get_applications" : "appstore/publisher/v1/applications",
        "get_application" : f"appstore/publisher/v1/applications/{args.listingVersionId}",
        "get_listing_packages" : f"appstore/publisher/v2/applications/{args.listingVersionId}/packages",
        "get_application_packages" : f"appstore/publisher/v2/applications/{args.listingVersionId}/packages",
        "get_application_package" : f"appstore/publisher/v2/applications/{args.listingVersionId}/packages/{args.packageVersionId}",
        "get_terms": "appstore/publisher/v1/terms",
        "get_terms_version": f"appstore/publisher/v1/terms/{args.termsId}/version/{args.termsVersionId}",
        "create_listing" : f"appstore/publisher/v1/applications",
        "update_stack" : f"appstore/publisher/v1/applications/{args.listingVersionId}/version",
        "new_package_version": f"appstore/publisher/v2/applications/{args.listingVersionId}/packages/{args.packageVersionId}/version",
    }

class ArtifactVersion:
  details = []

  def __init__(self, details):
    self.details = details

  def __str__(self):
      ppstring = ''
      ppstring += json.dumps(self.details, indent=4, sort_keys=False)
      return ppstring

class Artifact:
  versions = []
  resource = []

  def __init__(self, resource):
    self.resource = resource
    self.versions = []
    for property in resource["properties"]:
      args.action = "get_artifact"
      args.artifactId = int(property["value"])
      bind_action_dic()
      uri, r = do_get_action()
      av = ArtifactVersion(r)
      self.versions.append(av)

  def __str__(self):
      ppstring = ''
      ppstring += json.dumps(self.resource, indent=4, sort_keys=False)
      for version in self.versions:
          ppstring += str(version)
      return ppstring

class Package:

  package = []
  artifacts = []

  def __init__(self, package):
    self.artifacts = []
    self.package = package["Package"]
    for resource in self.package["resources"]:
      a = Artifact(resource)
      self.artifacts.append(a)

  def __str__(self):
      ppstring = ''
      ppstring += json.dumps(self.package, indent=4, sort_keys=False)
      for artifact in self.artifacts:
          ppstring += str(artifact)
      return ppstring


class Listing:

  packageVersions = []
  listing = ''
  listingDetails = ''
  packages = []

  def __init__(self, listing):
    self.packages = []
    self.listing = listing
    if "packageVersions" in self.listing:
        self.packageVersions = self.listing["packageVersions"]

    args.action = "get_listing"
    args.listingVersionId = self.listing["listingVersionId"]
    bind_action_dic()
    uri, self.listingDetails = do_get_action()

    args.action = "get_application_packages"
    bind_action_dic()
    packages = []
    uri, packages = do_get_action()

    for package in packages["items"]:
      p = Package(package)
      self.packages.append(p)

  def __str__(self):
      ppstring = ''
      ppstring += json.dumps(self.listing, indent=4, sort_keys=False)
      ppstring += json.dumps(self.listingDetails, indent=4, sort_keys=False)
      ppstring += json.dumps(self.packageVersions, indent=4, sort_keys=False)
      for package in self.packages:
          ppstring += str(package)
      return ppstring


class TermVersion():

    termVersion = []

    def __init__(self, termsId, termVersion):
        args.action = "get_terms_version"
        args.termsId = termsId
        args.termsVersionId = termVersion["termsVersionId"]
        bind_action_dic()
        uri, tv = do_get_action()
        self.termVersion = tv

    def __str__(self):
        return json.dumps(self.termVersion, indent=4, sort_keys=False)


class Terms():

    terms = []
    termVersions= []

    def __init__(self, terms):
        self.terms = terms
        self.termVersions = []

        for termVersion in terms["termVersions"]:
            tv = TermVersion(terms["termsId"], termVersion)
            self.termVersions.append(tv)

    def __str__(self):
        ppstring = ''
        ppstring += str(self.terms)
        for termVersion in self.termVersions:
            ppstring += str(termVersion)
        return ppstring


class Partner:

    listings = []
    terms = []

    def __init__(self):
        bind_action_dic()
        if args.listingVersionId is None:
          args.action = "get_listings"
        else:
          args.action = "get_listing"
        uri, listings = do_get_action()

        if "items" in listings:
          for item in listings["items"]:
              l = Listing(item["GenericListing"])
              self.listings.append(l)
        else:
            l = Listing(listings)
            self.listings.append(l)

        args.action = "get_terms"
        bind_action_dic()
        uri, terms = do_get_action()
        if "items" in terms:
          for item in terms["items"]:
              t = Terms(item["terms"])
              self.terms.append(t)
        else:
            t = Terms(terms)
            self.terms.append(t)


        pass


    def __str__(self):
      ppstring = ''
      for listing in self.listings:
          ppstring += str(listing)
      for terms in self.terms:
          ppstring += str(terms)
      return ppstring


def get_access_token():
    global access_token
    global creds
    with open(args.creds + "_creds.yaml", 'r') as stream:
        creds = yaml.safe_load(stream)

    auth_string = creds['client_id']
    auth_string += ':'
    auth_string += creds['secret_key']

    encoded = base64.b64encode(auth_string.encode('ascii'))
    encoded_string = encoded.decode("ascii")

    token_url = "https://login.us2.oraclecloud.com:443/oam/oauth2/tokens?grant_type=client_credentials"

    auth_headers = {'Content-Type': 'application/x-www-form-urlencoded', 'charset': 'UTF-8',
                    'X-USER-IDENTITY-DOMAIN-NAME': 'usoracle30650',
                    'Authorization': f"Basic {encoded_string}"}

    r = requests.post(token_url, headers=auth_headers)

    access_token = json.loads(r.text).get('access_token')


def create_listing():

  api_url = "https://ocm-apis-cloud.oracle.com/"
  api_headers = {'Content-Type': 'application/json', 'charset': 'UTF-8',
    'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}

  apicall = f"appstore/publisher/v1/applications"

  with open ("testlisting.payload", "r") as file_in:
    body = file_in.read()

  body_json = json.loads(body)

  r = requests.post(api_url + apicall, headers=api_headers, json=body_json)

  print (r.text)

  r_json = json.loads(r.text)
  print(json.dumps(r_json, indent=4, sort_keys=False))

def do_get_action():
  bind_action_dic()
  api_url = "https://ocm-apis-cloud.oracle.com/"
  api_headers = {'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}
  apicall = action_api_uri_dic[args.action]
  uri = api_url + apicall
  r = requests.get(uri, headers=api_headers)
  r_json = json.loads(r.text)

  return uri, r_json

def do_build():

  return partner

def do_create():
  bind_action_dic()
  pass

def do_update_stack():

    partner = Partner()

    #tcnId = partner.terms[0].termVersions[0].termVersion["termsVersionId"]
    tcnId = partner.terms[0].termVersions[0].termVersion["contentId"]
    #create a new version for the application listing
    args.action = "update_stack"
    bind_action_dic()
    api_url = "https://ocm-apis-cloud.oracle.com/"
    api_headers = {'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    r = requests.post(uri, headers=api_headers)
    r_json = json.loads(r.text)
    newVersionId = r_json["entityId"]

    #get the package version id needed for package version creation
    args.action = "get_application_packages"
    args.listingVersionId = newVersionId
    bind_action_dic()
    uri, r = do_get_action()
    newPackageId = r["items"][0]["Package"]["id"]

    #create a package version from existing package
    args.action = "new_package_version"
    args.listingVersionId = newVersionId
    args.packageVersionId = newPackageId
    bind_action_dic()
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    api_headers = {'Content-Type': 'application/json', 'charset': 'UTF-8',
                   'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}
    r = requests.patch(uri, headers=api_headers)
    r_json = json.loads(r.text)
    newPackageVersionId = r_json["entityId"]

    #update versioned package details
    args.action = "get_application_package"
    args.packageVersionId = newPackageVersionId
    bind_action_dic()
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    api_headers = {'Content-Type': 'multipart/form-data', 'boundary': '----WebKitFormBoundary7MA4YWxkTrZu0gW', 'charset': 'UTF-8',
                   'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}
    body = '{"version": "' + args.version_string + '", "description": "Description of package", "tncId": "'+ str(tcnId) +'", "serviceType": "OCIOrchestration"}'
    body_json = json.loads(body)
    r = requests.put(uri, headers=api_headers, json=body_json)
    r_json = json.loads(r.text)
    message = r_json["message"]

    # create new artifact
    args.action = "get_artifacts"
    bind_action_dic()
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    body = '{"name": "TF_' + args.version_string + '", "artifactType:": "TERRAFORM_TEMPLATE"}'
    body_json = json.loads(body)
    files = {'upload_file': open('tf.zip', 'rb')}
    r = requests.post(uri, headers=api_headers, json=body_json, files=files)
    r_json = json.loads(r.text)
    artifactId = r_json["entityId"]

    #update versioned package details - associate newly created artifact
    with open("newArtifact", "r") as file_in:
        body = file_in.read()
    body.replace("%%ARTID%%", artifactId)
    body.replace("%%VERS%%", args.version_string)
    body_json = json.loads(body)
    args.action = "get_application_package"
    args.packageVersionId = newPackageVersionId
    bind_action_dic()
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    r = requests.put(uri, headers=api_headers, json=body_json)
    r_json = json.loads(r.text)
    message = r_json["message"]
    return message

get_access_token()

if "get" in args.action:
  uri, r_json = do_get_action()
  print(uri)
  print(json.dumps(r_json, indent=4, sort_keys=True))

if "create" in args.action:
  do_create()

if "build" in args.action:
  partner = Partner()
  print(partner)

if "update_stack" in args.action:
  print(do_update_stack())




