from time import gmtime, strftime
import datetime
import requests
import base64
import yaml
import json
import os.path
import re

action_api_uri_dic = {}
access_token = ''
creds = {}
api_url = 'https://ocm-apis-cloud.oracle.com/'
picCompartmentOcid = 'ocid1.compartment.oc1..aaaaaaaaxrcshrhpq6exsqibhdzseghk4yjgrwxn3uaev6poaek2ooz4n7eq'
picTenancyId = '59030347'
api_headers = {}

class Config:

    listingVersionId = None
    artifactId = None
    packageVersionId = None
    termsId = None
    termsVersionId = None
    action = None
    access_token = None
    imageOcid = None
    credsFile = None
    versionString = None
    commitHash = None

    def __init__(self, credsFile):
        if self.access_token is None:
            set_access_token(credsFile)

class Request:
    class __Request:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __str__(self):
            return repr(self)

    instance = None

    def  __init__(self, **kwargs):
        if not Request.instance:
            Request.instance = Request.__Request(**kwargs)
        else:
            Request.instance.kwargs = {**Request.instance.kwargs, **kwargs}

    def get(self):
        r = requests.get(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'])
        if r.status_code > 299:
            print(r.text)
        return json.loads(r.text)

    def post(self, files=None, data=None):

        #### neither files nor data
        if files is None and data is None:
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'])

        #### data but no files
        elif data is not None and files is None:
            Request.instance.kwargs['api_headers']['Content-Type'] = 'application/json'
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'], data = data)
            del Request.instance.kwargs['api_headers']['Content-Type']

        #### files and data
        elif data is not None and files is not None:
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'],
                              files=files, data=data)

        #### only files
        else:
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'],
                              files=files)

        if r.status_code > 299:
            print(r.text)
        return json.loads(r.text)

    def patch(self, data = None, is_json = False):
        if data is None:
            r = requests.patch(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'])
        else:
            if is_json:
                Request.instance.kwargs['api_headers']['Content-Type'] = 'application/json'
            r = requests.patch(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'], data=data)
            del Request.instance.kwargs['api_headers']['Content-Type']

        if r.status_code > 299:
            print(r.text)
        return json.loads(r.text)

    def put(self, data):
        r = requests.put(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'], files=data)
        if r.status_code > 299:
            print(r.text)
        return json.loads(r.text)

def bind_action_dic(config):
    global action_api_uri_dic
    action_api_uri_dic = {
        'get_listingVersions': 'appstore/publisher/v1/listings',
        'get_listingVersion': f'appstore/publisher/v1/applications/{config.listingVersionId}',
        'get_artifacts': 'appstore/publisher/v1/artifacts',
        'get_artifact': f'appstore/publisher/v1/artifacts/{config.artifactId}',
        'get_applications': 'appstore/publisher/v1/applications',
        'get_application': f'appstore/publisher/v1/applications/{config.listingVersionId}',
        'get_listing_packages': f'appstore/publisher/v2/applications/{config.listingVersionId}/packages',
        'get_application_packages': f'appstore/publisher/v2/applications/{config.listingVersionId}/packages',
        'get_application_package': f'appstore/publisher/v2/applications/{config.listingVersionId}/packages/{config.packageVersionId}',
        'get_terms': 'appstore/publisher/v1/terms',
        'get_terms_version': f'appstore/publisher/v1/terms/{config.termsId}/version/{config.termsVersionId}',
        'create_listing': f'appstore/publisher/v1/applications',
        'create_new_version': f'appstore/publisher/v1/applications/{config.listingVersionId}/version',
        'new_package_version': f'appstore/publisher/v2/applications/{config.listingVersionId}/packages/{config.packageVersionId}/version',
        'upload_icon': f'appstore/publisher/v1/applications/{config.listingVersionId}/icon',
    }

def set_access_token(credsFile):
    global access_token
    global creds
    global api_headers

    with open(credsFile, 'r') as stream:
        creds = yaml.safe_load(stream)

    auth_string = creds['client_id']
    auth_string += ':'
    auth_string += creds['secret_key']

    encoded = base64.b64encode(auth_string.encode('ascii'))
    encoded_string = encoded.decode('ascii')

    token_url = 'https://login.us2.oraclecloud.com:443/oam/oauth2/tokens?grant_type=client_credentials'

    auth_headers = {}
    auth_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    auth_headers['charset'] = 'UTF-8'
    auth_headers['X-USER-IDENTITY-DOMAIN-NAME'] = 'usoracle30650'
    auth_headers['Authorization'] = f'Basic {encoded_string}'

    r = requests.post(token_url, headers=auth_headers)

    access_token = json.loads(r.text).get('access_token')
    api_headers['charset'] = 'UTF-8'
    api_headers['X-Oracle-UserId'] = creds['user_email']
    api_headers['Authorization'] = f'Bearer {access_token}'

    request = Request(api_headers = api_headers)

def sanitize_name(name):
    return re.sub('[^a-zA-Z0-9_\.\-\+ ]+', '', name)

def find_file(file_name):
    # github actions put files in a chroot jail, so we need to look in root
    file_name = file_name if os.path.isfile(file_name) \
        else '/{}'.format(file_name) if os.path.isfile('/{}'.format(file_name)) \
        else 'marketplace/{}'.format(file_name) if os.path.isfile('marketplace/{}'.format(file_name)) \
        else '/marketplace/{}'.format(file_name) if os.path.isfile('/marketplace/{}'.format(file_name)) \
        else file_name #return the original file name if not found so the open can throw the exception
    return file_name

def get_time_stamp():
    return strftime("%Y%m%d%H%M", gmtime())

def do_get_action(config):
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    request = Request(uri = uri)
    result = request.get()
    return result

def get_new_versionId(config):
    config.action = 'create_new_version'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    request = Request(uri = uri)
    result = request.post()
    return result['entityId'] if 'entityId' in result else result

def update_version_metadata(config, newVersionId):
    config.action = 'get_listingVersion'
    config.listingVersionId = newVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    file_name = find_file('metadata.yaml')
    if not os.path.isfile(file_name):
        return f'metadata file metadata.yaml not found. skipping metadata update.'
    with open(file_name,  'r') as stream:
        metadata = yaml.safe_load(stream)

    updateable_items = ['longDescription','name','shortDescription','systemRequirements','tagLine','tags','usageInformation']

    for k in list(metadata.keys()):
        if k not in updateable_items:
            del metadata[k]

    body = json.dumps(metadata)

    request = Request(uri = uri)
    result = request.patch(body, True)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result

def get_packageId(config, newVersionId):
    config.action = 'get_application_packages'
    config.listingVersionId = newVersionId
    r = do_get_action(config)
    return r['items'][0]['Package']['id']

def get_new_packageVersionId(config, newVersionId, packageId):
    config.action = 'new_package_version'
    config.listingVersionId = newVersionId
    config.packageVersionId = packageId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall

    request = Request(uri=uri)
    result = request.patch()

    return result['entityId'] if 'entityId' in result else result

def update_versioned_package_version(config, newPackageVersionId):
    config.action = 'get_application_package'
    config.packageVersionId = newPackageVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    if config.imageOcid is None:
        service_type = 'OCIOrchestration'
    else:
        service_type = 'OCI'
    body = {}
    body['version'] = sanitize_name(config.versionString) + ' ' + get_time_stamp()
    body['description'] = config.versionString
    body['serviceType'] = service_type
    payload = {'json': (None, json.dumps(body))}

    request = Request(uri=uri)
    result = request.put(payload)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result

def set_package_version_as_default(config, newVersionId, newPackageVersionId):
    config.action = 'get_application_package'
    config.listingVersionId = newVersionId
    config.packageVersionId = newPackageVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    body = {}
    body['action'] = 'default'
    request = Request(uri=uri)
    result = request.patch(json.dumps(body), True)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result

def create_new_stack_artifact(config, fileName):
    config.action = 'get_artifacts'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    body={}
    body['name'] = config.commitHash if config.commitHash is not None \
        else sanitize_name(config.versionString) + ' ' + get_time_stamp()
    body['artifactType'] = 'TERRAFORM_TEMPLATE'
    payload = {'json': (None, json.dumps(body))}
    index = fileName.rfind('/')
    name = fileName[index+1:]
    files = {'file': (name, open(fileName, 'rb'))}
    request = Request(uri = uri)
    result = request.post(files, payload)
    return result['entityId'] if 'entityId' in result else result

def create_new_image_artifact(config, old_listing_artifact_version):
    config.action = 'get_artifacts'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    if old_listing_artifact_version is not None:
        new_version = {key:old_listing_artifact_version[key] for key in ['name', 'artifactType', 'source', 'artifactProperties']}
        new_version['name'] = sanitize_name(config.versionString) + ' ' + get_time_stamp()
        new_version['source']['uniqueIdentifier'] = config.imageOcid
        new_version['artifactType'] = 'OCI_COMPUTE_IMAGE'
    else:
        new_version = {}
        new_version['name'] = sanitize_name(config.versionString) + ' ' + get_time_stamp()
        new_version['artifactType'] = 'OCI_COMPUTE_IMAGE'
        new_version['source'] = {}
        new_version['source']['regionCode'] = 'us-ashburn-1'
        new_version['source']['uniqueIdentifier'] = config.imageOcid
        new_version['artifactProperties'] = [{},{}]
        new_version['artifactProperties'][0]['artifactTypePropertyName'] = 'compartmentOCID'
        new_version['artifactProperties'][0]['value'] = picCompartmentOcid
        new_version['artifactProperties'][1]['artifactTypePropertyName'] = 'ociTenancyID'
        new_version['artifactProperties'][1]['value']  = picTenancyId

    request = Request(uri = uri)
    data = json.dumps(new_version)
    result = request.post(None, data)
    return result['entityId'] if 'entityId' in result else result

def associate_artifact_with_package(config, artifactId, newPackageVersionId):

    body = {}
    body['resources'] = [{}]
    body['resources'][0]['serviceType'] = 'OCIOrchestration' if config.imageOcid is None else 'OCI'
    body['resources'][0]['type'] = 'terraform' if config.imageOcid is None else 'ocimachineimage'
    body['resources'][0]['properties'] = [{}]
    body['resources'][0]['properties'][0]['name'] = 'artifact'
    body['resources'][0]['properties'][0]['value'] = artifactId
    body['resources'][0]['properties'][0]['valueProperties'] = [{}]
    body['resources'][0]['properties'][0]['valueProperties'][0]['name'] = 'name'
    body['resources'][0]['properties'][0]['valueProperties'][0]['value'] = sanitize_name(config.versionString)

    payload = {'json': (None, json.dumps(body))}
    config.action = 'get_application_package'
    config.packageVersionId = newPackageVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    request = Request(uri = uri)
    result = request.put(payload)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result

def submit_listing(config):
    autoApprove = 'true'
    while (True):
        config.action = 'get_listingVersion'
        bind_action_dic(config)
        apicall = action_api_uri_dic[config.action]
        uri = api_url + apicall
        body = {}
        body['action'] = 'submit'
        body['note'] = 'submitting new version'
        body['autoApprove'] = autoApprove
        data = json.dumps(body)
        request = Request(uri = uri)
        result = request.patch(data, True)
        if 'message' in result:
            return result['message']
        if autoApprove == 'false':
            return 'this partner has not yet been approved for auto approval. please contact MP admin.'
        else:
            autoApprove = 'false'

def publish_listing(config):
    config.action = 'get_listingVersion'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    body = {}
    body['action'] = 'publish'
    data = json.dumps(body)
    request = Request(uri=uri)
    result = request.patch(data, True)
    if 'message' in result:
        return result['message']
    else:
        return 'Failed to auto-publish, please contact MP admin to maunaully approve listing.'

def create_new_listing(config):
    config.action = 'get_applications'
    file_name = find_file('metadata.yaml')
    with open(file_name, 'r') as stream:
        new_listing_metadata = yaml.safe_load(stream)
        del new_listing_metadata['listingId']
    if 'versionDetails' in new_listing_metadata:
        vd = new_listing_metadata['versionDetails']
        config.versionString = vd['versionNumber']
        new_listing_metadata['versionDetails']['releaseDate'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    body = json.dumps(new_listing_metadata)
    request = Request(uri = uri)
    result = request.post(None, body)
    return result['entityId'] if 'entityId' in result else result

def create_new_package(config, artifactId):

    body = {}
    body['version'] = sanitize_name(config.versionString)
    body['description'] = config.versionString
    body['serviceType'] = 'OCIOrchestration'
    body['resources'] = [{}]
    body['resources'][0]['serviceType'] = 'OCIOrchestration'
    body['resources'][0]['type'] = 'terraform'
    body['resources'][0]['properties'] = [{}]
    body['resources'][0]['properties'][0]['name'] = 'artifact'
    body['resources'][0]['properties'][0]['value'] = artifactId

    config.action = 'get_application_packages'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    payload = {'json': (None, json.dumps(body))}
    request = Request(uri = uri)
    result = request.post(payload)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result

def upload_icon(config):
    config.action = 'upload_icon'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    file_name = find_file('icon.png')
    files = {'image': open(file_name, 'rb')}
    request = Request(uri = uri)
    result = request.post(files)
    return result['entityId'] if 'entityId' in result else result


