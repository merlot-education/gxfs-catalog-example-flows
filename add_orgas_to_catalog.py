import json
import os

import requests
from icecream import ic

from utils import get_access_token, checkResponse

from config import oauth_user,oauth_pass, oauth_url, oauth_client_secret, catalog_api_base

with open('orgas.json') as f:
    d = json.load(f)

for sd in d:
    ic(sd)
    participant_data = {
        "@context": {
            "gax-trust-framework": "http://w3id.org/gaia-x/gax-trust-framework#",
            "gax-validation": "http://w3id.org/gaia-x/validation#",
            "merlot": "http://w3id.org/gaia-x/merlot#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "sh": "http://www.w3.org/ns/shacl#",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "vcard": "http://www.w3.org/2006/vcard/ns#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@id": sd["id"],
        "@type": "merlot:MerlotOrganization",
        "gax-trust-framework:headquarterAddress": {
            "vcard:country-name": {
                "@value": sd["legalAddress"]["countryCode"],
                "@type": "xsd:string"
            },
            "vcard:postal-code": {
                "@value": sd["legalAddress"]["postalCode"],
                "@type": "xsd:string"
            },
            "vcard:street-address": {
                "@value": sd["legalAddress"]["street"],
                "@type": "xsd:string"
            },
            "vcard:locality": {
                "@type": "xsd:string",
                "@value": sd["legalAddress"]["city"]
            },
            "@type": "vcard:Address"
        },
        "gax-trust-framework:legalAddress": {
            "vcard:country-name": {
                "@value": sd["legalAddress"]["countryCode"],
                "@type": "xsd:string"
            },
            "vcard:postal-code": {
                "@value": sd["legalAddress"]["postalCode"],
                "@type": "xsd:string"
            },
            "vcard:street-address": {
                "@value": sd["legalAddress"]["street"],
                "@type": "xsd:string"
            },
            "vcard:locality": {
                "@type": "xsd:string",
                "@value": sd["legalAddress"]["city"]
            },
            "@type": "vcard:Address"
        },
        "gax-trust-framework:registrationNumber": {
            "gax-trust-framework:local": {
                "@value": sd["registrationNumber"],
                "@type": "xsd:string"
            },
            "@type": "gax-trust-framework:RegistrationNumber"
        },
        "gax-trust-framework:legalName": {
            "@value": sd["organizationLegalName"],
            "@type": "xsd:string"
        },
        "merlot:termsConditionsLink": {
            "@value": sd["termsAndConditionsLink"],
            "@type": "xsd:string"
        },
        "merlot:orgaName": {
            "@value": sd["organizationName"],
            "@type": "xsd:string"
        },
        "merlot:merlotId": {
            "@value": sd["merlotId"],
            "@type": "xsd:string"
        },
        "merlot:addressCode": {
            "@value": sd["legalAddress"]["addressCode"],
            "@type": "xsd:string"
        },
        "merlot:connectorId": {
            "@value": sd["connectorId"],
            "@type": "xsd:string"
        },
        "merlot:connectorPublicKey": {
            "@value": sd["connectorPublicKey"],
            "@type": "xsd:string"
        },
        "merlot:connectorBaseUrl": {
            "@value": sd["connectorBaseUrl"],
            "@type": "xsd:string"
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
