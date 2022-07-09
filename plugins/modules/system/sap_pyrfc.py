#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Sean Freeman ,
#                      Rainer Leber <rainerleber@gmail.com> <rainer.leber@sva.de>
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sap_pyrfc

short_description: This module executes rfc functions.

version_added: "1.2.0"

description:
    - This module will executes rfc calls on a sap system.
    - It is a generic approach to call rfc functions on a SAP System.
    - This module should be used where no module or role is provided.

options:
    function:
        description: The SAP RFC function to call.
        required: true
        type: str
    parameters:
        description: The parameters which are needed by the function.
        required: true
        type: dict
    connection:
        description: The required connection details.
        required: true
        type: dict
        suboptions:
          ashost:
            description: The required host for the SAP system. Can be either an FQDN or IP Address.
            type: str
            required: true
          sysid:
            description: The systemid of the SAP system.
            type: str
            required: false
          sysnr:
            description:
            - The system number of the SAP system.
            - You must quote the value to ensure retaining the leading zeros.
            type: str
            required: true
          client:
            description:
            - The client number to connect to.
            - You must quote the value to ensure retaining the leading zeros.
            type: str
            required: true
          user:
            description: The required username for the SAP system.
            type: str
            required: true
          passwd:
            description: The required password for the SAP system.
            type: str
            required: true
          lang:
            description: The used language to execute.
            type: str
            required: false

requirements:
    - pyrfc >= 2.4.0

author:
    - Sean Freeman (@seanfreeman)
    - Rainer Leber (@rainerleber)
'''

EXAMPLES = '''
community.sap_libs.sap_pyrfc:
  function: STFC_CONNECTION
  parameters:
    REQUTEXT: "Hello SAP!"
  connection:
    ashost: s4hana.poc.cloud
    sysid: TDT
    sysnr: "01"
    client: "400"
    user: DDIC
    passwd: Password1
    lang: EN
'''

RETURN = r'''
result:
    description: The execution description.
    type: dict
    returned: always
    sample: {'...'}
'''

import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
try:
    from pyrfc import (ABAPApplicationError, ABAPRuntimeError, CommunicationError,
                       Connection, LogonError)
except ImportError:
    HAS_PYRFC_LIBRARY = False
    PYRFC_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_PYRFC_LIBRARY = True


def get_connection(module, conn_params):
    module.warn('Connecting ... %s' % conn_params['ashost'])
    if "saprouter" in conn_params:
        module.warn("...via SAPRouter to SAP System")
    elif "gwhost" in conn_params:
        module.warn("...via Gateway to SAP System")
    else:
        module.warn("...direct to SAP System")

    conn = Connection(**conn_params)

    module.warn("Verifying connection is open/alive: %s" % conn.alive)
    return conn


def main():
    params_spec = dict(
        ashost=dict(type='str', required=True),
        sysid=dict(type='str', required=False),
        sysnr=dict(type='str', required=True),
        client=dict(type='str', required=True),
        user=dict(type='str', required=True),
        passwd=dict(type='str', required=True, no_log=True),
        lang=dict(type='str', required=False),
    )

    argument_spec = dict(function=dict(required=True, type='str'),
                         parameters=dict(required=True, type='dict'),
                         connection=dict(
                             required=True, type='dict', options=params_spec),
                         )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    function = module.params.get('function')
    func_params = module.params.get('parameters')
    conn_params = module.params.get('connection')

    if not HAS_PYRFC_LIBRARY:
        module.fail_json(
            msg=missing_required_lib('pyrfc'),
            exception=PYRFC_LIBRARY_IMPORT_ERROR)

    # Check mode
    if module.check_mode:
        msg = "function: %s; params: %s; login: %s" % (
            function, func_params, conn_params)
        module.exit_json(msg=msg, changed=True)

    try:
        conn = get_connection(module, conn_params)
        result = conn.call(function, **func_params)
        module.exit_json(changed=True, result=result)
    except CommunicationError as e:
        msg = "Could not connect to server: %s" % e.message
        module.exit_json(failed=True, msg=msg)
    except LogonError as e:
        msg = "Could not log in: %s" % e.message
        module.exit_json(failed=True, msg=msg)
    except (ABAPApplicationError, ABAPRuntimeError) as e:
        msg = "ABAP error occurred: %s" % e.message
        module.exit_json(failed=True, msg=msg)

    module.exit_json(failed=False)


if __name__ == '__main__':
    main()
