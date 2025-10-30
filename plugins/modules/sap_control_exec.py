#!/usr/bin/python

# Copyright: (c) 2022, Rainer Leber rainerleber@gmail.com, rainer.leber@sva.de,
#                      Robert Kraemer @rkpobe, robert.kraemer@sva.de
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sap_control_exec

short_description: Ansible Module to execute SAPCONTROL

version_added: "1.1.0"

description:
    - Provides support for sapstartsrv formaly known as sapcontrol
    - A complete information of all functions and the parameters can be found here
      U(https://www.sap.com/documents/2016/09/0a40e60d-8b7c-0010-82c7-eda71af511fa.html)
    - When hostname is 'localhost', sysnr is set and no username/password are provided, the module will attempt
      to use local Unix socket authentication (which works with 'become' privilege escalation).

options:
    sysnr:
        description:
            - The system number of the instance.
        required: false
        type: str
    port:
        description:
            - The port number of the sapstartsrv.
            - If provided, the module will use always use http connection instead of local socket.
        required: false
        type: int
    username:
        description:
            - The username to connect to the sapstartsrv.
        required: false
        type: str
    password:
        description:
            - The password to connect to the sapstartsrv.
        required: false
        type: str
    hostname:
        description:
            - The hostname to connect to the sapstartsrv.
            - Could be an IP address, FQDN or hostname.
        required: false
        default: localhost
        type: str
    function:
        description:
        - The function to execute.
        required: true
        choices:
        - Start
        - Stop
        - Shutdown
        - InstanceStart
        - InstanceStop
        - Bootstrap
        - ParameterValue
        - GetProcessList
        - GetProcessList2
        - GetStartProfile
        - GetTraceFile
        - GetAlertTree
        - GetAlerts
        - RestartService
        - StopService
        - GetEnvironment
        - ListDeveloperTraces
        - ListLogFiles
        - ReadDeveloperTrace
        - ReadLogFile
        - AnalyseLogFile
        - ConfigureLogFileList
        - GetLogFileList
        - RestartInstance
        - SendSignal
        - GetVersionInfo
        - GetQueueStatistic
        - GetInstanceProperties
        - OSExecute
        - AnalyseLogFiles
        - GetAccessPointList
        - GetSystemInstanceList
        - StartSystem
        - StopSystem
        - RestartSystem
        - AccessCheck
        - GetProcessParameter
        - SetProcessParameter
        - SetProcessParameter2
        - ShmDetach
        - CreateSnapshot
        - ReadSnapshot
        - ListSnapshots
        - DeleteSnapshots
        - RequestLogonFile
        - GetNetworkId
        - GetSecNetworkId
        - UpdateSystem
        - GetSystemUpdateList
        - UpdateSCSInstance
        - ABAPReadSyslog
        - ABAPReadRawSyslog
        - ABAPGetWPTable
        - ABAPAcknoledgeAlerts
        - CMGetThreadList
        - ICMGetConnectionList
        - ICMGetCacheEntries
        - ICMGetProxyConnectionList
        - WebDispGetServerList
        - WebDispGetGroupList
        - WebDispGetVirtHostList
        - WebDispGeUrlPrefixList
        - EnqGetLockTable
        - EnqRemoveLocks
        - EnqGetStatistic
        type: str
    parameter:
        description:
            - The parameter to pass to the function.
        required: false
        type: str
    force:
        description:
            - Forces the execution of the function C(Stop).
        required: false
        default: false
        type: bool
author:
    - Rainer Leber (@RainerLeber)
    - Robert Kraemer (@rkpobe)
notes:
    - Does not support C(check_mode).
'''

EXAMPLES = r"""
- name: GetProcessList with sysnr
  community.sap_libs.sap_control_exec:
    hostname: 192.168.8.15
    sysnr: "01"
    function: GetProcessList

- name: GetProcessList with custom port
  community.sap_libs.sap_control_exec:
    hostname: 192.168.8.15
    function: GetProcessList
    port: 50113

- name: ParameterValue with authentication
  community.sap_libs.sap_control_exec:
    hostname: 192.168.8.15
    sysnr: "01"
    username: hdbadm
    password: test1234
    function: ParameterValue
    parameter: ztta

- name: GetVersionInfo using local Unix socket (requires become)
  community.sap_libs.sap_control_exec:
    sysnr: "00"
    function: GetVersionInfo
  become: true

- name: GetProcessList using local Unix socket as SAP admin user
  community.sap_libs.sap_control_exec:
    sysnr: "00"
    function: GetProcessList
  become: true
  become_user: "{{ sap_sid | lower }}adm"
"""

RETURN = r'''
msg:
    description: Success-message with functionname.
    type: str
    returned: always
    sample: 'Succesful execution of: GetProcessList'
out:
    description: The full output of the required function.
    type: list
    elements: dict
    returned: always
    sample: [{
            "item": [
                {
                    "description": "MessageServer",
                    "dispstatus": "SAPControl-GREEN",
                    "elapsedtime": "412:30:50",
                    "name": "msg_server",
                    "pid": 70643,
                    "starttime": "2022 03 13 15:22:42",
                    "textstatus": "Running"
                },
                {
                    "description": "EnqueueServer",
                    "dispstatus": "SAPControl-GREEN",
                    "elapsedtime": "412:30:50",
                    "name": "enserver",
                    "pid": 70644,
                    "starttime": "2022 03 13 15:22:42",
                    "textstatus": "Running"
                },
                {
                    "description": "Gateway",
                    "dispstatus": "SAPControl-GREEN",
                    "elapsedtime": "412:30:50",
                    "name": "gwrd",
                    "pid": 70645,
                    "starttime": "2022 03 13 15:22:42",
                    "textstatus": "Running"
                }
                ]
            }]
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
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

    # Define dummy class when suds is not available
    class LocalSocketHttpAuthenticated(object):
        def __init__(self, socketpath, **kwargs):
            pass

        def u2handlers(self):
            return []


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


def choices():
    retlist = ["Start", "Stop", "Shutdown", "InstanceStart", "InstanceStop", "Bootstrap", "ParameterValue", "GetProcessList",
               "GetProcessList2", "GetStartProfile", "GetTraceFile", "GetAlertTree", "GetAlerts", "RestartService",
               "StopService", "GetEnvironment", "ListDeveloperTraces", "ListLogFiles", "ReadDeveloperTrace", "ReadLogFile",
               "AnalyseLogFile", "ConfigureLogFileList", "GetLogFileList", "RestartInstance", "SendSignal", "GetVersionInfo",
               "GetQueueStatistic", "GetInstanceProperties", "OSExecute", "AnalyseLogFiles", "GetAccessPointList",
               "GetSystemInstanceList", "StartSystem", "StopSystem", "RestartSystem", "AccessCheck", "GetProcessParameter",
               "SetProcessParameter", "SetProcessParameter2", "ShmDetach", "CreateSnapshot", "ReadSnapshot", "ListSnapshots",
               "DeleteSnapshots", "RequestLogonFile", "GetNetworkId", "GetSecNetworkId", "UpdateSystem", "GetSystemUpdateList",
               "UpdateSCSInstance", "ABAPReadSyslog", "ABAPReadRawSyslog", "ABAPGetWPTable", "ABAPAcknoledgeAlerts",
               "CMGetThreadList", "ICMGetConnectionList", "ICMGetCacheEntries", "ICMGetProxyConnectionList",
               "WebDispGetServerList", "WebDispGetGroupList", "WebDispGetVirtHostList", "WebDispGeUrlPrefixList",
               "EnqGetLockTable", "EnqRemoveLocks", "EnqGetStatistic"]
    return retlist


# converts recursively the suds object to a dictionary e.g. {'item': [{'name': hdbdaemon, 'value': '1'}]}
def recursive_dict(suds_object):
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


def connection(hostname, port, username, password, function, parameter, sysnr=None, use_local=False):
    if use_local and sysnr is not None:
        # Use Unix domain socket for local connection
        unix_socket = "/tmp/.sapstream5{0}13".format(str(sysnr).zfill(2))

        # Check if socket exists
        if not os.path.exists(unix_socket):
            raise Exception("SAP control Unix socket not found: {0}".format(unix_socket))

        url = "http://localhost/sapcontrol?wsdl"

        try:
            localsocket = LocalSocketHttpAuthenticated(unix_socket)
            client = Client(url, transport=localsocket)
        except Exception as e:
            raise Exception("Failed to connect via Unix socket: {0}".format(str(e)))
    else:
        # Use HTTP connection (original behavior)
        url = 'http://{0}:{1}/sapcontrol?wsdl'.format(hostname, port)
        client = Client(url, username=username, password=password)

    _function = getattr(client.service, function)
    if parameter is not None:
        result = _function(parameter)
    elif function == "StartSystem":
        result = _function(waittimeout=0)
    elif function == "StopSystem" or function == "RestartSystem":
        result = _function(waittimeout=0, softtimeout=0)
    else:
        result = _function()

    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            sysnr=dict(type='str', required=False),
            port=dict(type='int', required=False),
            username=dict(type='str', required=False),
            password=dict(type='str', no_log=True, required=False),
            hostname=dict(type='str', default="localhost"),
            function=dict(type='str', required=True, choices=choices()),
            parameter=dict(type='str', required=False),
            force=dict(type='bool', default=False),
        ),
        # Remove strict requirements to allow local mode
        required_one_of=[('sysnr', 'port')],
        mutually_exclusive=[('sysnr', 'port')],
        supports_check_mode=False,
    )
    result = dict(changed=False, msg='', out={}, error='')
    params = module.params

    sysnr = params['sysnr']
    port = params['port']
    username = params['username']
    password = params['password']
    hostname = params['hostname']
    function = params['function']
    parameter = params['parameter']
    force = params['force']

    if not HAS_SUDS_LIBRARY:
        module.fail_json(
            msg=missing_required_lib('suds'),
            exception=SUDS_LIBRARY_IMPORT_ERROR)

    # Validate arguments
    if sysnr is None and port is None:
        module.fail_json(msg="Either 'sysnr' or 'port' must be provided")

    if sysnr is not None and port is not None:
        module.fail_json(msg="'sysnr' and 'port' are mutually exclusive")

    if function == "Stop":
        if force is False:
            module.fail_json(msg="Stop function requires force: True")

    # Determine if we should use local Unix socket connection
    # Use local if hostname is localhost and no username/password provided
    use_local = (hostname == "localhost" and
                 username is None and
                 password is None and
                 sysnr is not None)

    if port is None:
        try:
            if use_local:
                # Try local connection first
                conn = connection(hostname, None, username, password, function, parameter, sysnr, use_local=True)
            else:
                # Try HTTP ports
                try:
                    conn = connection(hostname, "5{0}14".format((sysnr).zfill(2)), username, password, function, parameter, sysnr)
                except Exception:
                    conn = connection(hostname, "5{0}13".format((sysnr).zfill(2)), username, password, function, parameter, sysnr)
        except Exception as err:
            result['error'] = str(err)
    else:
        try:
            conn = connection(hostname, port, username, password, function, parameter, sysnr, use_local=False)
        except Exception as err:
            result['error'] = str(err)

    if result['error'] != '':
        connection_type = "Unix socket" if use_local else "SOAP API"
        result['msg'] = 'Something went wrong connecting to the {0}.'.format(connection_type)
        module.fail_json(**result)

    if conn is not None:
        returned_data = recursive_dict(conn)
    else:
        returned_data = conn

    result['changed'] = True
    result['msg'] = "Succesful execution of: " + function
    result['out'] = [returned_data]

    module.exit_json(**result)


if __name__ == '__main__':
    main()
