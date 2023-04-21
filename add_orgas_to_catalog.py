import json
import os

import requests
from icecream import ic

from utils import get_access_token, checkResponse

sd_wizard_api_base = "http://localhost:8085"
catalog_api_base = "http://localhost:8081"
oauth_url = "http://key-server:8080/realms/gaia-x/protocol/openid-connect/token"
oauth_client_secret = "KEJER0ZJAc7iTdXOtLFePgbphuuEFFu9"
oauth_user = "user"
oauth_pass = "user"

with open('orgas.json') as f:
    d = json.load(f)

for sd in d:
    ic(sd)
    participant_data = {
        "@id": sd["id"],
        "@type": "merlot:MerlotOrganization",
        "@context": {
            "cc": "http://creativecommons.org/ns#",
            "cred": "https://www.w3.org/2018/credentials#",
            "dcat": "http://www.w3.org/ns/dcat#",
            "dct": "http://purl.org/dc/terms/",
            "did": "https://www.w3.org/TR/did-core/#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "gax-core": "http://w3id.org/gaia-x/core#",
            "gax-trust-framework": "https://w3id.org/gaia-x/gax-trust-framework#",
            "merlot": "https://w3id.org/gaia-x/merlot#",
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
        "merlot:legalAddress": {
            "@type": "vcard:Address",
            "vcard:country-name": {
                "@type": "xsd:string",
                "@value": sd["legalAddress"]["countryCode"]
            },
            "vcard:locality": {
                "@type": "xsd:string",
                "@value": sd["legalAddress"]["city"]
            },
            "vcard:postal-code": {
                "@type": "xsd:string",
                "@value": sd["legalAddress"]["postalCode"]
            },
            "vcard:street-address": {
                "@type": "xsd:string",
                "@value": sd["legalAddress"]["street"]
            }
        },
        "merlot:legalName": {
            "@type": "xsd:string",
            "@value": sd["organizationLegalName"]
        },
        "merlot:registrationNumber": {
            "@type": "xsd:string",
            "@value": sd["registrationNumber"]
        },
        "merlot:merlotID": {
            "@type": "xsd:string",
            "@value": sd["merlotId"]
        },
        "merlot:orgaName": {
            "@type": "xsd:string",
            "@value": sd["organizationName"]
        },
        "merlot:addressCode": {
            "@type": "xsd:string",
            "@value": sd["legalAddress"]["addressCode"]
        },
        "merlot:termsAndConditionsLink": {
            "@type": "xsd:string",
            "@value": sd["termsAndConditionsLink"]
        }
    }
    issuer = sd["id"]

    presentation = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "@id": "http://example.edu/verifiablePresentation/self-description1",
        "type": ["VerifiablePresentation"],
        "verifiableCredential": {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "@id": "https://www.example.org/legalPerson.json",
            "@type": ["VerifiableCredential"],
            "issuer": issuer,
            "issuanceDate": "2022-10-19T18:48:09Z",
            "credentialSubject": participant_data
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
    response = requests.post(catalog_api_base + "/participants", headers={'Authorization': 'Bearer ' + access_token,
                                                                          "Content-Type": "application/json"},
                             data=json.dumps(d))
    checkResponse(response, valid_response_code=201)
