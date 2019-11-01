import io
import json
import argparse
from partners.scripts.mpapihelper import *

####################################
#
# usage:
#
#
#
#
#
#
#
#
#
#
#
####################################


action_api_uri_dic = []

parser = argparse.ArgumentParser()
parser.add_argument('-creds',
                    help='the name of the creds file to use')
parser.add_argument('-action',
                    help='the action to perform')
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
parser.add_argument('-filename',
                    help='the name of the TF file')
parser.add_argument('-version_string',
                    help='the new version for update')

args = parser.parse_args()
config = None


class ArtifactVersion:
    details = []

    def __init__(self, details):
        self.details = details

    def __str__(self):
        ppstring = ''
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
        ppstring += json.dumps(self.resource, indent=4, sort_keys=False)
        for version in self.versions:
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
        ppstring += json.dumps(self.package, indent=4, sort_keys=False)
        for artifact in self.artifacts:
            ppstring += str(artifact)
        return ppstring


class Listing:
    packageVersions = []
    listing = ''
    listingDetails = ''
    packages = []

    def __init__(self, listing):
        global config
        self.packages = []
        self.listing = listing
        if "packageVersions" in self.listing:
            self.packageVersions = self.listing["packageVersions"]

        config.action = "get_listing"
        config.listingVersionId = self.listing["listingVersionId"]
        self.listingDetails = do_get_action(config)

        config.action = "get_application_packages"
        packages = do_get_action(config)

        for package in packages["items"]:
            p = Package(package)
            self.packages.append(p)

    def __str__(self):
        ppstring = ''
        ppstring += json.dumps(self.listing, indent=4, sort_keys=False)
        ppstring += json.dumps(self.listingDetails, indent=4, sort_keys=False)
        ppstring += json.dumps(self.packageVersions, indent=4, sort_keys=False)
        for package in self.packages:
            ppstring += str(package)
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
        if config.listingVersionId is None:
            config.action = "get_listings"
        else:
            config.action = "get_listing"
        listings = do_get_action(config)

        if "items" in listings:
            for item in listings["items"]:
                l = Listing(item["GenericListing"])
                self.listings.append(l)
        else:
            l = Listing(listings)
            self.listings.append(l)

        config.action = "get_terms"
        terms = do_get_action(config)
        if "items" in terms:
            for item in terms["items"]:
                t = Terms(item["terms"])
                self.terms.append(t)
        else:
            t = Terms(terms)
            self.terms.append(t)

        pass

    def __str__(self):
        ppstring = ''
        for listing in self.listings:
            ppstring += str(listing)
        for terms in self.terms:
            ppstring += str(terms)
        return ppstring

def do_build():
    return partner

def do_create():
    global config
    create_listing(config)

def do_update_stack():
    global config
    partner = Partner()

    # tcnId = partner.terms[0].termVersions[0].termVersion["termsVersionId"]
    tcnId = partner.terms[0].termVersions[0].termVersion["contentId"]
    config.termsVersionsId = tcnId

    # create a new version for the application listing
    newVersionId = get_new_versionId(config)

    # get the package version id needed for package version creation
    newPackageId = get_new_packageId(config, newVersionId)

    # create a package version from existing package
    newPackageVersionId = get_new_packageVersionId(config, newVersionId, newPackageId)

    # update versioned package details
    message = update_versioned_package_version(config, newPackageVersionId, args.version_string)

    # create new artifact
    artifactId = create_new_artifact(config, args.version_string, 'tf.zip')

    # update versioned package details - associate newly created artifact
    message = associate_artifact_with_package(config, artifactId, newPackageVersionId, args.version_string)

    return message


config = Config(args.creds)
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

if "get" in args.action:
    r_json = do_get_action(config)
    print(json.dumps(r_json, indent=4, sort_keys=True))

if "create" in args.action:
    do_create()

if "build" in args.action:
    partner = Partner()
    print(partner)

if "update_stack" in args.action:
    print(do_update_stack())
