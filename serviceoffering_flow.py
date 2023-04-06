# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
from icecream import ic
import json
import os
from utils import checkResponse, get_access_token, resolveSchema

serviceoffering_data = {
    "@id": "https://www.example.org/mySoftwareOffering",
    "@type": "gax-trust-framework:ServiceOffering",
    "gax-trust-framework:providedBy": "gax-core:Participant1",
    "gax-trust-framework:policy": "demoValue",
    "gax-trust-framework:name": "MyServiceOffering",
    "gax-trust-framework:termsAndConditions": {
        "gax-trust-framework:hash": "1234",
        "gax-trust-framework:content": "http://example.org/tac"
    },
    "gax-trust-framework:dataAccountExport": {
        "gax-trust-framework:formatType": "demoValue",
        "gax-trust-framework:accessType": "demoValue",
        "gax-trust-framework:requestType": "demoValue",
    },

    "gax-trust-framework:dataProtectionRegime": "demoValue",
    "gax-trust-framework:aggregationOf": None,
    "gax-core:dependsOn": None,
    "gax-trust-framework:dependsOn": None,
    "dct:description": "demoValue",
    "gax-trust-framework:ServiceOfferingLocations": "demoValue",
    "dcat:keyword": "demoValue",
    "gax-trust-framework:endpoint": {

    },
    "gax-core:aggregationOf": None,
    "gax-core:offeredBy": "gax-core:Participant1",
    "gax-trust-framework:provisionType": "demoValue",
}

sd_wizard_api_base = "http://localhost:8085"
catalog_api_base = "http://localhost:8081"
oauth_url = "http://key-server:8080/realms/gaia-x/protocol/openid-connect/token"

ic("Get available Shapes")
response = requests.get(sd_wizard_api_base + "/getAvailableShapesCategorized?ecoSystem=gax-trust-framework")
checkResponse(response)

ic("Get shape for SD of Software Offering")
response = requests.get(sd_wizard_api_base + "/getJSON?name=Software%20Offering.json")
checkResponse(response)
shape_json = json.loads(response.text)

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
    else:
        context[p["alias"]] = p["url"]
filled_json["@context"] = context

ic("Compile SD into verifiable presentation")
# pad the sd with a verifiable presentation
presentation = {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "@id": "http://example.edu/verifiablePresentation/self-description1",
    "type": ["VerifiablePresentation"],
    "verifiableCredential": {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "@id": "https://www.example.org/SoftwareOffering.json",
        "@type": ["VerifiableCredential"],
        "issuer": "http://gaiax.de",
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
                            "aCjdwOojaWEaRXnCnT7ei2PwuCiACY3N", "user", "user")
checkResponse(response)
access_token = response.json()["access_token"]
ic(access_token)

# send the signed presentation to the catalog API endpoint
ic("Sending signed vp to catalog API")
response = requests.post(catalog_api_base + "/self-descriptions", headers={'Authorization': 'Bearer ' + access_token,
                                                                           "Content-Type": "application/json"},
                         data=json.dumps(d))
checkResponse(response, valid_response_code=201)

# retreive stored data in the catalog
ic("Retrieving stored data in catalog")
response = requests.get(catalog_api_base + "/participants", headers={'Authorization': 'Bearer ' + access_token,
                                                                     "accept": "application/json"})
checkResponse(response)
ic(response.status_code, json.loads(response.text))

# delete previously created endpoint
ic("Deleting previously created vp")
response = requests.delete(catalog_api_base + "/participants/http%3A%2F%2Fgaiax.de",
                           headers={'Authorization': 'Bearer ' + access_token,
                                    "accept": "application/json"})
checkResponse(response)
