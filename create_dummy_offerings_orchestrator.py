"""
  Copyright 2023-2024 Dataport AöR
  
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
import json
import os
from tqdm import tqdm

import requests
from icecream import ic

from utils import get_access_token, checkResponse


response = get_access_token("http://key-server:8080/realms/POC1/protocol/openid-connect/token", "MARKETPLACE", "", "user", "user")
checkResponse(response)
access_token = response.json()["access_token"]


for sd_i in tqdm(range(50000)):
    #ic(sd_i)
    sd_data = {
      "@context": {
        "merlot": "http://w3id.org/gaia-x/merlot#",
        "dct": "http://purl.org/dc/terms/",
        "gax-trust-framework": "http://w3id.org/gaia-x/gax-trust-framework#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "sh": "http://www.w3.org/ns/shacl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "gax-validation": "http://w3id.org/gaia-x/validation#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "dcat": "http://www.w3.org/ns/dcat#",
        "gax-core": "http://w3id.org/gaia-x/core#"
      },
      "@id": "ServiceOffering:TBR",
      "@type": "merlot:MerlotServiceOfferingSaaS",
      "gax-trust-framework:name": {
        "@value": "DummyOffering" + str(sd_i),
        "@type": "xsd:string"
      },
      "gax-core:offeredBy": {
        "@id": "Participant:30"
      },
      "gax-trust-framework:providedBy": {
        "@id": "Participant:30"
      },
      "merlot:creationDate": {
        "@value": "26.05.2023, 11:43",
        "@type": "xsd:string"
      },
      "merlot:dataAccessType": {
        "@value": "Download",
        "@type": "xsd:string"
      },
      "gax-trust-framework:dataAccountExport": {
        "@type": "gax-trust-framework:DataAccountExport",
        "gax-trust-framework:requestType": {
          "@value": "dummyValue",
          "@type": "xsd:string"
        },
        "gax-trust-framework:accessType": {
          "@value": "dummyValue",
          "@type": "xsd:string"
        },
        "gax-trust-framework:formatType": {
          "@value": "dummyValue",
          "@type": "xsd:string"
        }
      },
      "gax-trust-framework:policy": {
        "@value": "dummyPolicy",
        "@type": "xsd:string"
      },
      "merlot:runtimeOption": {
        "@type": "merlot:Runtime",
        "merlot:runtimeUnlimited": True
      },
      "gax-trust-framework:termsAndConditions": {
        "@type": "gax-trust-framework:TermsAndConditions",
        "gax-trust-framework:content": {
          "@value": "asd",
          "@type": "xsd:anyURI"
        },
        "gax-trust-framework:hash": {
          "@value": "asd",
          "@type": "xsd:string"
        }
      },
      "merlot:userCountOption": {
        "@type": "merlot:AllowedUserCount",
        "merlot:userCountUnlimited": True
      },
      "merlot:merlotTermsAndConditionsAccepted": True
    }

    # send the signed presentation to the catalog API endpoint
    #ic("Sending signed vp to catalog API")
    response = requests.post("http://localhost:8084/api/serviceoffering/merlot:MerlotServiceOfferingSaaS",
                             headers={'Authorization': 'Bearer ' + access_token,
                                      "Content-Type": "application/json"},
                             data=json.dumps(sd_data))
    if response.status_code != 200:
        response = get_access_token("http://key-server:8080/realms/POC1/protocol/openid-connect/token", "MARKETPLACE", "",
                                    "user", "user")
        checkResponse(response)
        access_token = response.json()["access_token"]
