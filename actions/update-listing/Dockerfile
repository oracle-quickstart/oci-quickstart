FROM python:3.8

LABEL "name"="Update Listing"
LABEL "version"="1.0"

COPY __init__.py /
COPY entrypoint.sh /
COPY mpapihelper.py /
COPY mpctl.py /
COPY newArtifact.json /
COPY newImage.json /
COPY newPackage.json /
ENTRYPOINT ["/entrypoint.sh"]
