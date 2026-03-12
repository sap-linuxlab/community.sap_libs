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
        """Fail when required parameters are missing."""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_error_module_not_found(self):
        """Fail when SUDS library is not found during import."""

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

    @patch('ansible_collections.community.sap_libs.plugins.module_utils.sapstartsrv_client.Client')
    def test_error_connection(self, mock_client):
        """Fail when there is a connection error."""

        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "GetProcessList"
        }
        with self.assertRaises(AnsibleFailJson) as result:
            mock_client.side_effect = Mock(side_effect=Exception('Test'))
            with set_module_args(args):
                self.module.main()
        error_msg = result.exception.args[0]['msg']
        self.assertEqual(error_msg, 'Function execution has failed. See error for more details.')

    def test_error_port_sysnr(self):
        """Fail when both sysnr and port are provided."""

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
        """Fail when force parameter is missing."""

        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "Stop"
        }

        with self.assertRaises(AnsibleFailJson) as result:
            with set_module_args(args):
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], "Function 'Stop' requires force: True")

    def test_success_sysnr(self):
        """Test successful connection with sysnr."""

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
        """Test successful connection with port."""

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
        """Test successful connection with sysnr."""

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

    def test_success_already_started(self):
        """Test successful connection when an instance is already running."""
        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "Start"
        }
        error_text = "Server raised fault: 'Instance already started'"

        with patch.object(self.module, 'connection') as mock_connection:
            mock_connection.side_effect = Exception(error_text)

            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    self.module.main()

        res = result.exception.args[0]
        self.assertFalse(res['changed'])
        self.assertEqual(res['out'], [None])
        self.assertIn("already started", res['msg'])

    def test_success_complex_parameter(self):
        """Test passing a dictionary as a parameter (e.g. InstanceStart)."""
        args = {
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "InstanceStart",
            "parameter": {
                "host": "s4hana",
                "nr": 0
            }
        }

        with patch.object(self.module, 'connection') as mock_connection:
            mock_connection.return_value = None

            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    self.module.main()

        res = result.exception.args[0]
        self.assertTrue(res['changed'])
        self.assertEqual(res['out'], [None])
        self.assertEqual(res['msg'], "Successful execution of function: InstanceStart")
