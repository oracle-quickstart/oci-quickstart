import sys
import argparse
import json
import os.path
from datetime import time

from mpapihelper import *

#######################################################################################################################
#
# usage:
#
#   update listing with new terraform template
#       python3 mpctl.py -credsFile <path to creds yaml file> -action update_listing -fileName <fileName of ORM zip>
#
#   update listing with new image
#       python3 mpctl.py -credsFile <path to creds yaml file> -action update_listing -imageOcid <imageOcid>
#
#   create new terraform listing
#       python3 mpctl.py -credsFile <path to creds yaml file> -action create_listing -fileName <fileName of ORM zip>
#
#   create new image listing
#       python3 mpctl.py -credsFile <path to creds yaml file> -action create_listing -imageOcid <imageOcid>
#
#   get one listing
#       python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersion -listingVersionId
#       <listingVersionId>
#
#   get the published version of one listing
#       python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersion -listingId <listingId>
#
#   get all listings
#       python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersions
#
#   build one listing tree
#       python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings -listingVersionId
#       <listingVersionId>
#
#   build one listing tree of the published version
#       python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings -listingId <listingId>
#
#   build all listings tree for partner
#       python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings [-includeUnpublished]
#
#   dump metadata file for a listing
#       python3 mpctl.py -credsFile <path to creds yaml file> -action dump_metadata -listingVersionId <listingVersionId>
#
#   dump metadata file for a listing's published version
#       python3 mpctl.py -credsFile <path to creds yaml file> -action dump_metadata -listingId <listingId>
#######################################################################################################################


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
            lvd = lv.listing_version_details
            self.api_metadata['versionDetails'] = {}
            self.api_metadata['listingId'] = args.listingId
            self.api_metadata['versionDetails']['versionNumber'] = lvd['versionDetails']['versionNumber'] \
                if 'versionDetails' in lvd and 'versionNumber' in lvd['versionDetails'] else ''
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
        ppstring = ''
        ppstring += '\n'
        ppstring += json.dumps(self.details, indent=4, sort_keys=False)
        return ppstring


class Artifact:
    versions = []
    resource = []

    def __init__(self, resource):
        config = Config()
        self.resource = resource
        self.versions = []
        for resource_property in resource['properties']:
            config.set('action','get_artifact')
            config.set('artifactId', int(resource_property['value']))
            r = do_get_action()
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
    package_versions = []
    listing_version = ''
    listing_version_details = ''
    packages = []
    listing_metadata = {}

    def __init__(self, listing_version):
        self.packages = []
        self.listing_version = listing_version

        if 'packageVersions' in self.listing_version:
            self.package_versions = self.listing_version['packageVersions']

        config = Config()
        config.set('action','get_listingVersion')
        config.set('listingVersionId', self.listing_version['listingVersionId'])
        self.listing_version_details = do_get_action()
        self.listing_metadata = ListingMetadata(find_file('metadata.yaml'), self)
        config.set('action','get_application_packages')
        packages = do_get_action()

        for package in packages['items']:
            if not args.includeUnpublished and package['Package']['status']['code'] == 'unpublished':
                continue
            p = Package(package)
            self.packages.append(p)

    def __str__(self):
        ppstring = ''
        ppstring += '\n'
        ppstring += json.dumps(self.listing_version, indent=4, sort_keys=False)
        ppstring += '\n'
        ppstring += json.dumps(self.listing_version_details, indent=4, sort_keys=False)
        ppstring += '\n'
        ppstring += json.dumps(self.package_versions, indent=4, sort_keys=False)
        for package in self.packages:
            ppstring += str(package)
            pass
        return ppstring


class Listing:
    listing_versions = []
    listingId = 0

    def __init__(self, listing_version):
        self.listingId = listing_version['listingId']
        self.listing_versions = [ListingVersion(listing_version)]

    def __str__(self):
        ppstring = ''
        for listingVersion in self.listing_versions:
            ppstring += '\n'
            ppstring += str(listingVersion)
        return ppstring


class TermVersion():
    term_version = []

    def __init__(self, terms_id, term_version):
        config = Config()
        config.set('action','get_terms_version')
        config.set('termsId', terms_id)
        config.set('termsVersionId', term_version['termsVersionId'])
        tv = do_get_action()
        self.term_version = tv

    def __str__(self):
        return json.dumps(self.term_version, indent=4, sort_keys=False)


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
        config = Config()

        if args.all or config.get('listingVersionId') is None or config.get('listingVersionId') == '0':
            config.set('action','get_listingVersions')
        else:
            config.set('action','get_listingVersion')
        listing_versions = do_get_action()

        if 'items' in listing_versions:
            for item in listing_versions['items']:
                if not args.includeUnpublished and item['GenericListing']['status']['code'] == 'UNPUBLISHED':
                    continue
                found = False
                for listing in self.listings:
                    if listing.listingId == item['GenericListing']['listingId']:
                        listing.listing_versions.append(ListingVersion(item['GenericListing']))
                        found = True
                        break

                if not found:
                    listing = Listing(item['GenericListing'])
                    self.listings.append(listing)

        else:
            listing = Listing(listing_versions)
            self.listings.append(listing)

        config.set('action','get_terms')
        terms = do_get_action()
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
    config = Config()
    config.set('listingVersionId', create_new_listing())

    upload_icon_message = upload_icon()

    # TODO: surround with retry loop if image is still in validation
    if config.get('listing_type') == 'stack':
        # create new artifact for stack listing
        artifact_id = create_new_stack_artifact(args.fileName)
    else:
        # create new artifact for iamge listing
        artifact_id = create_new_image_artifact(None)

    newPackageId = create_new_package(artifact_id)

    # submit the new version of the listing for approval
    message = submit_listing()

    # TODO: possible also publish new listings
    # message = publish_listing()

    return message


def do_update_listing():
    partner = Partner()

    if config.get('listing_type') == 'image':
        old_listing_artifact_version = \
            partner.listings[0].listing_versions[0].packages[0].artifacts[0].versions[0].details


    if config.get('listing_type') == 'stack':
        # create new artifact for stack listing
        artifactId = create_new_stack_artifact(args.fileName)
    else:
        # create new artifact for iamge listing
        done = False
        retry_count_remaining = 6
        while not done and retry_count_remaining > 0:
            artifactId = create_new_image_artifact(old_listing_artifact_version)
            time.sleep(10) # give api a moment
            config.set('action', 'get_artifact')
            config.set('artifactId', artifactId)
            artifact_status = do_get_action()['status']
            if artifact_status == 'Available':
                done = True
            else:
                print(f'artifact {artifactId} in status {artifact_status}, sleeping for 10 minutes.')
                time.sleep(600)
                retry_count_remaining = retry_count_remaining - 1
        if retry_count_remaining <= 0:
            raise Exception(f'artifact {artifactId} in status {artifact_status} after one hour. Please contact MP admin')


    # create a new version for the application listing
    new_version_id = get_new_version_id()

    updated_metadata_message = update_version_metadata(new_version_id)

    # get the package version id needed for package version creation
    package_id = get_package_id(new_version_id)

    # create a package version from existing package
    new_package_version_id = get_new_package_version_id(new_version_id, package_id)

    # update versioned package details
    message = update_versioned_package_version(new_package_version_id)

    # update versioned package details - associate newly created artifact
    message = associate_artifact_with_package(artifactId, new_package_version_id)

    # set new package version as default
    message = set_package_version_as_default(new_version_id, new_package_version_id)

    # submit the new version of the listing for approval
    message = submit_listing()

    # attempt to publish the listing (succeeds if partner is whitelisted)
    message = publish_listing()

    return message


def lookup_listing_version_id_from_listing_id(listing_id):
    config = Config()
    config.set('action','get_listingVersions')
    listing_versions = do_get_action('status=PUBLISHED')
    for item in listing_versions['items']:
        if item['GenericListing']['listingId'] == listing_id and item['GenericListing']['status']['code'] == 'PUBLISHED':
            return item['GenericListing']['listingVersionId']
    return '0'


def find_listing_version_id(): #TODO: this shouldn't have the side effect of setting the version string

    listing_version_id = None
    metadata_file_name = find_file('metadata.yaml')
    config = Config()
    if not os.path.isfile(metadata_file_name):
        config.set('versionString', 'No Version')
        if args.listingVersionId is None:
            listing_version_id = 0
            if args.listingId is not None:
                listing_version_id = lookup_listing_version_id_from_listing_id(args.listingId)
    else:
        with open(metadata_file_name, 'r') as stream:
            metadata = yaml.safe_load(stream)
            config.set('versionString', metadata['versionDetails']['versionNumber'])
            if args.listingVersionId is None:
                if args.listingId is None:
                    listing_version_id = lookup_listing_version_id_from_listing_id(metadata['listingId'])
                else:
                    listing_version_id = lookup_listing_version_id_from_listing_id(args.listingId)
    return listing_version_id


if __name__ == '__main__':

    usage_text = '''usage:

update listing with new terraform template
   python3 mpctl.py -credsFile <path to creds yaml file> -action update_listing -fileName <fileName of ORM zip>

update listing with new image
   python3 mpctl.py -credsFile <path to creds yaml file> -action update_listing -imageOcid <imageOcid>

create new terraform listing
   python3 mpctl.py -credsFile <path to creds yaml file> -action create_listing -fileName <fileName of ORM zip>

create new image listing
   python3 mpctl.py -credsFile <path to creds yaml file> -action create_listing -imageOcid <imageOcid>

get one listing
   python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersion -listingVersionId <listingVersionId>

get the published version of one listing
   python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersion -listingId <listingId>

get all listings
   python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersions

build one listing tree
   python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings -listingVersionId <listingVersionId>

build one listing tree of the published version 
   python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings -listingId <listingId>

build all listings tree for partner
   python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings [-includeUnpublished]

dump metadata file for a listing
   python3 mpctl.py -credsFile <path to creds yaml file> -action dump_metadata -listingVersionId <listingVersionId>

dump metadata file for a listing's published version
   python3 mpctl.py -credsFile <path to creds yaml file> -action dump_metadata -listingId <listingId>

   '''

    parser = argparse.ArgumentParser(prog='mpctl',
                                     description='publisher api tool',
                                     epilog=usage_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-action',
                        help='the action to perform')
    parser.add_argument('-includeUnpublished', action='store_true',
                        help='include unpublished versions when building tree')
    parser.add_argument('-listingId', type=int,
                        help='the listing to act on')
    parser.add_argument('-listingVersionId', type=int,
                        help='the listing version to act on [optional]. Can be inferred from listingId')
    parser.add_argument('-packageVersionId', type=int,
                        help='the package version to act on')
    parser.add_argument('-termsId', type=int,
                        help='the terms to act on')
    parser.add_argument('-termsVersionId', type=int,
                        help='the terms version to act on')
    parser.add_argument('-artifactId', type=int,
                        help='the artifact to act on')
    parser.add_argument('-fileName',
                        help='the name of the TF file')
    parser.add_argument('-imageOcid',
                        help='the ocid of the update image')
    parser.add_argument('-credsFile',
                        help='the path to the creds file')
    parser.add_argument('-all', action='store_true',
                        help='get all listings even if listing id is known')
    parser.add_argument('-commitHash',
                        help='a string to append to package version')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    config = Config(creds_file = args.credsFile)
    if args.artifactId is not None:
        config.set('artifactId', args.artifactId)
    if args.action is not None:
        config.set('action', args.action)
    if args.listingVersionId is not None:
        config.set('listingVersionId', args.listingVersionId)
    if args.packageVersionId is not None:
        config.set('packageVersionId', args.packageVersionId)
    if args.termsId is not None:
        config.set('termsId', args.termsId)
    if args.termsVersionId is not None:
        config.set('termsVersionId', args.termsVersionId)
    if args.imageOcid is not None:
        config.set('imageOcid', args.imageOcid)
        config.set('listing_type', 'image')
    else:
        config.set('listing_type', 'stack')
    if args.commitHash is not None:
        config.set('commitHash', args.commitHash)

    if args.listingVersionId is None:
        config.set('listingVersionId', find_listing_version_id())
    else:
        config.set('listingVersionId', args.listingVersionId)

    if 'get' in args.action:
        r_json = do_get_action()
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
        lmd = ListingMetadata(None, partner.listings[0].listing_versions[0])
        lmd.write_metadata(f'metadata.yaml')
