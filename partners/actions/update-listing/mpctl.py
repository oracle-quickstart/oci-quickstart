import argparse
import json
from mpapihelper import *

#######################################################################################################################
#
# usage:
#
#   get one listing
#       python3 mpctl.py -partner <partner> -action get_listingVersion -listingVersionId <listingVersionId>
#
#   get all listings
#       python3 mpctl.py -partner <partner> -action get_listingVersions
#
#   build one listing tree
#       python3 mpctl.py -partner <partner> -action build_listings -listingVersionId <listingVersionId>
#
#   build all listings trees for partner
#       python3 mpctl.py -partner <partner> -action build_listings [-includeUnpublished]
#
#   update listing with new terraform template
#       python3 mpctl.py -partner <partner> -action update_listing -listingVersionId <listingVersionId>
#           -versionString <versionString> -fileName <fileName>
#
#   update listing with new image
#       python3 mpctl.py -partner <partner> -action update_listing -listingVersionId <listingVersionId>
#           -versionString <versionString> -imageOcid <imageOcid>
#
#######################################################################################################################

action_api_uri_dic = []
config = None

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

    def __init__(self, listingVersion):
        global config
        self.packages = []
        self.listingVersion = listingVersion
        if "packageVersions" in self.listingVersion:
            self.packageVersions = self.listingVersion["packageVersions"]

        config.action = "get_listingVersion"
        config.listingVersionId = self.listingVersion["listingVersionId"]
        self.listingVersionDetails = do_get_action(config)

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
        if config.listingVersionId is None:
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
    create_listing(config)

def do_update_listing():
    global config
    partner = Partner()

    #tcnId = partner.terms[0].termVersions[0].termVersion["termsVersionId"]
    #tcnId = partner.terms[0].termVersions[0].termVersion["contentId"]
    #config.termsVersionsId = tcnId

    if config.imageOcid is not None:
        old_listing_artifact_version = partner.listings[0].listingVersions[0].packages[0].artifacts[0].versions[0].details

    # create a new version for the application listing
    newVersionId = get_new_versionId(config)

    # get the package version id needed for package version creation
    newPackageId = get_new_packageId(config, newVersionId)

    # create a package version from existing package
    newPackageVersionId = get_new_packageVersionId(config, newVersionId, newPackageId)

    # update versioned package details
    message = update_versioned_package_version(config, newPackageVersionId, args.versionString)

    if config.imageOcid is None:
        # create new artifact for stack listing
        artifactId = create_new_stack_artifact(config, args.versionString, args.fileName)
    else:
        # create new artifact for iamge listing
        artifactId = create_new_image_artifact(config, args.versionString, old_listing_artifact_version)

    # update versioned package details - associate newly created artifact
    message = associate_artifact_with_package(config, artifactId, newPackageVersionId, args.versionString)

    # submit the new version of the listing for approval
    message = submit_listing(config)

    return message

if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-partner',
                        help='the name of the partner to use')
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
    parser.add_argument('-versionString',
                        help='the new version for update')
    parser.add_argument('-imageOcid',
                       help='the ocid of the update image')
    parser.add_argument('-credsFile',
                        help='(optional) the path to the creds file')

    args = parser.parse_args()

    config = Config(args.partner, args.credsFile)
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

    if "get" in args.action:
        r_json = do_get_action(config)
        print(json.dumps(r_json, indent=4, sort_keys=True))

    if "create" in args.action:
        do_create()

    if "build" in args.action:
        partner = Partner()
        print(partner)

    if "update_listing" in args.action:
        print(do_update_listing())
