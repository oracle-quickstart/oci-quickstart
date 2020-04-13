FROM golang:1.13

LABEL "name"="Terraform Apply"
LABEL "version"="1.0"

COPY test-apply.go /
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
