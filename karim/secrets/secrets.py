import json

def get_var(key="", parent="", default="", value=""):
    """
    Retrieve configuration variables from the secrets.json file.
    :variable: String of the name of the variable you are retrieving (see secrets.json)
    """
    variables = {}
    with open('karim/secrets/secrets.json') as variables_file:
        variables = json.load(variables_file)
    if value != "":
        if value in variables.values():
            print("Value {} is in secrets.json".format(value))
            return True
        else:
            print("Value {} is NOT in secrets.json".format(value))
            return False

    elif parent == "":
        requested = variables.get(str(key))
    else:
        requested = variables[parent][str(key)]
    if requested in ("", None, "insert_here", "insert_here_if_available"):
        if default == "":
            return None
        else:
            return default
    else:
        return requested


def set_var(key, value):
    """
    Set a variable to the env_variables.json file.
    :key: String (all caps) with the dictionary name of the variable (type str)
    :value: the value of the variable (type str)
    """
    with open('karim/secrets/secrets.json') as variables_file:
        variables = json.load(variables_file)

    if key in variables:
        del variables[key]
    variables[key] = value

    with open('karim/secrets/secrets.json', 'w') as output_file:
        json.dump(variables, output_file)
    print("SETTINGS: Set variable ", key)
