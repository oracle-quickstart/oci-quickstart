FROM golang:1.13

LABEL "name"="Terraform Apply"
LABEL "version"="1.0"

COPY quickstart-terraform-test.go /quickstart-terraform-test.go
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
