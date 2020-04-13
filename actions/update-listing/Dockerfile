FROM rackspacedot/python37:latest

LABEL "name"="update listing"
LABEL "version"="1.0"

COPY entrypoint.sh /entrypoint.sh
COPY newArtifact.json /newArtifact.json
COPY newPackage.json /newPackage.json
COPY newImage.json /newImage.json
COPY mpctl.py /mpctl.py
COPY mpapihelper.py /mpapihelper.py
COPY __init__.py /__init__.py
ENTRYPOINT ["/entrypoint.sh"]
