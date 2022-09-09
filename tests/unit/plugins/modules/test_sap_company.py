# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.sap_libs.tests.unit.compat.mock import patch, MagicMock
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()

from ansible_collections.community.sap_libs.plugins.modules import sap_company


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_company

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
        """test fail to create company"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "company_id": "Comp_ID",
            "name": "Test_comp",
            "name_2": "LTD",
            "country": "DE",
            "time_zone": "UTC",
            "city": "City",
            "post_code": "12345",
            "street": "test_street",
            "street_no": "1",
            "e_mail": "test@test.de",
        })
        with patch.object(self.module, 'call_rfc_method') as RAW:
            RAW.return_value = {'RETURN': [{'FIELD': '', 'ID': '01', 'LOG_MSG_NO': '000000',
                                            'LOG_NO': '', 'MESSAGE': 'Something went wrong', 'MESSAGE_V1': 'ADMIN',
                                            'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '199',
                                            'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'E'}]}

            with self.assertRaises(AnsibleFailJson) as result:
                sap_company.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Something went wrong')

    def test_success(self):
        """test execute company create success"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "company_id": "Comp_ID",
            "name": "Test_comp",
            "name_2": "LTD",
            "country": "DE",
            "time_zone": "UTC",
            "city": "City",
            "post_code": "12345",
            "street": "test_street",
            "street_no": "1",
            "e_mail": "test@test.de",
        })
        with patch.object(self.module, 'call_rfc_method') as RAW:
            RAW.return_value = {'RETURN': [{'FIELD': '', 'ID': '01', 'LOG_MSG_NO': '000000',
                                            'LOG_NO': '', 'MESSAGE': 'Company address COMP_ID created', 'MESSAGE_V1': 'ADMIN',
                                            'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '102',
                                            'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

            with self.assertRaises(AnsibleExitJson) as result:
                sap_company.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Company address COMP_ID created')

    def test_no_changes(self):
        """test execute company no changes"""

        set_module_args({
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "company_id": "Comp_ID",
            "name": "Test_comp",
            "name_2": "LTD",
            "country": "DE",
            "time_zone": "UTC",
            "city": "City",
            "post_code": "12345",
            "street": "test_street",
            "street_no": "1",
            "e_mail": "test@test.de",
        })
        with patch.object(self.module, 'call_rfc_method') as RAW:
            RAW.return_value = {'RETURN': [{'FIELD': '', 'ID': '01', 'LOG_MSG_NO': '000000',
                                            'LOG_NO': '', 'MESSAGE': 'Company address COMP_ID changed', 'MESSAGE_V1': 'ADMIN',
                                            'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '079',
                                            'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

            with self.assertRaises(AnsibleExitJson) as result:
                sap_company.main()
        self.assertEqual(result.exception.args[0]['msg'], 'No changes where made.')

    def test_absent(self):
        """test execute company delete success"""

        set_module_args({
            "state": "absent",
            "conn_username": "DDIC",
            "conn_password": "Test1234",
            "host": "10.1.8.9",
            "company_id": "Comp_ID",
        })
        with patch.object(self.module, 'call_rfc_method') as RAW:
            RAW.return_value = {'RETURN': [{'FIELD': '', 'ID': '01', 'LOG_MSG_NO': '000000',
                                            'LOG_NO': '', 'MESSAGE': 'Company address COMP_ID deleted', 'MESSAGE_V1': 'ADMIN',
                                            'MESSAGE_V2': '', 'MESSAGE_V3': '', 'MESSAGE_V4': '', 'NUMBER': '080',
                                            'PARAMETER': '', 'ROW': 0, 'SYSTEM': '', 'TYPE': 'S'}]}

            with self.assertRaises(AnsibleExitJson) as result:
                sap_company.main()
        self.assertEqual(result.exception.args[0]['msg'], 'Company address COMP_ID deleted')
