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

import sys
from unittest.mock import patch, MagicMock, Mock
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()

from ansible_collections.community.sap_libs.plugins.modules import sap_snote


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_snote

    def tearDown(self):
        super(TestSAPRfcModule, self).tearDown()

    def define_rfc_connect(self, mocker):
        return mocker.patch(self.module.call_rfc_method)

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_error_module_not_found(self):
        """tests fail module error"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.HAS_PYRFC_LIBRARY = False
            self.module.ANOTHER_LIBRARY_IMPORT_ERROR = 'Module not found'
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['exception'], 'Module not found')

    def test_error_connection(self):
        """tests fail module error"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.Connection.side_effect = Mock(side_effect=Exception('Test'))
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Something went wrong connecting to the SAP system.')

    def test_error_wrong_path(self):
        """tests fail wrong path extension"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456_00.tx"
        }

        with self.assertRaises(AnsibleFailJson) as result:
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'The path must include the extracted snote file and ends with txt.')

    def test_error_wrong_user(self):
        """tests fail wrong path extension"""

        args = {
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456_00.tx"
        }

        with self.assertRaises(AnsibleFailJson) as result:
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'User C(DDIC) or C(SAP*) not allowed for this operation.')

    def test_success_absent(self):
        """test absent execute snote"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "absent",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        }
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [True, False]
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" deimplemented.')

    def test_success_absent_snot_only(self):
        """test absent execute snote"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "absent",
            "snote": "000123456"
        }
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [True, False]
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" deimplemented.')

    def test_nothing_to_do(self):
        """test nothing to do"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "present",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        }
        with patch.object(self.module, 'check_implementation') as check:
            check.return_value = True
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Nothing to do.')

    def test_success_present_with_copy(self):
        """test present execute snote"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "present",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        }
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [False, True]
                    with patch.object(self.module, 'call_rfc_method') as callrfc:
                        callrfc.side_effect = [{'EV_RC': 0}, {'EV_RC': 0}, {'ET_MANUAL_ACTIVITIES': ''}]
                        with set_module_args(args):
                            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" implemented.')

    def test_success_present_implement_only(self):
        """test present implement snote"""

        args = {
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "present",
            "snote": "000123456"
        }
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [False, True]
                    with patch.object(self.module, 'call_rfc_method') as callrfc:
                        callrfc.side_effect = [{'EV_RC': 0}, {'ET_MANUAL_ACTIVITIES': ''}]
                        with set_module_args(args):
                            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" implemented.')
