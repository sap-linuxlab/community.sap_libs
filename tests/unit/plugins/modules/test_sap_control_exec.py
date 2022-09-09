# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.sap_libs.tests.unit.compat.mock import patch, MagicMock, Mock
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['suds.client'] = MagicMock()
sys.modules['suds.sudsobject'] = MagicMock()
sys.modules['suds'] = MagicMock()

from ansible_collections.community.sap_libs.plugins.modules import sap_control_exec


class TestSapcontrolModule(ModuleTestCase):

    def setUp(self):
        super(TestSapcontrolModule, self).setUp()
        self.module = sap_control_exec

    def tearDown(self):
        super(TestSapcontrolModule, self).tearDown()

    def define_rfc_connect(self, mocker):
        return mocker.patch(self.module.call_rfc_method)

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_error_module_not_found(self):
        """tests fail module error"""

        set_module_args({
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "GetProcessList"
        })
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.HAS_SUDS_LIBRARY = False
            self.module.SUDS_LIBRARY_IMPORT_ERROR = 'Module not found'
            self.module.main()
        self.assertEqual(result.exception.args[0]['exception'], 'Module not found')

    def test_error_connection(self):
        """tests fail module exception"""

        set_module_args({
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "GetProcessList"
        })
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.Client.side_effect = Mock(side_effect=Exception('Test'))
            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Something went wrong connecting to the SAPCONTROL SOAP API.')

    def test_error_port_sysnr(self):
        """tests fail multi provide parameters"""

        set_module_args({
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "port": "50113",
            "function": "GetProcessList"
        })
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'parameters are mutually exclusive: sysnr|port')

    def test_error_missing_force(self):
        """tests fail missing force"""

        set_module_args({
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "Stop"
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Stop function requires force: True')

    def test_success_sysnr(self):
        """test success with sysnr"""

        set_module_args({
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "GetProcessList"
        })
        with patch.object(self.module, 'recursive_dict') as ret:
            ret.return_value = {'item': [{'name': 'hdbdaemon', 'value': '1'}]}
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [{'item': [{'name': 'hdbdaemon', 'value': '1'}]}])

    def test_success_port(self):
        """test success with port"""

        set_module_args({
            "hostname": "192.168.8.15",
            "port": "50113",
            "function": "GetProcessList"
        })
        with patch.object(self.module, 'recursive_dict') as ret:
            ret.return_value = {'item': [{'name': 'hdbdaemon', 'value': '1'}]}
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
        self.assertEqual(result.exception.args[0]['out'], [{'item': [{'name': 'hdbdaemon', 'value': '1'}]}])

    def test_success_string(self):
        """test success with sysnr"""

        set_module_args({
            "hostname": "192.168.8.15",
            "sysnr": "01",
            "function": "ParameterValue",
            "parameter": "ztta/short_area"
        })
        with patch.object(self.module, 'connection') as ret:
            ret.return_value = '1600000'
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
        self.assertEqual(result.exception.args[0]['out'], ['1600000'])
