# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from unittest.mock import patch, MagicMock, Mock
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['suds.client'] = MagicMock()
sys.modules['suds.sudsobject'] = MagicMock()
sys.modules['suds'] = MagicMock()

from ansible_collections.community.sap_libs.plugins.modules import sap_control_exec


class TestSapcontrolModule(ModuleTestCase):

    def setUp(self):
        super(TestSapcontrolModule, self).setUp()
        self.module = sap_control_exec
        # Patch HAS_SUDS_LIBRARY for all tests
        self.patcher_suds = patch.object(self.module, 'HAS_SUDS_LIBRARY', True)
        self.patcher_suds.start()

    def tearDown(self):
        self.patcher_suds.stop()
        super(TestSapcontrolModule, self).tearDown()

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
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "GetProcessList"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.HAS_SUDS_LIBRARY = False
            self.module.SUDS_LIBRARY_IMPORT_ERROR = 'Module not found'
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['exception'], 'Module not found')

    def test_error_connection(self):
        """tests fail module exception"""

        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "GetProcessList"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.Client.side_effect = Mock(side_effect=Exception('Test'))
            with set_module_args(args):
                self.module.main()
        error_msg = result.exception.args[0]['msg']
        expected_messages = [
            'Something went wrong connecting to the SOAP API.',
            'Something went wrong connecting to the Unix socket.'
        ]
        self.assertIn(error_msg, expected_messages)

    def test_error_port_sysnr(self):
        """tests fail multi provide parameters"""

        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "port": "50113",
            "function": "GetProcessList"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'parameters are mutually exclusive: sysnr|port')

    def test_error_missing_force(self):
        """tests fail missing force"""

        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "Stop"
        }

        with self.assertRaises(AnsibleFailJson) as result:
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Stop function requires force: True')

    def test_success_sysnr(self):
        """test success with sysnr"""

        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "GetProcessList"
        }
        with patch.object(self.module, 'connection') as mock_connection:
            mock_connection.return_value = {'item': [{'name': 'hdbdaemon', 'value': '1'}]}
            with patch.object(self.module, 'recursive_dict') as ret:
                ret.return_value = {'item': [{'name': 'hdbdaemon', 'value': '1'}]}
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [{'item': [{'name': 'hdbdaemon', 'value': '1'}]}])

    def test_success_port(self):
        """test success with port"""

        args = {
            "hostname": "192.168.8.15",
            "port": 50113,
            "function": "GetProcessList"
        }
        with patch.object(self.module, 'connection') as mock_connection:
            mock_connection.return_value = {'item': [{'name': 'hdbdaemon', 'value': '1'}]}
            with patch.object(self.module, 'recursive_dict') as ret:
                ret.return_value = {'item': [{'name': 'hdbdaemon', 'value': '1'}]}
                with self.assertRaises(AnsibleExitJson) as result:
                    with set_module_args(args):
                        self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [{'item': [{'name': 'hdbdaemon', 'value': '1'}]}])

    def test_success_string(self):
        """test success with sysnr"""

        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "ParameterValue",
            "parameter": "ztta/short_area"
        }
        with patch.object(self.module, 'connection') as ret:
            ret.return_value = '1600000'
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    self.module.main()
        self.assertEqual(result.exception.args[0]['out'], ['1600000'])
