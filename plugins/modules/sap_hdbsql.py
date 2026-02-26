#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber <rainerleber@gmail.com>
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
module: sap_hdbsql
short_description: Ansible Module to execute SQL on SAP HANA
version_added: "1.0.0"
description: This module executes SQL statements on HANA with hdbsql.
options:
    sid:
        description: The system ID.
        type: str
        required: false
    bin_path:
        description: The path to the hdbsql binary.
        type: str
        required: false
    instance:
        description: The instance number.
        type: str
        required: true
    user:
        description: A dedicated username. The user could be also in hdbuserstore.
        type: str
        default: SYSTEM
    userstore:
        description: If C(true), the user must be in hdbuserstore.
        type: bool
        default: false
    password:
        description:
          - The password to connect to the database.
          - "B(Note:) Since the passwords have to be passed as command line arguments, I(userstore=true) should
            be used whenever possible, as command line arguments can be seen by other users
            on the same machine."
        type: str
    autocommit:
        description: Autocommit the statement.
        type: bool
        default: true
    host:
        description: The Host IP address. The port can be defined as well.
        type: str
    database:
        description: Define the database on which to connect.
        type: str
    encrypted:
        description: Use encrypted connection.
        type: bool
        default: false
    filepath:
        description:
        - One or more files each containing one SQL query to run.
        - Must be a string or list containing strings.
        type: list
        elements: path
    query:
        description:
        - SQL query to run.
        - Must be a string or list containing strings. Please note that if you supply a string, it will be split by commas (C(,)) to a list.
          It is better to supply a one-element list instead to avoid mangled input.
        type: list
        elements: str
notes:
    - Does not support C(check_mode). Always reports that the state has changed even if no changes have been made.  
    - Logic for C(changed): If C(filepath) is used, C(changed) is always true. If C(query) is used, 
      C(changed) is true only if at least one query is not a C(SELECT) statement.
    - B(Environment Note:) Avoid using login shell flags (like V(become_flags: "-i") or V(become_flags: "-")) 
      when V(become_user) is a SAP admin user. These flags load SAP-specific environment variables that 
      can corrupt the Python path, leading to V(ModuleNotFoundError). 
    - If you must use a login shell, ensure you reset the environment in your task with 
      V(environment: { PYTHONPATH: "", LD_LIBRARY_PATH: "" }).
author:
    - Rainer Leber (@rainerleber)
'''

EXAMPLES = r'''
- name: Simple select query
  community.sap_libs.sap_hdbsql:
    sid: "hdb"
    instance: "01"
    password: "Test123"
    query: select user_name from users

- name: RUN select query with host port
  community.sap_libs.sap_hdbsql:
    sid: "hdb"
    instance: "01"
    password: "Test123"
    host: "10.10.2.4:30001"
    query: select user_name from users

- name: Run several queries
  community.sap_libs.sap_hdbsql:
    sid: "hdb"
    instance: "01"
    password: "Test123"
    query:
    - select user_name from users
    - select * from SYSTEM
    host: "localhost"
    autocommit: False

- name: Run several queries with path
  community.sap_libs.sap_hdbsql:
    bin_path: "/usr/sap/HDB/HDB01/exe/hdbsql"
    instance: "01"
    password: "Test123"
    query:
    - select user_name from users
    - select * from users
    host: "localhost"
    autocommit: False

- name: Run several queries from file
  community.sap_libs.sap_hdbsql:
    sid: "hdb"
    instance: "01"
    password: "Test123"
    filepath:
    - /tmp/HANA_CPU_UtilizationPerCore_2.00.020+.txt
    - /tmp/HANA.txt
    host: "localhost"

- name: Run several queries from user store
  community.sap_libs.sap_hdbsql:
    sid: "hdb"
    instance: "01"
    user: hdbstoreuser
    userstore: true
    query:
    - select user_name from users
    - select * from users
    autocommit: False
'''

RETURN = r'''
query_result:
    description: List containing results of all queries executed (one sublist for every query).
    returned: on success
    type: list
    elements: list
    sample: [[{"Column": "Value1"}, {"Column": "Value2"}], [{"Column": "Value1"}, {"Column": "Value2"}]]
'''

import csv
from ansible.module_utils.basic import AnsibleModule
from io import StringIO
from ansible.module_utils.common.text.converters import to_native


def csv_to_list(raw_csv):
    if not raw_csv.strip():
        return []

    reader_raw = csv.DictReader(StringIO(raw_csv))
    # Using to_native and strip to ensure clean dictionary keys/values
    reader = [dict((to_native(k), to_native(v).strip()) for k, v in row.items()) for row in reader_raw]
    return list(reader)

def run_hdb_command(module, full_cmd):
    rc, out_raw, err = module.run_command(full_cmd)

    if rc != 0:
        err_msg = to_native(err).lower()

        if "authentication failed" in err_msg or "invalid username or password" in err_msg:
            module.fail_json(msg="SAP HANA Authentication Failed. Please check credentials/userstore.", rc=rc, stderr=err)

        elif "insufficient privilege" in err_msg or "258:" in err_msg:
            module.fail_json(msg="SAP HANA Authorization Error: The user has insufficient privileges to perform this action.", rc=rc, stderr=err)

        elif "connect failed" in err_msg:
            module.fail_json(msg="SAP HANA Connection Failed. Check host, instance, and port.", rc=rc, stderr=err)

        else:
            module.fail_json(msg="SQL Execution Error", rc=rc, stderr=err, cmd=full_cmd)

    return out_raw

def main():
    module = AnsibleModule(
        argument_spec=dict(
            sid=dict(type='str', required=False),
            bin_path=dict(type='str', required=False),
            instance=dict(type='str', required=True),
            encrypted=dict(type='bool', default=False),
            host=dict(type='str', required=False),
            user=dict(type='str', default="SYSTEM"),
            userstore=dict(type='bool', default=False),
            password=dict(type='str', no_log=True),
            database=dict(type='str', required=False),
            query=dict(type='list', elements='str', required=False),
            filepath=dict(type='list', elements='path', required=False),
            autocommit=dict(type='bool', default=True),
        ),
        required_one_of=[('query', 'filepath')],
        required_if=[('userstore', False, ['password'])],
        supports_check_mode=False,
    )

    params = module.params
    output = []
    has_changed = False

    # Determine if module will show as changed.
    # If filepaths are provided, we assume changes will be made, as files typically contain DDL or DML statements.
    # If only queries are provided, we check if any of them are not SELECT statements. If at least one is not a SELECT, we assume changes will be made.
    if params['filepath']:
        has_changed = True

    elif params['query']:
        for q in params['query']:
            # Strip whitespace and check if it starts with SELECT
            if not q.strip().upper().startswith("SELECT"):
                has_changed = True
                break

    # Construct Binary Path
    bin_path = params['bin_path']
    if bin_path is None:
        if not params['sid']:
            module.fail_json(msg="Parameter 'sid' is required to determine default bin_path if 'bin_path' is not provided.")

        bin_path = "/usr/sap/{sid}/HDB{instance}/exe/hdbsql".format(
            sid=params['sid'].upper(), 
            instance=params['instance']
        )

    try:
        command = [module.get_bin_path(bin_path, required=True)]
    except Exception as e:
        module.fail_json(msg='Executable binary hdbsql not found at {0}: {1}'.format(bin_path, to_native(e)))

    # Build Base Command
    if params['encrypted']:
        # -e: Enforce encryption (don't fall back)
        # -ssltrustcert: Trust the server certificate
        # -sslcreatecert: Create a local certificate if necessary
        command.extend(['-e', '-ssltrustcert', '-sslcreatecert'])

    if not params['autocommit']:
        command.extend(['-z'])

    if params['host']:
        command.extend(['-n', params['host']])

    if params['database']:
        command.extend(['-d', params['database']])

    if params['userstore']:
        command.extend(['-x', '-U', params['user']])

    else:
        command.extend(['-x', '-i', params['instance'], '-u', params['user'], '-p', params['password']])

    # Process Queries
    if params['query']:
        for q in params['query']:
            query_command = command + [q]
            out_raw = run_hdb_command(module, query_command)
            try:
                output.append(csv_to_list(out_raw))
            except Exception as e:
                module.fail_json(msg="Failed to parse CSV output: {0}".format(to_native(e)))

    # Process Files
    # Note: File processing adds extra arguments so it has to execute after query processing.
    if params['filepath']:
        for p in params['filepath']:
            file_query_command = command + ['-E', '3', '-I', p]
            out_raw = run_hdb_command(module, file_query_command)
            try:
                output.append(csv_to_list(out_raw))
            except Exception as e:
                module.fail_json(msg="Failed to parse output from file {0}: {1}".format(p, to_native(e)))

    module.exit_json(changed=has_changed, query_result=output)

if __name__ == '__main__':
    main()
