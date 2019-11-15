import requests
import base64
import yaml
import json

action_api_uri_dic = []
access_token = ''
creds = []
api_url = "https://ocm-apis-cloud.oracle.com/"
form_data_api_headers = ''
put_api_headers = ''
get_api_headers = ''

class Config:

    listingVersionId = None
    artifactId = None
    packageVersionId = None
    termsId = None
    termsVersionId = None
    action = None
    access_token = None

    def __init__(self, partnerName):
        if self.access_token is None:
            set_access_token(partnerName)

def bind_action_dic(config):
    global action_api_uri_dic
    action_api_uri_dic = {
        "get_listingVersions": "appstore/publisher/v1/listings",
        "get_listingVersion": f"appstore/publisher/v1/applications/{config.listingVersionId}",
        "get_artifacts": "appstore/publisher/v1/artifacts",
        "get_artifact": f"appstore/publisher/v1/artifacts/{config.artifactId}",
        "get_applications": "appstore/publisher/v1/applications",
        "get_application": f"appstore/publisher/v1/applications/{config.listingVersionId}",
        "get_listing_packages": f"appstore/publisher/v2/applications/{config.listingVersionId}/packages",
        "get_application_packages": f"appstore/publisher/v2/applications/{config.listingVersionId}/packages",
        "get_application_package": f"appstore/publisher/v2/applications/{config.listingVersionId}/packages/{config.packageVersionId}",
        "get_terms": "appstore/publisher/v1/terms",
        "get_terms_version": f"appstore/publisher/v1/terms/{config.termsId}/version/{config.termsVersionId}",
        "create_listing": f"appstore/publisher/v1/applications",
        "update_stack": f"appstore/publisher/v1/applications/{config.listingVersionId}/version",
        "new_package_version": f"appstore/publisher/v2/applications/{config.listingVersionId}/packages/{config.packageVersionId}/version",
    }

def set_access_token(partnerName):
    global access_token
    global creds
    global form_data_api_headers
    global get_api_headers
    global put_api_headers
    with open(partnerName + "_creds.yaml", 'r') as stream:
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

    form_data_api_headers = {'Content-Type': 'multipart/form-data',
                             'charset': 'UTF-8',
                             'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}

    put_api_headers = {'charset': 'UTF-8',
                             'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}

    get_api_headers = {'Content-Type': 'application/json', 'charset': 'UTF-8',
                   'X-Oracle-UserId': creds['user_email'], 'Authorization': f"Bearer {access_token}"}

def do_get_action(config):
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    r = requests.get(uri, headers=get_api_headers)
    r_json = json.loads(r.text)
    return r_json

def get_new_versionId(config):
    config.action = "update_stack"
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    r = requests.post(uri, headers=get_api_headers)
    r_json = json.loads(r.text)
    return r_json["entityId"]

def get_new_packageId(config, newVersionId):
    config.action = "get_application_packages"
    config.listingVersionId = newVersionId
    r = do_get_action(config)
    return r["items"][0]["Package"]["id"]

def get_new_packageVersionId(config, newVersionId, newPackageId):
    config.action = "new_package_version"
    config.listingVersionId = newVersionId
    config.packageVersionId = newPackageId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    r = requests.patch(uri, headers=get_api_headers)
    r_json = json.loads(r.text)
    return r_json["entityId"]

def update_versioned_package_version(config, newPackageVersionId, versionString):
    config.action = "get_application_package"
    config.packageVersionId = newPackageVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    body = '{"version": "' + versionString + '", "description": "Description of package", "serviceType": "OCIOrchestration"}'
    payload = {'json': (None, body)}
    r = requests.put(uri, headers=put_api_headers, files=payload)
    r_json = json.loads(r.text)
    return r_json["message"]

def create_new_artifact(config, versionString, fileName):
    config.action = "get_artifacts"
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    body = '{"name": "TF_' + versionString + '", "artifactType:": "TERRAFORM_TEMPLATE"}'
    payload = {'json': (None, body)}
    files = {'file': open(fileName, 'rb')}
    r = requests.post(uri, headers=put_api_headers, files=files, data=payload)
    r_json = json.loads(r.text)
    return r_json["entityId"]

def associate_artifact_with_package(config, artifactId, newPackageVersionId, versionString):
    with open("newArtifact", "r") as file_in:
        body = file_in.read()
    body.replace("%%ARTID%%", artifactId)
    body.replace("%%VERS%%", versionString)
    body_json = json.loads(body)
    config.action = "get_application_package"
    config.packageVersionId = newPackageVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    r = requests.put(uri, headers=form_data_api_headers, json=body_json)
    r_json = json.loads(r.text)
    return r_json["message"]

def create_listing(config):

    apicall = f"appstore/publisher/v1/applications"
    with open("testlisting.payload", "r") as file_in:
        body = file_in.read()
    body_json = json.loads(body)
    r = requests.post(api_url + apicall, headers=get_api_headers, json=body_json)
    print(r.text)
    r_json = json.loads(r.text)
    print(json.dumps(r_json, indent=4, sort_keys=False))

