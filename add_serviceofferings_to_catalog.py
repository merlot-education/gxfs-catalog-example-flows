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
import json
import os

import requests
from icecream import ic

from utils import get_access_token, checkResponse

from config import oauth_user,oauth_pass, oauth_url, oauth_client_secret, catalog_api_base

with open('serviceofferings.json') as f:
    d = json.load(f)

for sd in d:
    ic(sd)
    serviceoffering_data = {
        "@context": {
            "cc": "http://creativecommons.org/ns#",
            "cred": "https://www.w3.org/2018/credentials#",
            "dcat": "http://www.w3.org/ns/dcat#",
            "dct": "http://purl.org/dc/terms/",
            "did": "https://www.w3.org/TR/did-core/#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "gax-core": "https://w3id.org/gaia-x/core#",
            "gax-trust-framework": "https://w3id.org/gaia-x/gax-trust-framework#",
            "gax-validation": "http://w3id.org/gaia-x/validation#",
            "ids": "https://w3id.org/idsa/core/",
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "schema": "http://schema.org/",
            "sh": "http://www.w3.org/ns/shacl#",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "vann": "http://purl.org/vocab/vann/",
            "vcard": "http://www.w3.org/2006/vcard/ns#",
            "voaf": "http://purl.org/vocommons/voaf#",
            "void": "http://rdfs.org/ns/void#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@id": sd["id"],
        "@type": "gax-trust-framework:ServiceOffering",
        "gax-core:offeredBy": {
            "@id": sd["offeredBy"],
            "@type": "nodeKind:IRI"
        },
        "gax-trust-framework:dataAccountExport": {
            "@type": "gax-trust-framework:DataAccountExport",
            "gax-trust-framework:accessType": {
                "@type": "xsd:string",
                "@value": sd["dataAccountExportAccessType"]
            },
            "gax-trust-framework:formatType": {
                "@type": "xsd:string",
                "@value": sd["dataAccountExportFormatType"]
            },
            "gax-trust-framework:requestType": {
                "@type": "xsd:string",
                "@value": sd["dataAccountExportRequestType"]
            }
        },
        "gax-trust-framework:endpoint": {
            "@type": "gax-trust-framework:Endpoint",
            "gax-trust-framework:endPointURL": {
                "@type": "xsd:anyURI",
                "@value": sd["endPointUrl"]
            }
        },
        "gax-trust-framework:name": {
            "@type": "xsd:string",
            "@value": sd["name"]
        },
        "gax-trust-framework:policy": {
            "@type": "xsd:string",
            "@value": sd["policy"]
        },
        "gax-trust-framework:providedBy": {
            "@id": sd["providedBy"],
            "@type": "nodeKind:IRI"
        },
        "gax-trust-framework:termsAndConditions": {
            "@type": "gax-trust-framework:TermsAndConditions",
            "gax-trust-framework:content": {
                "@type": "xsd:anyURI",
                "@value": sd["termsAndConditionsUrl"]
            },
            "gax-trust-framework:hash": {
                "@type": "xsd:string",
                "@value": sd["termsAndConditionsHash"]
            }
        }
    }
    issuer = sd["issuer"]

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
            "credentialSubject": serviceoffering_data
        }
    }

    ic("Storing unsigned vp as file")
    with open('vp.json', 'w', encoding='utf-8') as f:
        json.dump(presentation, f, ensure_ascii=False, indent=4, sort_keys=True)

    ic("Calling signer to sign unsigned vp")
    os.system("java -jar gxfsTest-0.1.0-jar-with-dependencies.jar vp.json vp.signed.json")

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
    response = requests.post(catalog_api_base + "/self-descriptions",
                             headers={'Authorization': 'Bearer ' + access_token,
                                      "Content-Type": "application/json"},
                             data=json.dumps(d))
    checkResponse(response, valid_response_code=201)
