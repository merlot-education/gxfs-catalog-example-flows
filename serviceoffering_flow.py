# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
from icecream import ic
import json
import os
from utils import checkResponse, get_access_token, resolveSchema

file_sd_override = ""

sd_wizard_api_base = "http://localhost:8085"
catalog_api_base = "http://localhost:8081"
oauth_url = "https://sso.common.merlot-education.eu/realms/gxfscatalog/protocol/openid-connect/token"
oauth_client_secret = os.getenv('OAUTH2_CLIENT_SECRET')
oauth_user = "gxfscatalog"
oauth_pass = os.getenv('OAUTH2_PASS')

issuer = "http://10"
serviceoffering_data = {
    # required fields
    "@id": "ServiceOffering:MyServiceOffering",
    "@type": "gax-trust-framework:ServiceOffering",
    "gax-trust-framework:termsAndConditions": {
        "gax-trust-framework:hash": "1234",
        "gax-trust-framework:content": "http://example.org/tac"
    },
    "gax-trust-framework:providedBy": issuer,  # required in wizard but not in actual catalog...
    "gax-trust-framework:policy": "demoValue",
    "gax-trust-framework:name": "MyServiceOffering",
    "gax-trust-framework:dataAccountExport": {
        "gax-trust-framework:formatType": "demoValue",
        "gax-trust-framework:accessType": "demoValue",
        "gax-trust-framework:requestType": "demoValue",
    },
    "gax-core:offeredBy": issuer,

    # optional fields
    "gax-trust-framework:endpoint": {
        "gax-trust-framework:endPointURL": "http://example.org/endpoint"
    },
}

if not file_sd_override:
    ic("Get available Shapes")
    response = requests.get(sd_wizard_api_base + "/getAvailableShapesCategorized?ecoSystem=gax-trust-framework")
    checkResponse(response)

    ic("Get shape for SD of Software Offering")
    response = requests.get(sd_wizard_api_base + "/getJSON?name=Software%20Offering.json")
    checkResponse(response)
    shape_json = json.loads(response.text)
    ic(shape_json)

    # extract prefixes and fields from the json
    prefixes = shape_json["prefixList"]
    fields = shape_json["shapes"]

    # transfer schemas in response into query-able dict
    schemas = {}
    for f in fields:
        schemas[f["schema"]] = f

    target_schema = schemas["SoftwareOfferingShape"]
    ic(target_schema)

    # resolve our target schema and add fields with dummy values
    filled_json = resolveSchema(target_schema, schemas, serviceoffering_data)

    # add id and type of the offering
    filled_json["@id"] = serviceoffering_data["@id"]
    filled_json["@type"] = serviceoffering_data["@type"]
    #filled_json["gax-trust-framework:mySoftwareOffering"] = {
    #    "@type": "gax-trust-framework:SoftwareOffering",
    #    "gax-trust-framework:accessType": "access type",
    #    "gax-trust-framework:formatType": "format type",
    #    "gax-trust-framework:requestType": "request type"
    #}

    # add context
    context = {}
    for p in prefixes:
        if p["alias"] == "gax-trust-framework":
            context[p["alias"]] = p["url"].replace("http",
                                                   "https")  # for gax-trust-framework we need an https instead of http, this is a bug of the wizard
        elif p["alias"] == "gax-core":
            context[p["alias"]] = p["url"].replace("http",
                                                   "https")  # for gax-core we need an https instead of http, this is a bug of the wizard
        else:
            context[p["alias"]] = p["url"]
    filled_json["@context"] = context
else:
    ic("Load self description from file")
    filled_json = None
    with open(file_sd_override) as f:
        filled_json = json.load(f)

ic("Compile SD into verifiable presentation")
# pad the sd with a verifiable presentation
presentation = {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "@id": "http://example.edu/verifiablePresentation/self-description1",
    "type": ["VerifiablePresentation"],
    "verifiableCredential": {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "@id": "https://www.example.org/ServiceOffering.json",
        "@type": ["VerifiableCredential"],
        "issuer": issuer,
        "issuanceDate": "2022-10-19T18:48:09Z",
        "credentialSubject": filled_json
    }
}

ic(presentation)

# store the presentation as a file
ic("Storing unsigned vp as file")
with open('vp.json', 'w', encoding='utf-8') as f:
    json.dump(presentation, f, ensure_ascii=False, indent=4, sort_keys=True)

# call the signer to sign the presentation
ic("Calling signer to sign unsigned vp")
os.system("java -jar gxfsTest-0.1.0-jar-with-dependencies.jar vp.json vp.signed.json")

# load the signed presentation from file
ic("Load signed vp from file")
d = None
with open('vp.signed.json') as f:
    d = json.load(f)

# retrieve oauth2 access token
ic("Retrieving access token from oauth2 server")
response = get_access_token(oauth_url,
                            "federated-catalogue",
                            oauth_client_secret, oauth_user, oauth_pass)
checkResponse(response)
access_token = response.json()["access_token"]
ic(access_token)

# send the signed presentation to the catalog API endpoint
ic("Sending signed vp to catalog API")
response = requests.post(catalog_api_base + "/self-descriptions", headers={'Authorization': 'Bearer ' + access_token,
                                                                           "Content-Type": "application/json"},
                         data=json.dumps(d))
checkResponse(response, valid_response_code=201)

ic(response.text)

sdHash = json.loads(response.text)["sdHash"]

# retreive stored data in the catalog
ic("Retrieving stored data in catalog")
response = requests.get(catalog_api_base + "/self-descriptions/" + sdHash, headers={'Authorization': 'Bearer ' + access_token,
                                                                     "accept": "application/json"})
checkResponse(response)
ic(response.status_code, json.loads(response.text))

# delete previously created endpoint
ic("Deleting previously created vp")
response = requests.delete(catalog_api_base + "/self-descriptions/" + sdHash,
                           headers={'Authorization': 'Bearer ' + access_token,
                                    "accept": "application/json"})
checkResponse(response)
