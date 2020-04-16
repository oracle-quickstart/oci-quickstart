import sys
import argparse
import json
import os.path
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
#       python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersion -listingVersionId <listingVersionId>
#
#   get all listings
#       python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersions
#
#   build one listing tree
#       python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings -listingVersionId <listingVersionId>
#
#   build all listings tree for partner
#       python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings [-includeUnpublished]
#
#   dump metadata file for a listing
#       python3 mpctl.py -credsFile <path to creds yaml file> -action dump_metadata -listingVersionId <listingVersionId>
#######################################################################################################################

config = None

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
            file_name = f"metadata.yaml"

        with open(file_name, 'w+') as stream:
            yaml.safe_dump(self.api_metadata, stream)

class ArtifactVersion:
    details = []

    def __init__(self, details):
        self.details = details

    def __str__(self):
        ppstring = ''
        ppstring += "\n"
        ppstring += json.dumps(self.details, indent=4, sort_keys=False)
        return ppstring

class Artifact:
    versions = []
    resource = []

    def __init__(self, resource):
        global config
        self.resource = resource
        self.versions = []
        for resourceProperty in resource["properties"]:
            config.action = "get_artifact"
            config.artifactId = int(resourceProperty["value"])
            r = do_get_action(config)
            av = ArtifactVersion(r)
            self.versions.append(av)

    def __str__(self):
        ppstring = ''
        ppstring += "\n"
        ppstring += json.dumps(self.resource, indent=4, sort_keys=False)
        for version in self.versions:
            ppstring += "\n"
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
        ppstring += "\n"
        ppstring += json.dumps(self.package, indent=4, sort_keys=False)
        for artifact in self.artifacts:
            ppstring += "\n"
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

        if "packageVersions" in self.listingVersion:
            self.packageVersions = self.listingVersion["packageVersions"]

        config.action = "get_listingVersion"
        config.listingVersionId = self.listingVersion["listingVersionId"]
        self.listingVersionDetails = do_get_action(config)
        self.listingMetadata = ListingMetadata(f"metadata_{config.listingVersionId}.yaml", self)
        config.action = "get_application_packages"
        packages = do_get_action(config)

        for package in packages["items"]:
            if not args.includeUnpublished and package["Package"]["status"]["code"] == "unpublished":
                continue
            p = Package(package)
            self.packages.append(p)

    def __str__(self):
        ppstring = ''
        ppstring += "\n"
        ppstring += json.dumps(self.listingVersion, indent=4, sort_keys=False)
        ppstring += "\n"
        ppstring += json.dumps(self.listingVersionDetails, indent=4, sort_keys=False)
        ppstring += "\n"
        ppstring += json.dumps(self.packageVersions, indent=4, sort_keys=False)
        for package in self.packages:
            ppstring += str(package)
            pass
        return ppstring

class Listing:
    listingVersions = []
    listingId = 0

    def __init__(self, listingVersion):
        self.listingId = listingVersion["listingId"]
        self.listingVersions = [ListingVersion(listingVersion)]

    def __str__(self):
        ppstring = ''
        for listingVersion in self.listingVersions:
            ppstring += "\n"
            ppstring += str(listingVersion)
        return ppstring

class TermVersion():
    termVersion = []

    def __init__(self, termsId, termVersion):
        global config
        config.action = "get_terms_version"
        config.termsId = termsId
        config.termsVersionId = termVersion["termsVersionId"]
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
        global config
        if config.listingVersionId is None or config.listingVersionId == 0:
            config.action = "get_listingVersions"
        else:
            config.action = "get_listingVersion"
        listingVersions = do_get_action(config)

        if "items" in listingVersions:
            for item in listingVersions["items"]:
                if not args.includeUnpublished and item["GenericListing"]["status"]["code"] == "UNPUBLISHED" :
                    continue
                found = False
                for listing in self.listings:
                    if listing.listingId == item["GenericListing"]["listingId"]:
                        listing.listingVersions.append(ListingVersion(item["GenericListing"]))
                        found = True
                        break

                if not found:
                    listing = Listing(item["GenericListing"])
                    self.listings.append(listing)

        else:
            listing = Listing(listingVersions)
            self.listings.append(listing)

        config.action = "get_terms"
        terms = do_get_action(config)
        if "items" in terms:
            for item in terms["items"]:
                t = Terms(item["terms"])
                self.terms.append(t)
        else:
            t = Terms(terms)
            self.terms.append(t)

    def __str__(self):
        ppstring = ''
        ppstring += (f"The parnter has {len(self.listings)} listing(s)")
        ppstring += "\n"
        for listing in self.listings:
            ppstring += str(listing)
            ppstring += "\n"
        ppstring += "\n"
        for terms in self.terms:
            ppstring += str(terms)
        return ppstring

def do_create():
    global config
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
        old_listing_artifact_version = partner.listings[0].listingVersions[0].packages[0].artifacts[0].versions[0].details

    # TODO: surround this if else with retry loop while status is "in validation"

    if config.imageOcid is None:
        # create new artifact for stack listing
        artifactId = create_new_stack_artifact(config, args.fileName)
    else:
        # create new artifact for iamge listing
        artifactId = create_new_image_artifact(config, old_listing_artifact_version)



    # create a new version for the application listing
    newVersionId = get_new_versionId(config)

    file_name = f"metadata_{args.listingVersionId}.yaml"
    config.metadataFile = file_name
    updated_metadata_message = update_version_metadata(config, newVersionId)

    # get the package version id needed for package version creation
    packageId = get_packageId(config, newVersionId)

    # create a package version from existing package
    newPackageVersionId = get_new_packageVersionId(config, newVersionId, packageId)

    # update versioned package details
    message = update_versioned_package_version(config, newPackageVersionId)
    

    # update versioned package details - associate newly created artifact
    message = associate_artifact_with_package(config, artifactId, newPackageVersionId)

    # submit the new version of the listing for approval
    message = submit_listing(config)

    # attempt to publish the listing (succeeds if partner is whitelisted)
    message = publish_listing(config)

    return message


def lookup_listingVersionId_from_listingId(listingId):
    config.action = "get_listingVersions"
    listingVersions = do_get_action(config)
    for item in listingVersions['items']:
        if item['GenericListing']['listingId'] == listingId and item['GenericListing']['status']['code'] == 'PUBLISHED':
            return item['GenericListing']['listingVersionId']
    return '0'




if __name__  == "__main__":

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

   get all listings
       python3 mpctl.py -credsFile <path to creds yaml file> -action get_listingVersions

   build one listing tree
       python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings -listingVersionId <listingVersionId>

   build all listings tree for partner
       python3 mpctl.py -credsFile <path to creds yaml file> -action build_listings [-includeUnpublished]
       
   dump metadata file for a listing
       python3 mpctl.py -credsFile <path to creds yaml file> -action dump_metadata -listingVersionId <listingVersionId>
   '''

    parser = argparse.ArgumentParser(prog='mpctl',
                                     description='publisher api tool',
                                     epilog=usage_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-action',
                        help='the action to perform')
    parser.add_argument('-includeUnpublished', action='store_true',
                        help='include unpublished versions when building tree')
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
    parser.add_argument('-fileName',
                        help='the name of the TF file')
    parser.add_argument('-imageOcid',
                       help='the ocid of the update image')
    parser.add_argument('-credsFile',
                        help='the path to the creds file')

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
    metadata_file_name = find_file("metadata.yaml")
    if not os.path.isfile(metadata_file_name):
        config.versionString = "No Version"
        if args.listingVersionId is None:
            config.listingVersionId = 0
    else:
        with open(metadata_file_name, "r") as stream:
            metadata = yaml.safe_load(stream)
            config.versionString = metadata['versionDetails']['versionNumber']
            if args.listingVersionId is None:
                config.listingVersionId = lookup_listingVersionId_from_listingId(metadata['listingId'])

    if "get" in args.action:
        r_json = do_get_action(config)
        print(json.dumps(r_json, indent=4, sort_keys=True))

    if "create" in args.action:
        print(do_create())

    if "build" in args.action:
        partner = Partner()
        print(partner)

    if "update_listing" in args.action:
        print(do_update_listing())

    if "dump_metadata" in args.action:
        partner = Partner()
        lmd = ListingMetadata(None, partner.listings[0].listingVersions[0])
        lmd.write_metadata(f"metadata.yaml")
