import yaml
import io
import base64
import requests
import json
import argparse

action_api_uri_dic = []

parser = argparse.ArgumentParser()
parser.add_argument('-creds',
                    help='the name of the creds file to use')
parser.add_argument('-action',
                    help='the action to perform')
parser.add_argument('-id', type=int,
                    help='the id to act on')
parser.add_argument('-id2', type=int,
                    help='the second id to act on')
parser.add_argument('-filename',
                    help='the name of the TF file')
parser.add_argument('-version_string',
                    help='the new version for update')


args = parser.parse_args()

def bind_action_dic():
  global action_api_uri_dic
  action_api_uri_dic = {
    "get_listings" : "appstore/publisher/v1/listings",
    "get_listing" : f"appstore/publisher/v1/applications/{args.id}",
    "get_artifacts" : "appstore/publisher/v1/artifacts",
    "get_artifact" : f"appstore/publisher/v1/artifacts/{args.id}",
    "get_applications" : "appstore/publisher/v1/applications",
    "get_application" : f"appstore/publisher/v1/applications/{args.id}",
    "get_listing_packages" : f"appstore/publisher/v2/applications/{args.id}/packages",
    "get_application_packages" : f"appstore/publisher/v2/applications/{args.id}/packages",
    "get_application_package" : f"appstore/publisher/v2/applications/{args.id}/packages/{args.id2}",
    "create_listing" : f"appstore/publisher/v1/applications",
    "update_stack" : f"appstore/publisher/v1/applications/{args.id}/version",
    "new_package_version": f"appstore/publisher/v2/applications/{args.id}/packages/{args.id2}/version",
  }

with open(args.creds + "_creds.yaml", 'r') as stream:
    creds = yaml.safe_load(stream)

auth_string = creds['client_id']
auth_string += ':'
auth_string += creds['secret_key']

encoded = base64.b64encode(auth_string.encode('ascii'))
encoded_string = encoded.decode("ascii")

token_url = "https://login.us2.oraclecloud.com:443/oam/oauth2/tokens?grant_type=client_credentials"

auth_headers = {'Content-Type': 'application/x-www-form-urlencoded', 'charset': 'UTF-8', 'X-USER-IDENTITY-DOMAIN-NAME': 'usoracle30650',
        'Authorization': f"Basic {encoded_string}"}

r = requests.post(token_url, headers=auth_headers)

access_token = json.loads(r.text).get('access_token')

class ArtifactVerion:
  details = []

  def __init__(self, details):
    self.details = details


class Artifact:
  versions = []
  resource = []

  def __init__(self, resource):
    self.resource = resource
    self.versions = []
    for property in resource["properties"]:
      args.action = "get_artifact"
      args.id = int(property["value"])
      bind_action_dic()
      uri, r = do_get_action()
      av = ArtifactVerion(r)
      self.versions.append(av)


class Package:

  package = []
  artifacts = []

  def __init__(self, package, listingVersionId):
    self.artifacts = []
    self.package = package["Package"]
    for resource in self.package["resources"]:
      a = Artifact(resource)
      self.artifacts.append(a)


class Listing:

  packageVersions = []
  listing = ''
  lisitingDetails = ''
  packages = []

  def __init__(self, listing):
    self.packages = []
    self.listing = listing
    if "packageVersions" in self.listing:
        self.packageVersions = self.listing["packageVersions"]

    args.action = "get_listing"
    args.id = self.listing["listingVersionId"]
    bind_action_dic()
    uri, self.lisitingDetails = do_get_action()

    args.action = "get_application_packages"
    bind_action_dic()
    packages = []
    uri, packages = do_get_action()

    for package in packages["items"]:
      p = Package(package, args.id)
      self.packages.append(p)



class Partner:

  listings = []

  def __init__(self, listings):
    if "items" in listings:
        for item in listings["items"]:
          l = Listing(item["GenericListing"])
          self.listings.append(l)
    else:
        l = Listing(listings)
        self.listings.append(l)



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
  bind_action_dic()
  if args.id is None:
    args.action = "get_listings"
  else:
    args.action = "get_listing"
  uri, r = do_get_action()
  partner = Partner(r)
  print ("done")

def do_create():
  bind_action_dic()
  pass

def do_update_stack():
    bind_action_dic()
    api_url = "https://ocm-apis-cloud.oracle.com/"
    api_headers = {'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    r = requests.post(uri, headers=api_headers)
    r_json = json.loads(r.text)
    newVersionId = r_json["entityId"]

    args.action = "get_application_packages"
    args.id = newVersionId
    bind_action_dic()
    uri, r = do_get_action()
    newPackageId = r["items"][0]["Package"]["id"]

    args.action = "new_package_version"
    args.id = newVersionId
    args.id2 = newPackageId
    bind_action_dic()
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    api_headers = {'Content-Type': 'application/json', 'charset': 'UTF-8',
                   'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}
    r = requests.patch(uri, headers=api_headers)
    r_json = json.loads(r.text)
    newPackageVersionId = r_json["entityId"]

    args.action = "get_application_package"
    args.id2 = newPackageVersionId
    bind_action_dic()
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    api_headers = {'Content-Type': 'multipart/form-data', 'boundary': '----WebKitFormBoundary7MA4YWxkTrZu0gW', 'charset': 'UTF-8',
                   'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}
    body = '{"version": "' + args.version_string + '", "description": "Description of package", "tncId": "", "serviceType": "OCIOrchestration"}'
    body_json = json.loads(body)
    #r = requests.put(uri, headers=api_headers, json=body_json)
    r = requests.put(uri, headers=api_headers, data=body)
    r_json = json.loads(r.text)
    message = r_json["message"]

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

    with open("newArtifact", "r") as file_in:
        body = file_in.read()

    body.replace("%%ARTID%%", artifactId)
    body.replace("%%VERS%%", args.version_string)
    body_json = json.loads(body)
    args.action = "get_application_package"
    args.id2 = newPackageVersionId
    bind_action_dic()
    apicall = action_api_uri_dic[args.action]
    uri = api_url + apicall
    r = requests.put(uri, headers=api_headers, json=body_json)
    r_json = json.loads(r.text)
    message = r_json["message"]




if "get" in args.action:
  uri, r_json = do_get_action()
  print(uri)
  print(json.dumps(r_json, indent=4, sort_keys=True))

if "create" in args.action:
  do_create()

if "build" in args.action:
  do_build()

if "update_stack" in args.action:
  do_update_stack()




