#!/usr/bin/env python

# Copyright (c) 2022-2026 The Project Contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For a detailed list of copyright holders and contribution history,
# please refer to the CONTRIBUTORS.md file in the project root.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import traceback
import socket
import os

try:
    from urllib.request import HTTPHandler
except ImportError:
    from ansible.module_utils.urls import (
        UnixHTTPHandler as HTTPHandler,
    )

try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection

try:
    from suds.client import Client
    from suds.sudsobject import asdict
    from suds.transport.http import HttpAuthenticated, HttpTransport
    HAS_SUDS_LIBRARY = True
    SUDS_LIBRARY_IMPORT_ERROR = None

    class LocalSocketHttpAuthenticated(HttpAuthenticated):
        """Authenticated HTTP transport using Unix domain sockets."""
        def __init__(self, socketpath, **kwargs):
            HttpAuthenticated.__init__(self, **kwargs)
            self._socketpath = socketpath

        def u2handlers(self):
            handlers = HttpTransport.u2handlers(self)
            handlers.append(LocalSocketHandler(socketpath=self._socketpath))
            return handlers

except ImportError:
    HAS_SUDS_LIBRARY = False
    SUDS_LIBRARY_IMPORT_ERROR = traceback.format_exc()

    # Dummy class when suds is not available (keeps imports stable in tests)
    class LocalSocketHttpAuthenticated(object):
        def __init__(self, socketpath, **kwargs):
            pass

        def u2handlers(self):
            return []

# Constant that defines accepted function prefixes, that are not doing changes.
READ_ONLY_FUNCTION_PREFIXES = (
    "get",
    "list",
    "enqget",
    "abapget",
    "icmget",
    "cmget",
    "webdispget",
)

# Constants that define if force mode is required for certain functions.
FORCE_REQUIRED_PREFIXES = ("stop", "restart")
FORCE_REQUIRED_EXACT = ("shutdown", "instancestop")


class LocalSocketHttpConnection(HTTPConnection):
    """HTTP connection class that uses Unix domain sockets."""
    def __init__(self, host, port=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None, socketpath=None):
        super(LocalSocketHttpConnection, self).__init__(host, port, timeout, source_address)
        self.socketpath = socketpath

    def connect(self):
        """Connect to Unix domain socket."""
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socketpath)


class LocalSocketHandler(HTTPHandler):
    """HTTP handler for Unix domain sockets."""
    def __init__(self, debuglevel=0, socketpath=None):
        self._debuglevel = debuglevel
        self._socketpath = socketpath

    def http_open(self, req):
        return self.do_open(LocalSocketHttpConnection, req, socketpath=self._socketpath)


def is_read_only_function(function_name):
    """Return True for read-only functions (e.g. Get*, List*)."""
    if not function_name:
        return False
    fname = function_name.strip().lower()
    return any(fname.startswith(prefix) for prefix in READ_ONLY_FUNCTION_PREFIXES)


def requires_force(function_name):
    """Return True when function should require force=True."""
    if not function_name:
        return False
    fname = function_name.strip().lower()
    return fname in FORCE_REQUIRED_EXACT or fname.startswith(FORCE_REQUIRED_PREFIXES)


def recursive_dict(suds_object):
    """Convert a suds object to a plain Python dict, recursively.

    Example output: ``{'item': [{'name': 'hdbdaemon', 'value': '1'}]}``
    """
    out = {}
    if isinstance(suds_object, str):
        return suds_object
    for k, v in asdict(suds_object).items():
        if hasattr(v, '__keylist__'):
            out[k] = recursive_dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(recursive_dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def connection(service_name, hostname, port, username, password, sysnr=None, is_socket=False):
    """
    Return a SOAP client for the given service (sapcontrol or saphostctrl).
    """
    # Prepare connection details before attempting to connect.
    if is_socket:
        # Use Unix domain socket for local connection
        if sysnr is not None:
            # sapcontrol: The socket name includes the system number
            unix_socket = "/tmp/.sapstream5{0}13".format(str(sysnr).zfill(2))
        else:
            # saphostctrl: The socket name is fixed
            unix_socket = "/tmp/.sapstream1128"

        connection_url = "http://localhost/{0}?wsdl".format(service_name)

    else:
        # Use HTTP connection (original behavior)
        connection_url = 'http://{0}:{1}/{2}?wsdl'.format(hostname, port, service_name)

    # Attempt to connect using the appropriate method
    try:
        if is_socket:
            if not os.path.exists(unix_socket):
                raise Exception("SAP control Unix socket not found: {0}".format(unix_socket))

            localsocket = LocalSocketHttpAuthenticated(unix_socket)
            client = Client(connection_url, transport=localsocket)
        else:
            client = Client(connection_url, username=username, password=password, timeout=10)

        return client

    except Exception as e:
        raise e


def call_sap_control(hostname, port, username, password, function, parameters, sysnr=None, is_socket=False):
    client = connection(
        "sapcontrol", hostname, port, username, password, sysnr=sysnr, is_socket=is_socket)
    return call_function(client, function, parameters)


def call_sap_hostctrl(hostname, port, username, password, function, parameters, is_socket=False):
    client = connection(
        "SAPHostControl/", hostname, port, username, password, sysnr=None, is_socket=is_socket)
    return call_function(client, function, parameters)


def call_function(client, function, parameters=None):
    _function = getattr(client.service, function)
    if parameters is not None:
        if isinstance(parameters, dict):
            result = _function(**parameters)
        else:
            result = _function(parameters)
    else:
        result = _function()
    return result
