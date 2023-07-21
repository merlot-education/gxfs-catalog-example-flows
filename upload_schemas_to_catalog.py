from icecream import ic
from utils import get_access_token, checkResponse
import os
import requests
import json

from config import oauth_user,oauth_pass, oauth_url, oauth_client_secret, catalog_api_base

ontology_base_folder = "/home/mbuskies/workspace/gxfs/service-characteristics/yaml2ontology/"
merged_shapes_path = "/home/mbuskies/workspace/gxfs/service-characteristics/yaml2shacl/mergedShapes.ttl"

# retrieve oauth2 access token
ic("Retrieving access token from oauth2 server")
response = get_access_token(oauth_url,
                            "federated-catalogue",
                            oauth_client_secret, oauth_user, oauth_pass)
checkResponse(response)
access_token = response.json()["access_token"]
ic(access_token)

# retreive stored data in the catalog and clean existing ontologies/shapes
ic("Retrieving stored schemas in catalog")
response = requests.get(catalog_api_base + "/schemas", headers={'Authorization': 'Bearer ' + access_token,
                                                                     "accept": "application/json"})
checkResponse(response)
schemas_json = json.loads(response.text)

if schemas_json["ontologies"]:
    for ontology in schemas_json["ontologies"]:
        print("Deleting Ontology", ontology)
        response = requests.delete(catalog_api_base + "/schemas/" + ontology.replace(":", "%3A").replace("/", "%2F")
                                   .replace("#", "%23")
                                   , headers={'Authorization': 'Bearer ' + access_token,
                                                                        "accept": "application/json"})
        checkResponse(response)

if schemas_json["shapes"]:
    for shape in schemas_json["shapes"]:
        print("Deleting Shape", shape)
        response = requests.delete(catalog_api_base + "/schemas/" + shape,
                                   headers={'Authorization': 'Bearer ' + access_token,
                                              "accept": "application/json"})
        checkResponse(response)

# upload the new available ontologies and shapes
for root, dirs, files in os.walk(ontology_base_folder, topdown=False):
   for name in files:
       print("Uploading Ontology ", name)
       with open(os.path.join(root, name), "rb") as f:
           response = requests.post(catalog_api_base + "/schemas",
                                      headers={'Authorization': 'Bearer ' + access_token,
                                               "accept": "application/json",
                                               "Content-Type":"text/turtle"},
                                    data=f.read())
           checkResponse(response, valid_response_code=201)


print("Uploading Shape ", merged_shapes_path)
with open(merged_shapes_path, "rb") as f:
   response = requests.post(catalog_api_base + "/schemas",
                            headers={'Authorization': 'Bearer ' + access_token,
                                     "accept": "application/json",
                                     "Content-Type": "text/turtle"},
                            data=f.read())
   checkResponse(response, valid_response_code=201)