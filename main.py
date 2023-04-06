# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
from icecream import ic
import json
import os

access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJfb0lXMGJhNjZCcDZILUN6alVSb1lUcTc0QTlGeHBnaEJ6LXAzWEZaRlNNIn0.eyJleHAiOjE2ODA3ODIwODYsImlhdCI6MTY4MDc4MTE4NiwianRpIjoiMDQwYmUyNzUtYTIwMC00NWNkLTllMDEtYzU4MDUxODRkMzhhIiwiaXNzIjoiaHR0cDovL2tleS1zZXJ2ZXI6ODA4MC9yZWFsbXMvZ2FpYS14Iiwic3ViIjoiNGNmMjMxMjItMmI2Ny00OGQ4LWIyZDEtZGFiOTBlZjBmMTE0IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZmVkZXJhdGVkLWNhdGFsb2d1ZSIsInNlc3Npb25fc3RhdGUiOiIwYzU2NjU5NS1kZWI3LTQ5MDgtYTc5MS0wNzQ4MWFiNjc1OTgiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtZ2FpYS14Il19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiZmVkZXJhdGVkLWNhdGFsb2d1ZSI6eyJyb2xlcyI6WyJSby1NVS1DQSIsIlJvLU1VLUEiLCJSby1TRC1BIiwiUm8tUEEtQSJdfX0sInNjb3BlIjoib3BlbmlkIGdhaWEteCIsInNpZCI6IjBjNTY2NTk1LWRlYjctNDkwOC1hNzkxLTA3NDgxYWI2NzU5OCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoidXNlciB1c2VyIiwicHJlZmVycmVkX3VzZXJuYW1lIjoidXNlciIsImdpdmVuX25hbWUiOiJ1c2VyIiwiZmFtaWx5X25hbWUiOiJ1c2VyIiwiZW1haWwiOiJ1c2VyQHVzZXIudXNlciJ9.AoeeR3lwb8ZmTY6mQGQvs2YIH46Fn1hOLdOCvN2hJ_nIuA7YkoSpdyiRiPGITtH5agG6DS6xPpms8TiMYj0_6dvBzHHPuzBvh9LtSnBf-Usc1yOIEMWmcuiI8iNF7O0Mk5mF58SXBV9vRMFYmWniytQUdL3JXiCK-_u63-yHKdlLwgJQMLwvM7XNjiYwNjZI0lHYe1NokTNXL_mpoqnMPovCarU6qT9sNpXY0ufeqGha1hmUE19XlQ5Xr-8yQ1oARYDY1MSO7N9V3jV4RvgCBXBhcz3EYMR1uQwbBibANHWVYTFrVVSd8BNg5_adsCvXT8ZTBg5Kri_knXuvwZO_Ng"


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


ic("Get available Shapes")
response = requests.get("http://localhost:8085/getAvailableShapesCategorized?ecoSystem=gax-trust-framework")
ic(response.status_code)

ic("Get shape for SD of Legal Person")
response = requests.get("http://localhost:8085/getJSON?name=Legal%20Person.json")
ic(response.status_code)
shape_json = json.loads(response.text)

# extract prefixes and fields from the json
prefixes = shape_json["prefixList"]
fields = shape_json["shapes"]

target_schema = fields[0]  # for now assume that the first listed schema is our target, # TODO this might be wrong

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
        context[p["alias"]] = p["url"].replace("http", "https")  # for gax-trust-framework we need an https instead of http, this is a bug of the wizard
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

#ic(presentation)

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

# send the signed presentation to the catalog API endpoint
ic("Sending signed vp to catalog API")
response = requests.post("http://localhost:8081/participants", headers={'Authorization': 'Bearer ' + access_token,
                                                                        "Content-Type": "application/json"}, data=json.dumps(d))
ic(response.status_code)

# retreive stored data in the catalog
ic("Retrieving stored data in catalog")
response = requests.get("http://localhost:8081/participants", headers={'Authorization': 'Bearer ' + access_token,
                                                                        "accept": "application/json"})
ic(response.status_code, json.loads(response.text))

# delete previously created endpoint
ic("Deleting previously created vp")
response = requests.delete("http://localhost:8081/participants/http%3A%2F%2Fgaiax.de", headers={'Authorization': 'Bearer ' + access_token,
                                                                        "accept": "application/json"})
ic(response.status_code)
