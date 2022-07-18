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

import sys
from ansible_collections.community.sap_libs.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()
from ansible_collections.community.sap_libs.plugins.modules import sap_pyrfc


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_pyrfc

    def tearDown(self):
        super(TestSAPRfcModule, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_error_module_not_found(self):
        """tests fail module error"""

        set_module_args({
            "function": "STFC_CONNECTION",
            "parameters": {"REQUTEXT": "Hello SAP!"},
            "connection": {"ashost": "s4hana.poc.cloud",
                           "sysnr": "01",
                           "client": "400",
                           "user": "DDIC",
                           "passwd": "Password1",
                           "lang": "EN"}
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.HAS_PYRFC_LIBRARY = False
            self.module.PYRFC_LIBRARY_IMPORT_ERROR = 'Module not found'
            self.module.main()
        self.assertEqual(
            result.exception.args[0]['exception'], 'Module not found')

    def test_success_communication(self):
        """tests success"""
        set_module_args({
            "function": "STFC_CONNECTION",
            "parameters": {"REQUTEXT": "Hello SAP!"},
            "connection": {"ashost": "s4hana.poc.cloud",
                           "sysnr": "01",
                           "client": "400",
                           "user": "DDIC",
                           "passwd": "Password1",
                           "lang": "EN"}
        })
        with patch.object(self.module, 'get_connection') as patch_call:
            patch_call.call.return_value = 'Patched'
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
        self.assertEqual(result.exception.args[0]['changed'], True)
