#!/bin/sh
set -e

python3 delete_orgas_from_catalog.py
# python3 delete_offerings_from_catalog.py
python3 upload_schemas_to_catalog.py
python3 add_orgas_to_catalog.py