"""
  Copyright 2024 Dataport. All rights reserved. Developed as part of the MERLOT project.
  
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  
      http://www.apache.org/licenses/LICENSE-2.0
  
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""
from icecream import ic
from utils import get_access_token, checkResponse
import os
import requests
import json

from config import oauth_user,oauth_pass, oauth_url, oauth_client_secret, catalog_api_base

ontology_base_folder = os.path.expanduser("~/workspace/mpo/catalog-shapes/catalog-shapes/shacl/ontology/")
merged_shapes_path = os.path.expanduser("~/workspace/mpo/catalog-shapes/catalog-shapes/shacl/shapes/mergedShapes.ttl")

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