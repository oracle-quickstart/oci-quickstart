FROM golang:1.13

LABEL "name"="Terraform Apply"
LABEL "version"="1.0"

COPY terratest.go /
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
