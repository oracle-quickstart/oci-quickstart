from time import gmtime, strftime
import datetime
import requests
import base64
import yaml
import json
import os.path
import re

api_url = 'https://ocm-apis-cloud.oracle.com/'
picCompartmentOcid = 'ocid1.compartment.oc1..aaaaaaaaxrcshrhpq6exsqibhdzseghk4yjgrwxn3uaev6poaek2ooz4n7eq'
picTenancyId = '59030347'


class Config:
    class __Config:
        kwargs = {}

        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __str__(self):
            return repr(self)

    instance = None

    def __init__(self, **kwargs):
        if not Config.instance:
            Config.instance = Config.__Config(**kwargs)
        else:
            Config.instance.kwargs = {**Config.instance.kwargs, **kwargs}

    def set(self, key, value):
        Config.instance.kwargs[key] = value

    def get(self, key):
        if key not in Config.instance.kwargs: return None
        return Config.instance.kwargs[key]


class Request:
    class __Request:
        kwargs = {}

        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __str__(self):
            return repr(self)

    instance = None

    def __init__(self, **kwargs):
        config = Config()
        if not Request.instance:
            Request.instance = Request.__Request(**kwargs)
            Request.set_access_token(self, config.get('creds_file'))
        else:
            Request.instance.kwargs = {**Request.instance.kwargs, **kwargs}
        Request.bind_action_dic(self)
        Request.instance.kwargs['api_call'] = Request.instance.kwargs['action_api_uri_dic'][config.get('action')]
        Request.instance.kwargs['uri'] = api_url + Request.instance.kwargs['api_call']

    def bind_action_dic(self):
        config = Config()
        Request.instance.kwargs['action_api_uri_dic'] = {
            'get_listingVersions': 'appstore/publisher/v1/listings',
            'get_listingVersion': f'appstore/publisher/v1/applications/{config.get("listingVersionId")}',
            'get_artifacts': 'appstore/publisher/v1/artifacts',
            'get_artifact': f'appstore/publisher/v1/artifacts/{config.get("artifactId")}',
            'get_applications': 'appstore/publisher/v1/applications',
            'get_application': f'appstore/publisher/v1/applications/{config.get("listingVersionId")}',
            'get_listing_packages': f'appstore/publisher/v2/applications/{config.get("listingVersionId")}'
                                    f'/packages',
            'get_application_packages': f'appstore/publisher/v2/applications/{config.get("listingVersionId")}'
                                        f'/packages',
            'get_application_package': f'appstore/publisher/v2/applications/{config.get("listingVersionId")}'
                                       f'/packages/{config.get("packageVersionId")}',
            'get_terms': 'appstore/publisher/v1/terms',
            'get_terms_version': f'appstore/publisher/v1/terms/{config.get("termsId")}/version/'
                                 f'{config.get("termsVersionId")}',
            'create_listing': f'appstore/publisher/v1/applications',
            'create_new_version': f'appstore/publisher/v1/applications/{config.get("listingVersionId")}/version',
            'new_package_version': f'appstore/publisher/v2/applications/{config.get("listingVersionId")}'
                                   f'/packages/{config.get("packageVersionId")}/version',
            'upload_icon': f'appstore/publisher/v1/applications/{config.get("listingVersionId")}/icon',
        }

    def set_access_token(self, creds_file):

        with open(creds_file, 'r') as stream:
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

        Request.instance.kwargs['access_token'] = json.loads(r.text).get('access_token')
        api_headers = {}
        api_headers['charset'] = 'UTF-8'
        api_headers['X-Oracle-UserId'] = creds['user_email']
        api_headers['Authorization'] = f'Bearer {Request.instance.kwargs["access_token"]}'

        Request.instance.kwargs['api_headers'] = api_headers

    def get(self, qsp = None):
        uri = Request.instance.kwargs['uri'] + (f'?{qsp}' if qsp is not None else '')
        r = requests.get(uri, headers=Request.instance.kwargs['api_headers'])
        if r.status_code > 299:
            print(r.text)
        return json.loads(r.text)

    def post(self, files=None, data=None):

        # neither files nor data
        if files is None and data is None:
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'])

        # data but no files
        elif data is not None and files is None:
            Request.instance.kwargs['api_headers']['Content-Type'] = 'application/json'
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'], data=data)
            del Request.instance.kwargs['api_headers']['Content-Type']

        # files and data
        elif data is not None and files is not None:
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'],
                              files=files, data=data)

        # only files
        else:
            r = requests.post(Request.instance.kwargs['uri'], headers=Request.instance.kwargs['api_headers'],
                              files=files)

        if r.status_code > 299:
            print(r.text)
        return json.loads(r.text)

    def patch(self, data=None, is_json=False):
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


def sanitize_name(name):
    return re.sub('[^a-zA-Z0-9_\.\-\+ ]+', '', name)


def find_file(file_name):
    # github actions put files in a chroot jail, so we need to look in root
    file_name = file_name if os.path.isfile(file_name) \
        else '/{}'.format(file_name) if os.path.isfile('/{}'.format(file_name)) \
        else 'marketplace/{}'.format(file_name) if os.path.isfile('marketplace/{}'.format(file_name)) \
        else '/marketplace/{}'.format(file_name) if os.path.isfile('/marketplace/{}'.format(file_name)) \
        else file_name  # return the original file name if not found so the open can throw the exception
    return file_name


def get_time_stamp():
    return strftime("%Y%m%d%H%M", gmtime())


def do_get_action(qsp = None):
    request = Request()
    result = request.get(qsp)
    return result


def get_new_version_id():
    config = Config()
    config.set('action','create_new_version')
    request = Request()
    result = request.post()
    return result['entityId'] if 'entityId' in result else result


def update_version_metadata(newVersionId):
    config = Config()
    config.set('action','get_listingVersion')
    config.set('listingVersionId', newVersionId)
    file_name = find_file('metadata.yaml')
    if not os.path.isfile(file_name):
        return f'metadata file metadata.yaml not found. skipping metadata update.'
    with open(file_name, 'r') as stream:
        metadata = yaml.safe_load(stream)

    updateable_items = ['longDescription', 'name', 'shortDescription', 'systemRequirements', 'tagLine', 'tags',
                        'usageInformation']

    for k in list(metadata.keys()):
        if k not in updateable_items:
            del metadata[k]

    body = json.dumps(metadata)

    request = Request()
    result = request.patch(body, True)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result


def get_package_id(new_version_id):
    config = Config()
    config.set('action','get_application_packages')
    config.set('listingVersionId', new_version_id)
    r = do_get_action()
    return r['items'][0]['Package']['id']


def get_new_package_version_id(new_version_id, package_id):
    config = Config()
    config.set('action','new_package_version')
    config.set('listingVersionId', new_version_id)
    config.set('packageVersionId', package_id)
    request = Request()
    result = request.patch()

    return result['entityId'] if 'entityId' in result else result


def update_versioned_package_version(new_package_version_id):
    config = Config()
    config.set('action','get_application_package')
    config.set('packageVersionId', new_package_version_id)

    if config.get('listing_type') == 'stack':
        service_type = 'OCIOrchestration'
    else:
        service_type = 'OCI'
    body = {}
    body['version'] = sanitize_name(config.get('versionString')) + ' ' + get_time_stamp()
    body['serviceType'] = service_type
    payload = {'json': (None, json.dumps(body))}

    request = Request()
    result = request.put(payload)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result


def set_package_version_as_default(new_version_id, new_package_version_id):
    config = Config()
    config.set('action','get_application_package')
    config.set('listingVersionId', new_version_id)
    config.set('packageVersionId', new_package_version_id)
    body = {}
    body['action'] = 'default'
    request = Request()
    result = request.patch(json.dumps(body), True)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result


def create_new_stack_artifact(file_name):
    config = Config()
    config.set('action','get_artifacts')
    body = {}
    body['name'] = config.get('commitHash') if config.get('commitHash') is not None \
        else sanitize_name(config.get('versionString')) + ' ' + get_time_stamp()
    body['artifactType'] = 'TERRAFORM_TEMPLATE'
    payload = {'json': (None, json.dumps(body))}
    index = file_name.rfind('/')
    name = file_name[index + 1:]
    files = {'file': (name, open(file_name, 'rb'))}
    request = Request()
    result = request.post(files, payload)
    return result['entityId'] if 'entityId' in result else result


def create_new_image_artifact(old_listing_artifact_version):
    config = Config()
    config.set('action','get_artifacts')
    if old_listing_artifact_version is not None:
        new_version = {key: old_listing_artifact_version[key] for key in
                       ['name', 'artifactType', 'source', 'artifactProperties']}
        new_version['name'] = sanitize_name(config.get('versionString')) + ' ' + get_time_stamp()
        new_version['source']['uniqueIdentifier'] = config.get('imageOcid')
        new_version['artifactType'] = 'OCI_COMPUTE_IMAGE'
    else:
        new_version = {}
        new_version['name'] = sanitize_name(config.get('versionString')) + ' ' + get_time_stamp()
        new_version['artifactType'] = 'OCI_COMPUTE_IMAGE'
        new_version['source'] = {}
        new_version['source']['regionCode'] = 'us-ashburn-1'
        new_version['source']['uniqueIdentifier'] = config.get('imageOcid')
        new_version['artifactProperties'] = [{}, {}]
        new_version['artifactProperties'][0]['artifactTypePropertyName'] = 'compartmentOCID'
        new_version['artifactProperties'][0]['value'] = picCompartmentOcid
        new_version['artifactProperties'][1]['artifactTypePropertyName'] = 'ociTenancyID'
        new_version['artifactProperties'][1]['value'] = picTenancyId
    request = Request()
    data = json.dumps(new_version)
    result = request.post(None, data)
    return result['entityId'] if 'entityId' in result else result


def associate_artifact_with_package(artifact_id, new_package_version_id):
    config = Config()
    body = {}
    body['resources'] = [{}]
    body['resources'][0]['serviceType'] = 'OCIOrchestration' if config.get('listing_type') == 'stack' else 'OCI'
    body['resources'][0]['type'] = 'terraform' if config.get('listing_type') == 'stack' else 'ocimachineimage'
    body['resources'][0]['properties'] = [{}]
    body['resources'][0]['properties'][0]['name'] = 'artifact'
    body['resources'][0]['properties'][0]['value'] = artifact_id
    body['resources'][0]['properties'][0]['valueProperties'] = [{}]
    body['resources'][0]['properties'][0]['valueProperties'][0]['name'] = 'name'
    body['resources'][0]['properties'][0]['valueProperties'][0]['value'] = sanitize_name(config.get('versionString'))

    payload = {'json': (None, json.dumps(body))}
    config.set('action','get_application_package')
    config.set('packageVersionId', new_package_version_id)
    request = Request()
    result = request.put(payload)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result


def submit_listing():
    config = Config()
    auto_approve = 'true'
    while True:
        config.set('action','get_listingVersion')
        body = {}
        body['action'] = 'submit'
        body['note'] = 'submitting new version'
        body['autoApprove'] = auto_approve
        data = json.dumps(body)
        request = Request()
        result = request.patch(data, True)
        if 'message' in result:
            return result['message']
        if auto_approve == 'false':
            return 'this partner has not yet been approved for auto approval. please contact MP admin.'
        else:
            auto_approve = 'false'


def publish_listing():
    config = Config()
    config.set('action','get_listingVersion')
    body = {}
    body['action'] = 'publish'
    data = json.dumps(body)
    request = Request()
    result = request.patch(data, True)
    if 'message' in result:
        return result['message']
    else:
        return 'Failed to auto-publish, please contact MP admin to maunaully approve listing.'


def create_new_listing():
    config = Config()
    config.set('action','get_applications')
    file_name = find_file('metadata.yaml')
    with open(file_name, 'r') as stream:
        new_listing_metadata = yaml.safe_load(stream)
        del new_listing_metadata['listingId']
    if 'versionDetails' in new_listing_metadata:
        vd = new_listing_metadata['versionDetails']
        config.set('versionString', vd['versionNumber'])
        new_listing_metadata['versionDetails']['releaseDate'] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S.000Z")
    body = json.dumps(new_listing_metadata)
    request = Request()
    result = request.post(None, body)
    return result['entityId'] if 'entityId' in result else result


def create_new_package(artifact_id):
    config = Config()
    body = {}
    body['version'] = sanitize_name(config.get('versionString'))
    body['description'] = config.get('versionString')
    body['serviceType'] = 'OCIOrchestration'
    body['resources'] = [{}]
    body['resources'][0]['serviceType'] = 'OCIOrchestration'
    body['resources'][0]['type'] = 'terraform'
    body['resources'][0]['properties'] = [{}]
    body['resources'][0]['properties'][0]['name'] = 'artifact'
    body['resources'][0]['properties'][0]['value'] = artifact_id

    config.set('action','get_application_packages')
    payload = {'json': (None, json.dumps(body))}
    request = Request()
    result = request.post(payload)
    if 'message' in result:
        return result['message']
    else:
        return result.text if 'text' in result else result


def upload_icon():
    config = Config()
    config.set('action','upload_icon')
    file_name = find_file('icon.png')
    files = {'image': open(file_name, 'rb')}
    request = Request()
    result = request.post(files)
    return result['entityId'] if 'entityId' in result else result
