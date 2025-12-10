#!/usr/bin/python

# Copyright: (c) 2022, Rainer Leber rainerleber@gmail.com, rainer.leber@sva.de,
#                      Robert Kraemer @rkpobe, robert.kraemer@sva.de,
#                      Yannick Douvry, ydouvry@oxya.com
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
module: sap_hostctrl_exec

short_description: Ansible Module to execute SAPHostControl

version_added: "1.6.0"

description:
    - Provides support for SAP Host Agent
    - More information of some functions can be found here
      U(https://help.sap.com/docs/host-agent/saphostcontrol-web-service-interface)
    - When hostname is 'localhost' and no username/password are provided, the module will attempt
      to use local Unix socket authentication (which works with 'become' privilege escalation).

options:
    port:
        description:
            - The port number of the sapstartsrv (usually 1128 and 1129).
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
            - ACOSPrepare
            - AttachDatabase
            - CallServiceOperation
            - CancelOperation
            - ConfigureOutsideDiscovery
            - ConfigureOutsideDiscoveryDestination
            - ConfigureOutsideDiscoveryPath
            - DeployConfiguration
            - DeployManagedObjectsFromSAR
            - DetachDatabase
            - DetectManagedObjects
            - ExecuteDatabaseOperation
            - ExecuteInstallationProcedure
            - ExecuteOperation
            - ExecuteOutsideDiscovery
            - ExecuteUpgradeProcedure
            - FinalizeDatabaseCopy
            - GetCIMObject
            - GetComputerSystem
            - GetDatabaseProperties
            - GetDatabaseStatus
            - GetDatabaseSystemStatus
            - GetIpAddressProperties
            - GetOperationResults
            - ListDatabases
            - ListDatabaseSystems
            - ListInstances
            - LiveDatabaseUpdate
            - PrepareDatabaseCopy
            - RegisterInstanceService
            - SetDatabaseProperty
            - StartDatabase
            - StartInstance
            - StopDatabase
            - StopInstance
            - UnregisterInstanceService
        type: str
    parameters:
        description:
            - A dictionary containing all the parameters to pass to the function.
            - This option is mandatory for most of the functions, only a few like ListInstances or ListDatabases can be run without option.
            - Be careful, no validation is done by this module regarding the suboptions.
            - An analysis of the WSDL file must be done to provide correct parameters.
            - See also the examples section for more appreciation.
        required: false
        type: dict
    force:
        description:
            - Forces the execution of the function C(Stop).
        required: false
        default: false
        type: bool
author:
    - Rainer Leber (@RainerLeber)
    - Robert Kraemer (@rkpobe)
    - Yannick Douvry (@ydouvry)
notes:
    - Does not support C(check_mode).
'''


EXAMPLES = r"""
- name: ListDatabases with custom host and port
  community.sap_libs.sap_hostctrl_exec:
    hostname: 192.168.8.15
    function: ListDatabases
    port: 1128

- name: ListInstances using local Unix socket (requires become)
  community.sap_libs.sap_hostctrl_exec:
    function: ListInstances
  become: true

- name: ListInstances using local Unix socket as SAP admin user and selector parameters
  community.sap_libs.sap_hostctrl_exec:
    function: ListInstances
    parameters:
      aSelector:
        aInstanceStatus: S-INSTALLED # S-INSTALLED | S_RUNNING | S-STOPPED | S-LAST
  become: true
  become_user: "{{ sap_sid | lower }}adm"

- name: StartInstance with authentication
  community.sap_libs.sap_hostctrl_exec:
    hostname: 192.168.8.15
    username: tstadm
    password: test1234
    function: StartInstance
    parameters:
      aInstance:
        mSid: 'TST'
        mSystemNumber: '01'
      aOptions:
        mTimeout: -1 # -1=synchronous, 0=async, >0=wait timeout in seconds
        mSoftTimeout: 0
        mOptions:
          - O-INSTANCE

- name: Synchronous StartDatabase using local Unix socket with arguments
  community.sap_libs.sap_hostctrl_exec:
    function: StartDatabase
    parameters:
      aArguments:
        item: "{{ dict_arguments | dict2items(key_name='mKey', value_name='mValue') }}"
      aOptions:
        mTimeout: -1
  vars:
    dict_arguments:
      Database/Name: SYSTEMDB@XDH
      Database/Type: hdb # hdb|ora|mss|db6|ada|sap|syb|ase|db2|max
      # Database/InstanceName: HDB00 # the following parameters are optional
      # Database/Host: mydbhost.example.com
      # Database/Username: SYSTEM
      # Database/Password: StarWarsFTW123!
  become: true

- name: Example of GetDatabaseStatus
  community.sap_libs.sap_hostctrl_exec:
    function: GetDatabaseStatus
    parameters:
      aArguments:
        item: "{{ dict_arguments | dict2items(key_name='mKey', value_name='mValue') }}"
  vars:
    dict_arguments:
      Database/Name: XDH
      Database/Type: hdb
  become: true

# Example from https://help.sap.com/docs/host-agent/saphostcontrol-web-service-interface/executeoperation
- name: Asynchronous ExecuteOperation
  community.sap_libs.sap_hostctrl_exec:
    function: ExecuteOperation
    parameters:
      aOperation: "sayhello"
      aArguments:
        item:
          mKey: "MY_NAME"
          mValue: "Sally"
  register: operation_say_hello
  become: true

- name: Check results of previous ExecuteOperation
  community.sap_libs.sap_hostctrl_exec:
    function: GetOperationResults
    parameters:
      aOperationID: "{{ operation_say_hello.out[0].mOperationID }}"
      aOptions:
        mTimeout: -1
  become: true

# Output of GetOperationResults for the above ExecuteOperation :
#
# changed: true
# error: ""
# msg: Succesful execution of: GetOperationResults
# out:
#   - mOperationID: "42010A3F050B1FD0B5A26EF66B9FA7B7"
#     mOperationResults:
#       item:
#         - mMessageKey: description
#           mMessageValue: Say hello
#         - mMessageKey: null
#           mMessageValue: "\"hello Sally\""
#         - mMessageKey: exitcode
#           mMessageValue: 0
"""

RETURN = r'''
msg:
    description: Success-message with functionname.
    type: str
    returned: always
    sample: 'Succesful execution of: ListInstances'
out:
    description: The full output of the required function.
    type: list
    elements: dict
    returned: always
    sample: [{
            "item": [
                {
                    "mHostname": "test-vm-001",
                    "mSapVersionInfo": "793, patch 200, commit ec1833e294d84a70c04c6a1b01fd1a493f5c72fb",
                    "mSid": "TST",
                    "mSystemNumber": "01"
                },
                {
                    "mHostname": "test-vm-001",
                    "mSapVersionInfo": "793, patch 200, commit ec1833e294d84a70c04c6a1b01fd1a493f5c72fb",
                    "mSid": "TST",
                    "mSystemNumber": "00"
                }]
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
    retlist = ["ACOSPrepare", "AttachDatabase", "CallServiceOperation", "CancelOperation", "ConfigureOutsideDiscovery",
               "ConfigureOutsideDiscoveryDestination", "ConfigureOutsideDiscoveryPath", "DeployConfiguration", "DeployManagedObjectsFromSAR",
               "DetachDatabase", "DetectManagedObjects", "ExecuteDatabaseOperation", "ExecuteInstallationProcedure", "ExecuteOperation",
               "ExecuteOutsideDiscovery", "ExecuteUpgradeProcedure", "FinalizeDatabaseCopy", "GetCIMObject", "GetComputerSystem",
               "GetDatabaseProperties", "GetDatabaseStatus", "GetDatabaseSystemStatus", "GetIpAddressProperties", "GetOperationResults",
               "ListDatabases", "ListDatabaseSystems", "ListInstances", "LiveDatabaseUpdate", "PrepareDatabaseCopy", "RegisterInstanceService",
               "SetDatabaseProperty", "StartDatabase", "StartInstance", "StopDatabase", "StopInstance", "UnregisterInstanceService"]
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


def connection(hostname, port, username, password, function, parameters, use_local=False):
    if use_local:
        # Use Unix domain socket for local connection
        unix_socket = "/tmp/.sapstream1128"

        # Check if socket exists
        if not os.path.exists(unix_socket):
            raise Exception("SAP control Unix socket not found: {0}".format(unix_socket))

        url = "http://localhost/SAPHostControl/?wsdl"

        try:
            localsocket = LocalSocketHttpAuthenticated(unix_socket)
            client = Client(url, transport=localsocket)
        except Exception as e:
            raise Exception("Failed to connect via Unix socket: {0}".format(str(e)))
    else:
        # Use HTTP connection (original behavior)
        url = 'http://{0}:{1}/SAPHostControl/?wsdl'.format(hostname, port)
        client = Client(url, username=username, password=password)

    _function = getattr(client.service, function)
    if parameters is not None:
        result = _function(**parameters)
    else:
        result = _function()

    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            port=dict(type='int', required=False),
            username=dict(type='str', required=False),
            password=dict(type='str', no_log=True, required=False),
            hostname=dict(type='str', default="localhost"),
            function=dict(type='str', required=True, choices=choices()),
            parameters=dict(type='dict', required=False),
            force=dict(type='bool', default=False),
        ),
        supports_check_mode=False,
    )
    result = dict(changed=False, msg='', out={}, error='')
    params = module.params

    port = params['port']
    username = params['username']
    password = params['password']
    hostname = params['hostname']
    function = params['function']
    parameters = params['parameters']
    force = params['force']

    if not HAS_SUDS_LIBRARY:
        module.fail_json(
            msg=missing_required_lib('suds'),
            exception=SUDS_LIBRARY_IMPORT_ERROR)

    # Validate arguments
    if function == "StopDatabase" or function == "StopInstance":
        if force is False:
            module.fail_json(msg="Stop function requires force: True")

    # Determine if we should use local Unix socket connection
    # Use local if hostname is localhost and no username/password provided
    use_local = (hostname == "localhost" and
                 username is None and
                 password is None)

    if port is None:
        try:
            if use_local:
                # Try local connection first
                conn = connection(hostname, None, username, password, function, parameters, use_local=True)
            else:
                # Try HTTP ports
                try:
                    conn = connection(hostname, "1129", username, password, function, parameters)
                except Exception:
                    conn = connection(hostname, "1128", username, password, function, parameters)
        except Exception as err:
            result['error'] = str(err)
    else:
        try:
            conn = connection(hostname, port, username, password, function, parameters, use_local=False)
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
