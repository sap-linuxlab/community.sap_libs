# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.sap_libs.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()

from ansible_collections.community.sap_libs.plugins.modules import sap_user


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_user

    def tearDown(self):
        super(TestSAPRfcModule, self).tearDown()

    def define_rfc_connect(self, mocker):
        return mocker.patch(self.module.call_rfc_method)

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing"""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            self.module.main()

    def test_error_user_create(self):
        """test fail to create user"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
            "firstname": "first_admin",
            "lastname": "last_admin",
            "email": "admin@test.de",
            "password": "Test123456",
            "useralias": "ADMIN",
            "company": "DEFAULT_COMPANY"
        })

        with patch.object(self.module, 'check_user') as check:
            check.return_value = False

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': 'Something went wrong', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '199',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'E'}]}

                with self.assertRaises(AnsibleFailJson) as result:
                    sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Something went wrong')

    def test_success(self):
        """test execute user create success"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
            "firstname": "first_admin",
            "lastname": "last_admin",
            "email": "admin@test.de",
            "password": "Test123456",
            "useralias": "ADMIN",
            "company": "DEFAULT_COMPANY"
        })
        with patch.object(self.module, 'check_user') as check:
            check.return_value = False

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': 'User ADMIN created', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '102',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

                with self.assertRaises(AnsibleExitJson) as result:
                    sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'User ADMIN created')

    def test_no_changes(self):
        """test execute user no changes"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
            "firstname": "first_admin",
            "lastname": "last_admin",
            "email": "admin@test.de",
            "password": "Test123456",
            "useralias": "ADMIN",
            "company": "DEFAULT_COMPANY"
        })
        with patch.object(self.module, 'check_user') as check:
            check.return_value = True

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': '', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '029',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

                with patch.object(self.module, 'all') as DETAIL:
                    DETAIL.return_value = True

                    with self.assertRaises(AnsibleExitJson) as result:
                        sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'No changes where made.')

    def test_absent(self):
        """test execute user delete success"""

        set_module_args({
            "state": "absent",
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
        })
        with patch.object(self.module, 'check_user') as check:
            check.return_value = True

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': 'User ADMIN deleted', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '102',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

                with self.assertRaises(AnsibleExitJson) as result:
                    sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'User ADMIN deleted')

    def test_lock(self):
        """test execute user lock success"""

        set_module_args({
            "state": "lock",
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
        })
        with patch.object(self.module, 'check_user') as check:
            check.return_value = True

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': 'User ADMIN locked', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '206',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

                with self.assertRaises(AnsibleExitJson) as result:
                    sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'User ADMIN locked')

    def test_unlock(self):
        """test execute user lock success"""

        set_module_args({
            "state": "lock",
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "username": "ADMIN",
        })
        with patch.object(self.module, 'check_user') as check:
            check.return_value = True

            with patch.object(self.module, 'call_rfc_method') as RAW:
                RAW.return_value = {'RETURN': [{'FIELD': 'BNAME', 'ID': '01', 'LOG_MSG_NO': '000000',
                                                'LOG_NO': '', 'MESSAGE': 'User ADMIN unlocked', 'MESSAGE_V1': 'ADMIN',
                                                'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '210',
                                                'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

                with self.assertRaises(AnsibleExitJson) as result:
                    sap_user.main()
        self.assertEqual(result.exception.args[0]['msg'], 'User ADMIN unlocked')
