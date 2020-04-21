FROM golang

LABEL "name"="test terraform code"
LABEL "version"="1.0"

COPY apply_test.go /apply_test.go
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
