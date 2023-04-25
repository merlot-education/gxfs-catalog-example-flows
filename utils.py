from icecream import ic
import json
import requests

def checkResponse(response, valid_response_code=200):
    ic(response.status_code)
    if response.status_code != valid_response_code:
        ic(json.loads(response.text))
        exit()

def resolveSchema(schema, all_schemas, entryValues={}):
    # initialize a dict for our current entry and set the type field according to the schema
    entry = {}
    entry["@type"] = schema["targetClassPrefix"] + ":" + schema["targetClassName"]
    # for our schema iterate through all constraints and save the path
    for constraint in schema["constraints"]:
        path = constraint["path"]["prefix"] + ":" + constraint["path"]["value"]
        if path in entryValues.keys():
            if "children" in constraint.keys():  # if we have children, we have a nested schema
                subschema = all_schemas[constraint["children"]]
                entry[path] = resolveSchema(subschema, all_schemas, entryValues[path])
            else:  # otherwise we simply resolve all constraints and add them to the dict
                datatype = constraint["datatype"]["prefix"] + ":" + constraint["datatype"]["value"]
                if datatype == "nodeKind:IRI":
                    entry[path] = {
                        "@type": datatype,
                        "@id": entryValues[path]
                    }
                else:
                    entry[path] = {
                        "@type": datatype,
                        "@value": entryValues[path]
                    }
        elif "minCount" in constraint.keys():
            ic("required field was not populated, exiting...")
            ic(constraint)
            exit()
    return entry


def get_access_token(url, client_id, client_secret, user, password):
    response = requests.post(url, data={
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': user,
        'password': password
    })
    return response