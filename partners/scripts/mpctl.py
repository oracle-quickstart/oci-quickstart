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
    for item in listings["items"]:
      l = Listing(item["GenericListing"])
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
  args.action = "get_listings"
  uri, r = do_get_action()
  partner = Partner(r)
  print (partner)

def do_create_action():
  bind_action_dic()
  pass

if "get" in args.action:
  uri, r_json = do_get_action()
  print(uri)
  print(json.dumps(r_json, indent=4, sort_keys=True))

if "create" in args.action:
  do_create_action()

if "build" in args.action:
  do_build()




