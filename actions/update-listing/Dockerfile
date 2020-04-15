FROM python

LABEL "name"="Update Listing"
LABEL "version"="1.0"

COPY __init__.py /
COPY entrypoint.sh /
COPY mpapihelper.py /
COPY mpctl.py /
ENTRYPOINT ["/entrypoint.sh"]
