FROM rackspacedot/python37:latest

LABEL "name"="Update Listing"
LABEL "version"="1.0"

COPY entrypoint.sh /
COPY newArtifact.json /
COPY newPackage.json /
COPY newImage.json /
COPY mpctl.py /
COPY mpapihelper.py /
COPY __init__.py /
ENTRYPOINT ["/entrypoint.sh"]
