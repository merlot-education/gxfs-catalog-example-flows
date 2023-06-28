import json
import os

import requests
from icecream import ic

from utils import get_access_token, checkResponse

from config import oauth_user,oauth_pass, oauth_url, oauth_client_secret, catalog_api_base

# retrieve oauth2 access token
ic("Retrieving access token from oauth2 server")
tokenResponse = get_access_token(oauth_url,
                            "federated-catalogue",
                            oauth_client_secret, oauth_user, oauth_pass)
checkResponse(tokenResponse)
access_token = tokenResponse.json()["access_token"]
ic(access_token)

organisationsResponse = requests.get(catalog_api_base + "/participants", headers={'Authorization': 'Bearer ' + access_token,
                                                                          "Content-Type": "application/json"})

checkResponse(organisationsResponse, valid_response_code=200)

ic(organisationsResponse.json())