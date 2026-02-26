#!/usr/bin/python

# Copyright: (c) 2022, Rainer Leber rainerleber@gmail.com>
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
module: sap_system_facts

short_description: Gathers SAP facts in a host

version_added: "1.0.0"

description:
    - This facts module gathers SAP system facts about the running instance.

author:
    - Rainer Leber (@rainerleber)

notes:
    - Supports C(check_mode).
    - The user executing the module must have execute permissions for C(/usr/sap/hostctrl/exe/sapcontrol).
    - Only directories matching SAP SID and Instance naming conventions are scanned.
'''

EXAMPLES = r'''
- name: Return SAP system ansible_facts
  community.sap_libs.sap_system_facts:
'''

RETURN = r'''
# These are examples of possible return values,
# and in general should use other names for return values.
ansible_facts:
  description: Facts about the running SAP systems.
  returned: always
  type: dict
  contains:
    sap:
      description: Facts about the running SAP systems.
      type: list
      elements: dict
      returned: When SAP system fact is present
      sample: [
        {
            "InstanceType": "NW",
            "NR": "00",
            "SID": "ABC",
            "TYPE": "ASCS"
        },
        {
            "InstanceType": "NW",
            "NR": "01",
            "SID": "ABC",
            "TYPE": "PAS"
        },
        {
            "InstanceType": "HANA",
            "NR": "02",
            "SID": "HDB",
            "TYPE": "HDB"
        },
        {
            "InstanceType": "NW",
            "NR": "80",
            "SID": "WEB",
            "TYPE": "WebDisp"
        }
      ]
'''

from ansible.module_utils.basic import AnsibleModule
import os
import re


def get_all_hana_sid():
    hana_sid = list()

    # Expected SID pattern: 3 character in specific pattern (e.g., ABC, D01, etc.)
    sid_pattern = re.compile(r'^[A-Z][A-Z0-9][A-Z0-9]$')

    shared_path = "/hana/shared"
    
    if is_accessible_dir(shared_path):
        try:
            for sid in os.listdir(shared_path):
                if not sid_pattern.match(sid):
                    continue
                
                target_path = os.path.join("/usr/sap", sid)
                
                try:
                    if is_accessible_dir(target_path):
                        hana_sid.append(sid)
                except OSError:
                    # Individual SID folder is problematic, move to next
                    continue

        except OSError:
            # Entire shared_path is inaccessible
            pass

    return hana_sid


def get_all_nw_sid():
    nw_sid = list()

    # Expected SID pattern with only 3 character in specific pattern (e.g., ABC, D01, etc.)
    sid_pattern = re.compile(r'^[A-Z][A-Z0-9][A-Z0-9]$')

    sapmnt_path = "/sapmnt"
    
    if is_accessible_dir(sapmnt_path):
        try:
            for sid in os.listdir(sapmnt_path):
                if not sid_pattern.match(sid):
                    continue

                target_path = os.path.join("/usr/sap", sid)

                try:
                    if is_accessible_dir(target_path):
                        nw_sid.append(sid)
                    else:
                        # Check to see if /sapmnt/SID/sap_bobj exists and is accessible
                        bobj_path = os.path.join(sapmnt_path, sid, "sap_bobj")
                        if is_accessible_dir(bobj_path):
                            nw_sid.append(sid)
                except OSError:
                    # Individual SID folder is problematic, move to next
                    continue

        except OSError:
            # Entire shared_path is inaccessible
            pass

    return nw_sid


def get_hana_nr(sids, module):
    hana_list = list()

    # Expected Instance pattern: HDB followed by exactly 2 digits (e.g., HDB00, HDB01, etc.)
    instance_pattern = re.compile(r'^HDB(\d{2})$')

    sapcontrol_path = module.get_bin_path('/usr/sap/hostctrl/exe/sapcontrol', required=True)

    for sid in sids:
        path = os.path.join('/usr/sap', sid)

        if not is_accessible_dir(path):
            continue

        for instance in os.listdir(path):
            match = instance_pattern.match(instance)
            if match:
                # 'match.group(1)' is the 2 digits captured by (\d{2})
                instance_nr = match.group(1)

                command = [sapcontrol_path]
                command.extend(['-nr', instance_nr, '-function', 'GetProcessList'])

                check_instance = module.run_command(command, check_rc=False)

                # sapcontrol returns (0-5) exit codes; (1) usually means unavailable
                if check_instance[0] != 1:
                    hana_list.append({
                        'NR': instance_nr, 
                        'SID': sid, 
                        'TYPE': 'HDB', 
                        'InstanceType': 'HANA'
                    })
                else:
                    continue

    return hana_list


def get_nw_nr(sids, module):
    nw_list = list()

    # Expected Instance pattern: letters followed by exactly 2 digits (e.g., ASCS00, D01)
    # Excludes 'SYS', 'exe', 'hdbclient', etc.
    instance_pattern = re.compile(r'^[a-zA-Z]+(\d{2})$')

    sapcontrol_path = module.get_bin_path('/usr/sap/hostctrl/exe/sapcontrol', required=True)
    type = ""

    for sid in sids:
        path = os.path.join('/usr/sap', sid)

        if not is_accessible_dir(path):
            continue

        for instance in os.listdir(path):
            match = instance_pattern.match(instance)
            if match:
                # 'match.group(1)' is the 2 digits captured by (\d{2})
                instance_nr = match.group(1)

                command = [sapcontrol_path]
                command.extend(['-nr', instance_nr, '-function', 'GetInstanceProperties'])

                check_instance = module.run_command(command, check_rc=False)
                if check_instance[0] != 1:
                    for line in check_instance[1].splitlines():
                        if re.search('INSTANCE_NAME', line):
                            # convert to list and extract last
                            type_raw = (line.strip('][').split(', '))[-1]
                            # split instance number
                            type = type_raw[:-2]
                            nw_list.append({'NR': instance_nr, 'SID': sid, 'TYPE': get_instance_type(type), 'InstanceType': 'NW'})
                    else:
                        continue

    return nw_list


def get_instance_type(raw_type):
    if raw_type[0] == "D":
        # It's a PAS
        type = "PAS"
    elif raw_type[0] == "A":
        # It's an ASCS
        type = "ASCS"
    elif raw_type[0] == "W":
        # It's a Webdisp
        type = "WebDisp"
    elif raw_type[0] == "J":
        # It's a Java
        type = "Java"
    elif raw_type[0] == "S":
        # It's an SCS
        type = "SCS"
    elif raw_type[0] == "E":
        # It's an ERS
        type = "ERS"
    else:
        # Unknown instance type
        type = "XXX"
    return type


def is_accessible_dir(path):
    return os.path.isdir(path) and os.access(path, os.R_OK)


def run_module():
    module_args = dict()
    system_result = list()

    result = dict(
        changed=False,
        ansible_facts=dict(),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # Fail if execution user does not have permission for sapcontrol
    sapcontrol_path = module.get_bin_path('/usr/sap/hostctrl/exe/sapcontrol', required=True)
    if not os.access(sapcontrol_path, os.X_OK):
        module.fail_json(msg=f"Permission denied: Ansible user cannot execute {sapcontrol_path}")

    hana_sid = get_all_hana_sid()
    if hana_sid:
        system_result = system_result + get_hana_nr(hana_sid, module)

    nw_sid = get_all_nw_sid()
    if nw_sid:
        system_result = system_result + get_nw_nr(nw_sid, module)


    if system_result:
        result['ansible_facts'] = {'sap': system_result}
        result['msg'] = "SAP System facts were collected."
    else:
        result['ansible_facts'] 
        result['msg'] = "No running SAP instances found or Ansible user cannot access them."

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
