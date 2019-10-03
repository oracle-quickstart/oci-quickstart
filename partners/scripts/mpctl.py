import yaml
import io
import base64
import requests
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('creds',
                    help='the name of the creds file to use')
args = parser.parse_args()

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
r_dic = json.loads(r.text)

access_token = r_dic['access_token']

api_url = "https://ocm-apis-cloud.oracle.com/"
api_headers = {'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}


get_listings_apicall = "appstore/publisher/v1/listings"

r = requests.get(api_url + get_listings_apicall, headers=api_headers)
r_dic = json.loads(r.text)

print(json.dumps(r_dic, indent=4, sort_keys=False))
