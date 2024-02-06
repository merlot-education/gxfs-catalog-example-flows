import json
import os

import requests
from icecream import ic

from utils import get_access_token, checkResponse

from config import oauth_user, oauth_pass, oauth_url, oauth_client_secret, catalog_api_base

# retrieve oauth2 access token
ic("Retrieving access token from oauth2 server")
response = get_access_token(oauth_url,
                            "federated-catalogue",
                            oauth_client_secret, oauth_user, oauth_pass)
checkResponse(response)
access_token = response.json()["access_token"]
ic(access_token)

# send the signed presentation to the catalog API endpoint
ic("Getting list of offerings")
response = requests.get(catalog_api_base + "/self-descriptions?statuses=REVOKED,ACTIVE,DEPRECATED",
                        headers={'Authorization': 'Bearer ' + access_token,
                                                                     "Content-Type": "application/json"})
checkResponse(response, valid_response_code=200)
ic(response.text)

for p in json.loads(response.text)["items"]:
    #if p["meta"]["id"].startswith("ServiceOffering"):
    ic("Deleting offering", p["meta"]["id"])
    response = requests.delete(catalog_api_base + "/self-descriptions/" + p["meta"]["sdHash"]
                                , headers={'Authorization': 'Bearer ' + access_token,
                                            "Content-Type": "application/json"})
    checkResponse(response, valid_response_code=200)
