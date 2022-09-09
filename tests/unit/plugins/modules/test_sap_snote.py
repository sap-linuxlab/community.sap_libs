# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.sap_libs.tests.unit.compat.mock import patch, MagicMock, Mock
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
            set_module_args({})
            self.module.main()

    def test_error_module_not_found(self):
        """tests fail module error"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        })
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.HAS_PYRFC_LIBRARY = False
            self.module.ANOTHER_LIBRARY_IMPORT_ERROR = 'Module not found'
            self.module.main()
        self.assertEqual(result.exception.args[0]['exception'], 'Module not found')

    def test_error_connection(self):
        """tests fail module error"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        })
        with self.assertRaises(AnsibleFailJson) as result:
            self.module.Connection.side_effect = Mock(side_effect=Exception('Test'))
            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Something went wrong connecting to the SAP system.')

    def test_error_wrong_path(self):
        """tests fail wrong path extension"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456_00.tx"
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'The path must include the extracted snote file and ends with txt.')

    def test_error_wrong_user(self):
        """tests fail wrong path extension"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "snote_path": "/user/sap/trans/temp/000123456_00.tx"
        })

        with self.assertRaises(AnsibleFailJson) as result:
            self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'User C(DDIC) or C(SAP*) not allowed for this operation.')

    def test_success_absent(self):
        """test absent execute snote"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "absent",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        })
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [True, False]
                    self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" deimplemented.')

    def test_success_absent_snot_only(self):
        """test absent execute snote"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "absent",
            "snote": "000123456"
        })
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [True, False]
                    self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" deimplemented.')

    def test_nothing_to_do(self):
        """test nothing to do"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "present",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        })
        with patch.object(self.module, 'check_implementation') as check:
            check.return_value = True
            with self.assertRaises(AnsibleExitJson) as result:
                self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Nothing to do.')

    def test_success_present_with_copy(self):
        """test present execute snote"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "present",
            "snote_path": "/user/sap/trans/temp/000123456.txt"
        })
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [False, True]
                    with patch.object(self.module, 'call_rfc_method') as callrfc:
                        callrfc.side_effect = [{'EV_RC': 0}, {'EV_RC': 0}, {'ET_MANUAL_ACTIVITIES': ''}]
                        self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" implemented.')

    def test_success_present_implement_only(self):
        """test present implement snote"""

        set_module_args({
            "conn_username": "ADMIN",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "state": "present",
            "snote": "000123456"
        })
        with patch.object(self.module, 'call_rfc_method') as call:
            call.return_value = {'EV_RC': 0}
            with self.assertRaises(AnsibleExitJson) as result:
                with patch.object(self.module, 'check_implementation') as check:
                    check.side_effect = [False, True]
                    with patch.object(self.module, 'call_rfc_method') as callrfc:
                        callrfc.side_effect = [{'EV_RC': 0}, {'ET_MANUAL_ACTIVITIES': ''}]
                        self.module.main()
        self.assertEqual(result.exception.args[0]['msg'], 'SNOTE "000123456" implemented.')
