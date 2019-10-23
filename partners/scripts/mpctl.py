import yaml
import io
import base64
import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-creds',
                    help='the name of the creds file to use')
parser.add_argument('-action',
                    help='the action to perform')
parser.add_argument('-id', type=int,
                    help='the id to act on')


args = parser.parse_args()


action_api_uri = { "get_listings" : "appstore/publisher/v1/listings",
  "get_packages" : "appstore/publisher/v1/artifacts",
  "get_package" : f"appstore/publisher/v1/artifacts/{args.id}",
  "get_applications" : "appstore/publisher/v1/applications",
  "get_application" : f"appstore/publisher/v1/applications/{args.id}",
  "get_listing" : f"appstore/publisher/v1/applications/{args.id}",
  "get_listing_package" : f"appstore/publisher/v1/applications/{args.id}/packages",
  "get_application_package" : f"appstore/publisher/v1/applications/{args.id}/packages",
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
  api_url = "https://ocm-apis-cloud.oracle.com/"
  api_headers = {'X-Oracle-UserId': creds['user_email'],      'Authorization': f"Bearer {access_token}"}
  apicall = action_api_uri[args.action]
  r = requests.get(api_url + apicall, headers=api_headers)
  r_json = json.loads(r.text)
  
  print(api_url + apicall)
  print(json.dumps(r_json, indent=4, sort_keys=False))
  

if "get" in args.action:
  do_get_action()
  
if "create" in args.action:
  do_create_action()




