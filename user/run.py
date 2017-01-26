"""Azure Functions HTTP Example Code for Python"""

# FYI: This file is named "run.py". The "run" part is the naming convention
# used by Azure Functions to find your primary function script and then run it.
# See https://github.com/Azure/azure-webjobs-sdk-script/blob/v1.0.10690/src/WebJobs.Script/Host/ScriptHost.cs#L760

# Boilerplate begins
import sys, os
func_path = os.path.dirname( __file__ )
sys.path.append(os.path.abspath(os.path.join(func_path, '..', 'lib')))
from azurefunctions import Context
ctx = Context(os.path.join(func_path, "function.json"))
# Boilerplate ends


# Your own function code starts from here
import json
import itertools

from azurefunctions import is_subdict_of


def beautify(a_dict):  # Your own helper function(s), if needed
    return json.dumps(a_dict, indent=2)

query = ctx.req["query"]
lab_data = json.load(open(os.path.join("..", "labdata.json")))
users_from_chosen_labs = list(itertools.chain.from_iterable(
    lab["users"] for lab in lab_data["labs"]
    if lab["federationProvider"] == query.get("federationProvider", "none")))
query.pop("federationProvider", None)
users = [user for user in users_from_chosen_labs if is_subdict_of(query, user)]
ctx.done(body=beautify(users), headers={"Content-Type": "text/json"})

