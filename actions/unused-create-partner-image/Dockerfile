FROM golang:1.13

LABEL "name"="create marketplace-ready image"
LABEL "version"="1.0"

COPY marketplace_image.json /marketplace_image.json
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
