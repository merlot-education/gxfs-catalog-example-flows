#!/bin/sh
set -e

if ! [ -f "./gxfsTest-0.1.0-jar-with-dependencies.jar" ]; then
    git clone https://gitlab.com/gaia-x/data-infrastructure-federation-services/cat/fc-tools/signer
    cd signer
    git apply ../signer.patch
    mvn clean install
    mv target/gxfsTest-0.1.0-jar-with-dependencies.jar ../
    cd ..
    rm -rf signer
fi

python3 delete_orgas_from_catalog.py
# python3 delete_offerings_from_catalog.py
python3 upload_schemas_to_catalog.py
python3 add_orgas_to_catalog.py