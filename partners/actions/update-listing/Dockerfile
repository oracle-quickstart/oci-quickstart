FROM rackspacedot/python37:latest

LABEL "name"="update marketplace listing"
LABEL "version"="1.0"

COPY entrypoint.sh /entrypoint.sh
COPY ../../scripts/newArtifact.json /newArtifact.json
COPY ../../scripts/mpctl.py /mpctl.py
COPY ../../scripts/mpapihelper.py /mpapihelper.py
ENTRYPOINT ["/entrypoint.sh"]
