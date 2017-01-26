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

def beautify(a_dict):  # Your own helper function(s), if needed
    return json.dumps(a_dict, indent=2)

ctx.log("This log message will show up in Azure Functions log")

req = ctx.req  # shorthand
output = '\n'.join([  # Typically you prepare your output as a string
    "Headers: {}".format(beautify(req["headers"])),
    "Query: {}".format(beautify(req["query"])),
    "Body: {}".format(beautify(req["body"])),
    "Env: {}".format(beautify(req["env"])),
    "CWD: {}".format(os.getcwd()),
    "Python: {}".format(sys.version),
    ])
ctx.done(body=output)  # This will generate a successful HTTP 200 response

