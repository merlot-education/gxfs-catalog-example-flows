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

from icecream import ic
from datetime import datetime


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
    "@id": "did:web:marketplace.dev.merlot-education.eu",
    "@type": "merlot:MerlotOrganization",
    "gax-trust-framework:headquarterAddress": {
        "vcard:country-name": {
            "@value": "DE",
            "@type": "xsd:string"
        },
        "vcard:postal-code": {
            "@value": "12345",
            "@type": "xsd:string"
        },
        "vcard:street-address": {
            "@value": "Some Str. 123",
            "@type": "xsd:string"
        },
        "vcard:locality": {
            "@type": "xsd:string",
            "@value": "Berlin"
        },
        "@type": "vcard:Address"
    },
    "gax-trust-framework:legalAddress": {
                "vcard:country-name": {
            "@value": "DE",
            "@type": "xsd:string"
        },
        "vcard:postal-code": {
            "@value": "12345",
            "@type": "xsd:string"
        },
        "vcard:street-address": {
            "@value": "Some Str. 123",
            "@type": "xsd:string"
        },
        "vcard:locality": {
            "@type": "xsd:string",
            "@value": "Berlin"
        },
        "@type": "vcard:Address"
    },
    "gax-trust-framework:registrationNumber": {
        "gax-trust-framework:local": {
            "@value": "12345",
            "@type": "xsd:string"
        },
        "@type": "gax-trust-framework:RegistrationNumber"
    },
    "gax-trust-framework:legalName": {
        "@value": "Example Org",
        "@type": "xsd:string"
    },
    "merlot:termsAndConditions": {
        "@type": "gax-trust-framework:TermsAndConditions",
        "gax-trust-framework:content": {
            "@type": "xsd:anyURI",
            "@value": "http://example.org"
        },
        "gax-trust-framework:hash": {
            "@type": "xsd:string",
            "@value": "1234"
        }
    },
    "merlot:orgaName": {
        "@value": "Example",
        "@type": "xsd:string"
    }
}


presentation = {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "@id": "http://example.edu/verifiablePresentation/self-description1",
    "type": ["VerifiablePresentation"],
    "verifiableCredential": [
        {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "@id": "https://www.example.org/legalPerson.json",
        "@type": ["VerifiableCredential"],
        "issuer": "did:web:marketplace.dev.merlot-education.eu",
        "issuanceDate": (datetime.utcnow()).isoformat() + 'Z',
        "credentialSubject": participant_data
        }
    ]
}

ic("Storing unsigned vp as file")
with open('vp.json', 'w', encoding='utf-8') as f:
    json.dump(presentation, f, ensure_ascii=False, indent=4, sort_keys=True)

ic("Calling signer to sign unsigned vp")
os.system("java -jar gxfsTest-0.1.0-jar-with-dependencies.jar vp.json vp.signed.json ~/workspace/mpo/marketplace.dev.merlot-education.eu.pkcs8.key ~/workspace/mpo/marketplace.dev.merlot-education.eu.public.crt")

ic("Load signed vp from file")
d = None
with open('vp.signed.json') as f:
    d = json.load(f)
