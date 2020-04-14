FROM golang:1.14

LABEL "name"="Terraform Apply"
LABEL "version"="1.0"

COPY apply_test.go /
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
