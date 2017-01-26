# Copyright (c) Ray Luo
# All rights reserved.
#
# This code is licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import json
import urlparse


class Context(object):
    """A helper for Azure Functions (AF).

    This class is inspired from its Node.js counterpart
    https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-node
    """

    def __init__(self, function_setting_path):
        # For each item in function.json, you will be able to access it by
        #    context.bindings["binding_name"]["name"]
        with open(function_setting_path) as f:
            self.bindings = {b['name']: b for b in json.load(f)["bindings"]}
        input_binding = find_first_matching(
            self.bindings.values(), {"direction": "in"})
        self.req = {
            "original_url": "TODO",
            "query": {},  # AF node also stores query strings in a dict "query"
            "params": {},  # TODO: Looks like Azure Functions treats the variables inside the url as param
                # https://github.com/Azure/azure-webjobs-sdk-script/tree/master/sample/HttpTrigger-CustomRoute-Get
            "headers": {},
            "env": {},
            "raw": open(os.environ[input_binding["name"]]).read()
                if os.getenv(input_binding["name"]) else "",
            "body": {},  # Note: AF node also names HTTP POST dict as "body"
                # https://github.com/Azure/azure-webjobs-sdk-script/blob/master/sample/HttpTrigger-CustomRoute-Post/index.js
            }
        if self.req["headers"].get("Content-Type") == "application/x-www-form-urlencoded":
            self.req["body"] = urlparse.parse_qs(self.req["raw"])
        for k in os.environ:
            if k[:12] == "REQ_HEADERS_":
                self.req["headers"][k[12:].lower()] = os.environ[k]
            elif k[:10] == "REQ_QUERY_":
                self.req["query"][k[10:].lower()] = os.environ[k]
            else:
                self.req["env"][k] = os.environ[k]  # k is in upper case

    def log(self, message):
        # In Azure Functions, the output on stdout will be logged
        print(str(message))

    def done(self, response=None, status=200, headers=None, body=""):
        # Note: this method signature is different than its Node.js counterpart
        # https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-node#contextdoneerrpropertybag
        if isinstance(headers, dict) and "Content-Type" not in headers:
            headers["Content-Type"] = (
		"text/html" if body.startswith('<') else 'text/plain')
        if not response:
            response = {"status": status, "headers": headers or {}, "body": body}
        response['isRaw'] = True  # https://github.com/Azure/azure-webjobs-sdk-script/issues/965
        http_output_binding = find_first_matching(
            self.bindings.values(), {"direction": "out", "type": "http"})
        assert http_output_binding, "Need at least one http output binding"
        if os.getenv(http_output_binding['name']):
            with open(os.environ[http_output_binding['name']], 'w') as f:
                json.dump(response, f)
        else:
            print(response['body'])  # For local debug

def is_subdict_of(small, big):
    "Tests whether the key/value pairs in dictionary small are a subset of those in big"
    return small.viewitems() <= big.viewitems()  # Python 2.7 only

def find_first_matching(list_of_dicts, filter, default=None):
    "In a list of dicts, find the first one which contains a given filter dict"
    return next((d for d in list_of_dicts if is_subdict_of(filter, d)), default)

