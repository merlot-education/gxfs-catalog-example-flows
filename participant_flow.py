# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
from icecream import ic
import json
import os

sd_wizard_api_base = "http://localhost:8085"
catalog_api_base = "http://localhost:8081"
oauth_url = "http://key-server:8080/realms/gaia-x/protocol/openid-connect/token"

def checkResponse(response, valid_response_code=200):
    ic(response.status_code)
    if response.status_code != valid_response_code:
        ic(json.loads(response.text))
        exit()

def resolveSchema(schema, all_schemas):
    # initialize a dict for our current entry and set the type field according to the schema
    entry = {}
    entry["@type"] = schema["targetClassPrefix"] + ":" + schema["targetClassName"]
    # for our schema iterate through all constraints and save the path
    for constraint in schema["constraints"]:
        path = constraint["path"]["prefix"] + ":" + constraint["path"]["value"]
        if "children" in constraint.keys():  # if we have children, we have a nested schema
            subschema = all_schemas[constraint["children"]]
            entry[path] = resolveSchema(subschema, all_schemas)
        else:  # otherwise we simply resolve all constraints and add them to the dict
            if constraint["datatype"]["prefix"] == "nodeKind":  # TODO support nodes
                continue
            datatype = constraint["datatype"]["prefix"] + ":" + constraint["datatype"]["value"]
            entry[path] = {
                "@type": datatype,
                "@value": "demoValue" if not constraint["in"] else constraint["in"][0]["value"]
            }
    return entry


def get_access_token(url, client_id, client_secret, user, password):
    response = requests.post(url, data={
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': user,
        'password': password
    })
    return response


ic("Get available Shapes")
response = requests.get(sd_wizard_api_base + "/getAvailableShapesCategorized?ecoSystem=gax-trust-framework")
checkResponse(response)

ic("Get shape for SD of Legal Person")
response = requests.get(sd_wizard_api_base + "/getJSON?name=Legal%20Person.json")
#response = requests.get(sd_wizard_api_base + "/getJSON?name=Storage%20Offering.json")
checkResponse(response)
shape_json = json.loads(response.text)

# extract prefixes and fields from the json
prefixes = shape_json["prefixList"]
fields = shape_json["shapes"]

target_schema = fields[0]  # for now assume that the first listed schema is our target, # TODO this might be wrong
#ic(target_schema)

# transfer schemas in response into query-able dict
schemas = {}
for f in fields:
    schemas[f["schema"]] = f

# resolve our target schema and add fields with dummy values
filled_json = resolveSchema(target_schema, schemas)

# add id of the participant
filled_json["@id"] = "gax-core:Participant1"

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
        "@id": "https://www.example.org/legalPerson.json",
        "@type": ["VerifiableCredential"],
        "issuer": "http://gaiax.de",
        "issuanceDate": "2022-10-19T18:48:09Z",
        "credentialSubject": filled_json
    }
}

# ic(presentation)

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
response = requests.post(catalog_api_base + "/participants", headers={'Authorization': 'Bearer ' + access_token,
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
