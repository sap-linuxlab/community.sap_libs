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

sys.modules['suds.client'] = MagicMock()
sys.modules['suds.sudsobject'] = MagicMock()
sys.modules['suds'] = MagicMock()

from ansible_collections.community.sap_libs.plugins.modules import sap_hostctrl_exec


class TestSapcontrolModule(ModuleTestCase):

    def setUp(self):
        super(TestSapcontrolModule, self).setUp()
        self.module = sap_hostctrl_exec
        # Patch HAS_SUDS_LIBRARY for all tests
        self.patcher_suds = patch.object(self.module, 'HAS_SUDS_LIBRARY', True)
        self.patcher_suds.start()

    def tearDown(self):
        self.patcher_suds.stop()
        super(TestSapcontrolModule, self).tearDown()

    def define_rfc_connect(self, mocker):
        return mocker.patch(self.module.call_rfc_method)

    def test_without_required_parameters(self):
        """Fail when required parameters are missing."""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_error_module_not_found(self):
        """Fail when SUDS library is not found during import."""

        args = {
            "hostname": "192.168.8.15",
            "function": "ListInstances"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.HAS_SUDS_LIBRARY = False
            self.module.SUDS_LIBRARY_IMPORT_ERROR = 'Module not found'
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['exception'], 'Module not found')

    @patch('ansible_collections.community.sap_libs.plugins.module_utils.sapstartsrv_client.Client')
    def test_error_connection(self, mock_client):
        """Fail when there is a connection error."""

        args = {
            "hostname": "192.168.8.15",
            "function": "ListInstances"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            mock_client.side_effect = Mock(side_effect=Exception('Test'))
            with set_module_args(args):
                self.module.main()
        error_msg = result.exception.args[0]['msg']
        self.assertEqual(error_msg, 'Function execution has failed. See error for more details.')

    def test_error_missing_force(self):
        """Fail when force parameter is missing."""

        args = {
            "hostname": "192.168.8.15",
            "function": "StopInstance"
        }

        with self.assertRaises(AnsibleFailJson) as result:
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], "Function 'StopInstance' requires force: True")

    def test_success_list_instances(self):
        """Test successful execution of ListInstances."""

        args = {
            "hostname": "192.168.8.15",
            "function": "ListInstances"
        }
        ret_dict = {'item': [{'mHostname': 'test-vm-001',
                              'mSapVersionInfo': '793, patch 200, commit ec1833e294d84a70c04c6a1b01fd1a493f5c72fb',
                              'mSid': 'TST',
                              'mSystemNumber': '00'}]}
        with patch.object(self.module, 'connection') as mock_connection:
            with patch.object(self.module, 'recursive_dict') as ret:
                ret.return_value = ret_dict
                mock_connection.return_value = ret_dict
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [ret_dict])

    def test_success_port(self):
        """Test successful execution with port."""

        args = {
            "hostname": "192.168.8.15",
            "port": 1128,
            "function": "ListInstances"
        }
        ret_dict = {'item': [{'mHostname': 'test-vm-001',
                              'mSapVersionInfo': '793, patch 200, commit ec1833e294d84a70c04c6a1b01fd1a493f5c72fb',
                              'mSid': 'TST',
                              'mSystemNumber': '00'}]}
        with patch.object(self.module, 'connection') as mock_connection:
            with patch.object(self.module, 'recursive_dict') as ret:
                ret.return_value = ret_dict
                mock_connection.return_value = ret_dict
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [ret_dict])

    def test_success_local(self):
        """Test successful execution with local port."""

        args = {
            "function": "ListInstances"
        }
        ret_dict = {'item': [{'mHostname': 'test-vm-001',
                              'mSapVersionInfo': '793, patch 200, commit ec1833e294d84a70c04c6a1b01fd1a493f5c72fb',
                              'mSid': 'TST',
                              'mSystemNumber': '00'}]}
        with patch.object(self.module, 'connection') as mock_connection:
            with patch.object(self.module, 'recursive_dict') as ret:
                ret.return_value = ret_dict
                mock_connection.return_value = ret_dict
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [ret_dict])

    def test_success_parameters(self):
        """Test successful execution with parameters."""

        args = {
            "hostname": "192.168.8.15",
            "function": "StartInstance",
            "parameters": {
                "aInstance": {"mSid": "TST", "mSystemNumber": '00'},
                "aOptions": {"mTimeout": -1, "mSoftTimeout": 0, "mOptions": ["O-INSTANCE"]}
            }
        }
        ret_dict = {"mOperationID": "42010A3F050C1FD0B3D4D6F5E5D41924",
                    "mOperationResults": {"item": [
                        {"mMessageKey": "LogMsg/TimeStamp", "mMessageValue": "null"},
                        {"mMessageKey": "LogMsg/Severity", "mMessageValue": "Info"},
                        {"mMessageKey": "LogMsg/Source", "mMessageValue": "saphostcontrol"},
                        {"mMessageKey": "LogMsg/Text", "mMessageValue": "exitcode=0"},
                        {"mMessageKey": "LogMsg/TimeStamp", "mMessageValue": "null"},
                        {"mMessageKey": "LogMsg/Severity", "mMessageValue": "Info"},
                        {"mMessageKey": "LogMsg/Source", "mMessageValue": "saphostcontrol"},
                        {"mMessageKey": "LogMsg/Text", "mMessageValue": "'sapcontrol -function Start' successfully executed"},
                        {"mMessageKey": "LogMsg/TimeStamp", "mMessageValue": "null"},
                        {"mMessageKey": "LogMsg/Severity", "mMessageValue": "Info"},
                        {"mMessageKey": "LogMsg/Source", "mMessageValue": "saphostcontrol"},
                        {"mMessageKey": "LogMsg/Text", "mMessageValue": "exitcode=0"},
                        {"mMessageKey": "LogMsg/TimeStamp", "mMessageValue": "null"},
                        {"mMessageKey": "LogMsg/Severity", "mMessageValue": "Info"},
                        {"mMessageKey": "LogMsg/Source", "mMessageValue": "saphostcontrol"},
                        {"mMessageKey": "LogMsg/Text", "mMessageValue": "'sapcontrol -function StartWait' successfully executed"}]}}
        with patch.object(self.module, 'connection') as mock_connection:
            with patch.object(self.module, 'recursive_dict') as ret:
                ret.return_value = ret_dict
                mock_connection.return_value = ret_dict
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [ret_dict])
