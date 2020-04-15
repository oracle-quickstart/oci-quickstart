import sys
import argparse
import json
import requests
import base64
import yaml
import os.path

action_api_uri_dic = {}
access_token = ''
creds = {}
api_url = 'https://ocm-apis-cloud.oracle.com/'
form_data_api_headers = ''
api_headers = ''
config = None

def main():
    usage_text = '''usage:
    update listing with new terraform template
       python mpctl.py -credsFile <path to creds yaml file> -action update_listing -fileName <fileName of ORM zip>

   update listing with new image
       python mpctl.py -credsFile <path to creds yaml file> -action update_listing -imageOcid <imageOcid>

   create new terraform listing
       python mpctl.py -credsFile <path to creds yaml file> -action create_listing -fileName <fileName of ORM zip>

   create new image listing
       python mpctl.py -credsFile <path to creds yaml file> -action create_listing -imageOcid <imageOcid>

   get one listing
       python mpctl.py -credsFile <path to creds yaml file> -action get_listingVersion -listingVersionId <listingVersionId>

   get all listings
       python mpctl.py -credsFile <path to creds yaml file> -action get_listingVersions

   build one listing tree
       python mpctl.py -credsFile <path to creds yaml file> -action build_listings -listingVersionId <listingVersionId>

   build all listings tree for partner
       python mpctl.py -credsFile <path to creds yaml file> -action build_listings [-includeUnpublished]

   dump metadata file for a listing
       python mpctl.py -credsFile <path to creds yaml file> -action dump_metadata -listingVersionId <listingVersionId>
   '''

    parser = argparse.ArgumentParser(prog='mpctl', description='publisher api tool', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-action', help='action to perform')
    parser.add_argument('-includeUnpublished', action='store_true', help='include unpublished versions when building tree')
    parser.add_argument('-listingVersionId', type=int, help='listing version to act on')
    parser.add_argument('-packageVersionId', type=int, help='package version to act on')
    parser.add_argument('-termsId', type=int, help='terms to act on')
    parser.add_argument('-termsVersionId', type=int, help='terms version to act on')
    parser.add_argument('-artifactId', type=int, help='artifact to act on')
    parser.add_argument('-fileName', help='name of the terraform file')
    parser.add_argument('-imageOcid', help='ocid of the update image')
    parser.add_argument('-credsFile', help='path to the creds file')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    config = Config(args.credsFile)
    if args.artifactId is not None:
        config.artifactId = args.artifactId
    if args.action is not None:
        config.action = args.action
    if args.listingVersionId is not None:
        config.listingVersionId = args.listingVersionId
    if args.packageVersionId is not None:
        config.packageVersionId = args.packageVersionId
    if args.termsId is not None:
        config.termsId = args.termsId
    if args.termsVersionId is not None:
        config.termsVersionId = args.termsVersionId
    if args.imageOcid is not None:
        config.imageOcid = args.imageOcid
    if not os.path.isfile('metadata.yaml'):
        config.versionString = 'No Version'
        if args.listingVersionId is None:
            config.listingVersionId = 0
    else:
        with open('metadata.yaml', 'r') as stream:
            metadata = yaml.safe_load(stream)
            config.versionString = metadata['versionDetails']['versionNumber']
            if args.listingVersionId is None:
                config.listingVersionId = lookup_listingVersionId_from_listingId(metadata['listingId'])

    if 'get' in args.action:
        r_json = do_get_action(config)
        print(json.dumps(r_json, indent=4, sort_keys=True))

    if 'create' in args.action:
        print(do_create())

    if 'build' in args.action:
        partner = Partner()
        print(partner)

    if 'update_listing' in args.action:
        print(do_update_listing())

    if 'dump_metadata' in args.action:
        partner = Partner()
        lmd = ListingMetadata(None, partner.listings[0].listingVersions[0])
        lmd.write_metadata(f'metadata.yaml')

class ListingMetadata:

    git_metadata = {}
    api_metadata = {}

    def __init__(self, file_name, lv):

        self.git_metadata = {}
        self.api_metadata = {}

        if file_name is not None and os.path.isfile(file_name):
            with open(file_name, 'r') as stream:
                self.git_metadata = yaml.safe_load(stream)

        if lv is not None:
            lvd = lv.listingVersionDetails
            self.api_metadata['versionDetails'] = {}
            self.api_metadata['versionDetails']['versionNumber'] = lvd['versionDetails']['versionNumber'] \
                if 'versionDetails' in lvd and 'versionNumber' in lvd['versionDetails'] else ''
            self.api_metadata['versionDetails']['releaseDate'] = lvd['versionDetails']['releaseDate'] \
                if 'versionDetails' in lvd and 'releaseDate' in lvd['versionDetails'] else ''
            self.api_metadata['name'] = lvd['name'] if 'name' in lvd else ''
            self.api_metadata['shortDescription'] = lvd['shortDescription'] if 'shortDescription' in lvd else ''
            self.api_metadata['longDescription'] = lvd['longDescription'] if 'longDescription' in lvd else ''
            self.api_metadata['usageInformation'] = lvd['usageInformation'] if 'usageInformation' in lvd else ''
            self.api_metadata['tags'] = lvd['tags'] if 'tags' in lvd else ''
            self.api_metadata['tagLine'] = lvd['tagLine'] if 'tagLine' in lvd else ''
            self.api_metadata['systemRequirements'] = lvd['systemRequirements'] if 'systemRequirements' in lvd else ''

    def write_metadata(self, file_name):

        if file_name is None:
            file_name = f'metadata.yaml'

        with open(file_name, 'w+') as stream:
            yaml.safe_dump(self.api_metadata, stream)


class ArtifactVersion:
    details = []

    def __init__(self, details):
        self.details = details

    def __str__(self):
        return '\n' + json.dumps(self.details, indent=4, sort_keys=False)


class Artifact:
    versions = []
    resource = []

    def __init__(self, resource):
        global config
        self.resource = resource
        self.versions = []
        for resourceProperty in resource['properties']:
            config.action = 'get_artifact'
            config.artifactId = int(resourceProperty['value'])
            r = do_get_action(config)
            av = ArtifactVersion(r)
            self.versions.append(av)

    def __str__(self):
        ppstring = ''
        ppstring += '\n'
        ppstring += json.dumps(self.resource, indent=4, sort_keys=False)
        for version in self.versions:
            ppstring += '\n'
            ppstring += str(version)
        return ppstring


class Package:
    package = []
    artifacts = []

    def __init__(self, package):
        self.artifacts = []
        self.package = package['Package']
        for resource in self.package['resources']:
            a = Artifact(resource)
            self.artifacts.append(a)

    def __str__(self):
        ppstring = ''
        ppstring += '\n'
        ppstring += json.dumps(self.package, indent=4, sort_keys=False)
        for artifact in self.artifacts:
            ppstring += '\n'
            ppstring += str(artifact)
        return ppstring


class ListingVersion:
    packageVersions = []
    listingVersion = ''
    listingVersionDetails = ''
    packages = []
    listingMetadata = {}

    def __init__(self, listingVersion):
        global config
        self.packages = []
        self.listingVersion = listingVersion

        if 'packageVersions' in self.listingVersion:
            self.packageVersions = self.listingVersion['packageVersions']

        config.action = 'get_listingVersion'
        config.listingVersionId = self.listingVersion['listingVersionId']
        self.listingVersionDetails = do_get_action(config)
        self.listingMetadata = ListingMetadata(
            f'metadata_{config.listingVersionId}.yaml', self)
        config.action = 'get_application_packages'
        packages = do_get_action(config)

        for package in packages['items']:
            if not args.includeUnpublished and package['Package']['status']['code'] == 'unpublished':
                continue
            p = Package(package)
            self.packages.append(p)

    def __str__(self):
        ppstring = ''
        ppstring += '\n'
        ppstring += json.dumps(self.listingVersion, indent=4, sort_keys=False)
        ppstring += '\n'
        ppstring += json.dumps(self.listingVersionDetails, indent=4, sort_keys=False)
        ppstring += '\n'
        ppstring += json.dumps(self.packageVersions, indent=4, sort_keys=False)
        for package in self.packages:
            ppstring += str(package)
            pass
        return ppstring


class Listing:
    listingVersions = []
    listingId = 0

    def __init__(self, listingVersion):
        self.listingId = listingVersion['listingId']
        self.listingVersions = [ListingVersion(listingVersion)]

    def __str__(self):
        ppstring = ''
        for listingVersion in self.listingVersions:
            ppstring += '\n'
            ppstring += str(listingVersion)
        return ppstring


class TermVersion():
    termVersion = []

    def __init__(self, termsId, termVersion):
        global config
        config.action = 'get_terms_version'
        config.termsId = termsId
        config.termsVersionId = termVersion['termsVersionId']
        tv = do_get_action(config)
        self.termVersion = tv

    def __str__(self):
        return json.dumps(self.termVersion, indent=4, sort_keys=False)


class Terms():
    terms = []
    termVersions = []

    def __init__(self, terms):
        self.terms = terms
        self.termVersions = []

        for termVersion in terms['termVersions']:
            tv = TermVersion(terms['termsId'], termVersion)
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
        global config
        if config.listingVersionId is None:
            config.action = 'get_listingVersions'
        else:
            config.action = 'get_listingVersion'
        listingVersions = do_get_action(config)

        if 'items' in listingVersions:
            for item in listingVersions['items']:
                if not args.includeUnpublished and item['GenericListing']['status']['code'] == 'UNPUBLISHED':
                    continue
                found = False
                for listing in self.listings:
                    if listing.listingId == item['GenericListing']['listingId']:
                        listing.listingVersions.append(
                            ListingVersion(item['GenericListing']))
                        found = True
                        break

                if not found:
                    listing = Listing(item['GenericListing'])
                    self.listings.append(listing)

        else:
            listing = Listing(listingVersions)
            self.listings.append(listing)

        config.action = 'get_terms'
        terms = do_get_action(config)
        if 'items' in terms:
            for item in terms['items']:
                t = Terms(item['terms'])
                self.terms.append(t)
        else:
            t = Terms(terms)
            self.terms.append(t)

    def __str__(self):
        ppstring = ''
        ppstring += (f'The parnter has {len(self.listings)} listing(s)')
        ppstring += '\n'
        for listing in self.listings:
            ppstring += str(listing)
            ppstring += '\n'
        ppstring += '\n'
        for terms in self.terms:
            ppstring += str(terms)
        return ppstring


def do_create():
    global config
    file_name = 'marketplace/icon.png'
    if not os.path.isfile(file_name):
        return ('icon.png file not found in workspace directory. exiting.')
    config.listingVersionId = create_new_listing(config)

    upload_icon_message = upload_icon(config)

    # TODO: surround with retry loop if image is still in validation
    if config.imageOcid is None:
        # create new artifact for stack listing
        artifactId = create_new_stack_artifact(config, args.fileName)
    else:
        # create new artifact for iamge listing
        artifactId = create_new_image_artifact(config, None)

    newPackageId = create_new_package(config, artifactId)

    # submit the new version of the listing for approval
    message = submit_listing(config)

    # TODO: possible also publish new listings
    #message = publish_listing(config)

    return message


def do_update_listing():
    global config
    partner = Partner()

    if config.imageOcid is not None:
        old_listing_artifact_version = partner.listings[0].listingVersions[
            0].packages[0].artifacts[0].versions[0].details

    # TODO: surround this if else with retry loop while status is 'in validation'

    if config.imageOcid is None:
        # create new artifact for stack listing
        artifactId = create_new_stack_artifact(config, args.fileName)
    else:
        # create new artifact for iamge listing
        artifactId = create_new_image_artifact(
            config, old_listing_artifact_version)

    # create a new version for the application listing
    newVersionId = get_new_versionId(config)

    file_name = f'metadata_{args.listingVersionId}.yaml'
    config.metadataFile = file_name
    updated_metadata_message = update_version_metadata(config, newVersionId)

    # get the package version id needed for package version creation
    packageId = get_packageId(config, newVersionId)

    # create a package version from existing package
    newPackageVersionId = get_new_packageVersionId(
        config, newVersionId, packageId)

    # update versioned package details
    message = update_versioned_package_version(config, newPackageVersionId)

    # update versioned package details - associate newly created artifact
    message = associate_artifact_with_package(
        config, artifactId, newPackageVersionId)

    # submit the new version of the listing for approval
    message = submit_listing(config)

    # attempt to publish the listing (succeeds if partner is whitelisted)
    message = publish_listing(config)

    return message


def lookup_listingVersionId_from_listingId(listingId):
    print('Using ' + listingId + ' to look up the listingVersionId.')

    config.action = 'get_listingVersions'
    listingVersions = do_get_action(config)
    for item in listingVersions['items']:
        if item['GenericListing']['listingId'] == listingId and item['GenericListing']['status']['code'] == 'PUBLISHED':
            return item['GenericListing']['listingVersionId']
    return '0'

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
    metadataFile = None
    versionString = None

    def __init__(self, credsFile):
        if self.access_token is None:
            set_access_token(credsFile)


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

    auth_string = creds['client_id'] + ':' + creds['secret_key']

    encoded = base64.b64encode(auth_string.encode('ascii'))
    encoded_string = encoded.decode('ascii')

    token_url = 'https://login.us2.oraclecloud.com:443/oam/oauth2/tokens?grant_type=client_credentials'
    auth_headers = {'Content-Type': 'application/x-www-form-urlencoded', 'charset': 'UTF-8', 'X-USER-IDENTITY-DOMAIN-NAME': 'usoracle30650', 'Authorization': f'Basic {encoded_string}'}

    r = requests.post(token_url, headers=auth_headers)
    access_token = json.loads(r.text).get('access_token')
    api_headers = {'charset': 'UTF-8', 'X-Oracle-UserId': creds['user_email'], 'Authorization': f'Bearer {access_token}'}


def do_get_action(config):
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    r = requests.get(uri, headers=api_headers)
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json


def get_new_versionId(config):
    config.action = 'create_new_version'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    api_headers['Content-Type'] = 'application/json'
    r = requests.post(uri, headers=api_headers)
    del api_headers['Content-Type']
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['entityId']


def update_version_metadata(config, newVersionId):
    config.action = 'get_listingVersion'
    config.listingVersionId = newVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall

    if not os.path.isfile('metadata.yaml'):
        return f'metadata file metadata.yaml not found. skipping metadata update.'
    with open('metadata.yaml',  'r') as stream:
        metadata = yaml.safe_load(stream)

    updateable_items = ['longDescription', 'name', 'shortDescription',
                        'systemRequirements', 'tagLine', 'tags', 'usageInformation']

    body = ''
    for k, v in metadata.items():
        if k in updateable_items:
            v = v.replace(''', ''')
            body += f''''{k}': '{v}','''

    body_start = '{'
    body_end = '}'
    body = body_start + body
    body = body[:len(body) - 1]
    body = body + body_end
    body = body.encode('unicode_escape').decode('utf-8')

    api_headers['Content-Type'] = 'application/json'
    r = requests.patch(uri, headers=api_headers, data=body)
    del api_headers['Content-Type']
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    if 'message' in r_json:
        return r_json['message']
    else:
        return r.text


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
    api_headers['Content-Type'] = 'application/json'
    r = requests.patch(uri, headers=api_headers)
    del api_headers['Content-Type']
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['entityId']


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

    body = {
        'version': config.versionString,
        'description': config.versionString,
        'serviceType': service_type
    }
    payload = {'json': (None, str(body))}
    r = requests.put(uri, headers=api_headers, files=payload)
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['message']


def create_new_stack_artifact(config, fileName):
    config.action = 'get_artifacts'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    body = {
        'name': config.versionString,
        'artifactType': 'TERRAFORM_TEMPLATE'
    }
    payload = {'json': (None, str(body))}
    index = fileName.rfind('/')
    name = fileName[index + 1:]
    files = {'file': (name, open(fileName, 'rb'))}
    r = requests.post(uri, headers=api_headers, files=files, data=payload)
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['entityId']


def create_new_image_artifact(config, old_listing_artifact_version):
    config.action = 'get_artifacts'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    if old_listing_artifact_version is not None:
        new_version = {key: old_listing_artifact_version[key] for key in ['name', 'artifactType', 'source', 'artifactProperties']}
        new_version['name'] = config.versionString
        new_version['source']['uniqueIdentifier'] = config.imageOcid
        new_version['artifactType'] = 'OCI_COMPUTE_IMAGE'
        body = json.dumps(new_version)
    else:
        body = {
            'name': config.versionString,
            'artifactType': 'OCI_COMPUTE_IMAGE',
            'source': {
                'regionCode': 'us-ashburn-1',
                'uniqueIdentifier': config.imageOcid
            },
            'artifactProperties': [
                {
                    'artifactTypePropertyName': 'compartmentOCID',
                    'value': 'ocid1.compartment.oc1..aaaaaaaaxrcshrhpq6exsqibhdzseghk4yjgrwxn3uaev6poaek2ooz4n7eq'
                },
                {
                    'artifactTypePropertyName': 'ociTenancyID',
                    'value': '59030347'
                }
            ]
        }

    api_headers['Content-Type'] = 'application/json'
    r = requests.post(uri, headers=api_headers, data=str(body))
    del api_headers['Content-Type']
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['entityId']


def associate_artifact_with_package(config, artifactId, newPackageVersionId):
    body = {
        'resources': [
            {
                'serviceType': 'OCIOrchestration',
                'type': 'terraform',
                'properties': [
                    {
                        'name': 'artifact',
                        'value': artifactId,
                        'valueProperties': [
                            {
                                'name': 'name',
                                'value': config.versionString
                            }
                        ]
                    }
                ]
            }
        ]
    }

    if config.imageOcid is not None:
        body['resources'][0]['serviceType']='Orchestration'
        body['resources'][0]['type']='ocimachineimage'

    payload = {'json': (None, str(body))}
    config.action = 'get_application_package'
    config.packageVersionId = newPackageVersionId
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    r = requests.put(uri, headers=api_headers, files=payload)
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['message']


def submit_listing(config):
    autoApprove = 'true'
    while (True):
        config.action = 'get_listingVersion'
        bind_action_dic(config)
        apicall = action_api_uri_dic[config.action]
        uri = api_url + apicall

        api_headers['Content-Type'] = 'application/json'
        body = {
            'action': 'submit',
            'note': 'submitting new version',
            'autoApprove': autoApprove
        }
        r = requests.patch(uri, headers=api_headers, data=str(body))
        del api_headers['Content-Type']
        if r.status_code > 299:
            print(r.text)
        r_json = json.loads(r.text)
        if 'message' in r_json:
            return r_json['message']
        if autoApprove == 'false':
            return 'this partner has not yet been approved for auto approval. please contact MP admin.'
        else:
            autoApprove = 'false'


def publish_listing(config):
    config.action = 'get_listingVersion'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall

    api_headers['Content-Type'] = 'application/json'
    body = {'action': 'publish'}
    r = requests.patch(uri, headers=api_headers, data=str(body))

    del api_headers['Content-Type'] ####why would you delete this?
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    if 'message' in r_json:
        return r_json['message']
    else:
        return 'Failed to auto-publish, please contact MP admin to maunaully approve listing.'


def create_new_listing(config):
    config.action = 'get_applications'
    file_name = 'marketplace/metadata.yaml'
    with open(file_name, 'r') as stream:
        new_listing_body = yaml.safe_load(stream)
        del new_listing_body['listingId']
    if 'versionDetails' in new_listing_body:
        vd = new_listing_body['versionDetails']
        config.versionString = vd['versionNumber']
        if 'releaseDate' in vd:
            new_listing_body['versionDetails']['releaseDate'] = str(
                new_listing_body['versionDetails']['releaseDate'])
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    api_headers['Content-Type'] = 'application/json'
    body = json.dumps(new_listing_body)
    r = requests.post(uri, headers=api_headers, data=body)
    del api_headers['Content-Type']
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['entityId']


def create_new_package(config, artifactId):
    body = {
        'version': config.versionString,
        'description': config.versionString,
        'serviceType': 'OCIOrchestration',
        'resources': [
            {
                'serviceType': 'OCIOrchestration',
                'type': 'terraform',
                'properties': [
                    {
                        'name': 'artifact',
                        'value': artifactId
                    }
                ]
            }
        ]
    }

    config.action = 'get_application_packages'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    payload = {'json': (None, str(body))}
    r = requests.post(uri, headers=api_headers, files=payload)
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['message']


def upload_icon(config):
    config.action = 'upload_icon'
    bind_action_dic(config)
    apicall = action_api_uri_dic[config.action]
    uri = api_url + apicall
    file_name = '/marketplace/icon.png' if os.path.isfile('/marketplace/icon.png') else 'marketplace/icon.png'
    files = {'image': open(file_name, 'rb')}
    r = requests.post(uri, headers=api_headers, files=files)
    if r.status_code > 299:
        print(r.text)
    r_json = json.loads(r.text)
    return r_json['entityId']


if __name__ == '__main__':
    main()
