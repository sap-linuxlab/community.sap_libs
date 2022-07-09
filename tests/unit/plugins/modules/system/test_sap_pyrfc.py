# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from ansible_collections.community.sap_libs.plugins.modules.system import sap_pyrfc
__metaclass__ = type

import sys
from ansible_collections.community.sap_libs.tests.unit.compat.mock import patch, MagicMock, Mock, PropertyMock
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args

sys.modules['pyrfc'] = MagicMock()
sys.modules['pyrfc.Connection'] = MagicMock()


class TestSAPRfcModule(ModuleTestCase):

    def setUp(self):
        super(TestSAPRfcModule, self).setUp()
        self.module = sap_pyrfc

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

    def test_error_communication(self):
        """tests fail missing connections details"""

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

        with patch.object(self.module, 'get_connection') as connection:
            connection.return_value.ok = PropertyMock(return_value=False)

            with self.assertRaises(AnsibleFailJson) as result:
                self.module.Connection.side_effect = Mock(
                    side_effect=Exception(KeyError, 'This error'))
                self.module.main()
        self.assertEqual(result.exception.args[0], {})

    # def test_success(self):
    #     """test execute task list success"""

    #     set_module_args({
    #         "function": "STFC_CONNECTION",
    #         "parameters": { "REQUTEXT": "Hello SAP!" },
    #         "connection": { "ashost": "s4hana.poc.cloud",
    #                         "sysnr": "01",
    #                         "client": "400",
    #                         "user": "DDIC",
    #                         "passwd": "Password1",
    #                         "lang": "EN" },
    #         "conn_username": "DDIC",
    #         "conn_password": "Test1234",
    #         "host": "10.1.8.9",
    #         "task_to_execute": "SAP_BASIS_SSL_CHECK"
    #     })
    #     with patch.object(self.module, 'xml_to_dict') as XML:
    #         XML.return_value = {'item': [{'TASK': {'CHECK_STATUS_DESCR': 'Check successfully',
    #                                                'STATUS_DESCR': 'Executed successfully', 'TASKNAME': 'CL_STCT_CHECK_SEC_CRYPTO',
    #                                                'LNR': '1', 'DESCRIPTION': 'Check SAP Cryptographic Library', 'DOCU_EXIST': 'X',
    #                                                'LOG_EXIST': 'X', 'ACTION_SKIP': None, 'ACTION_UNSKIP': None, 'ACTION_CONFIRM': None,
    #                                                'ACTION_MAINTAIN': None}}]}

    #         with self.assertRaises(AnsibleExitJson) as result:
    #             sap_task_list_execute.main()
    #     self.assertEqual(result.exception.args[0]['out'], {'item': [{'TASK': {'CHECK_STATUS_DESCR': 'Check successfully',
    #                                                                           'STATUS_DESCR': 'Executed successfully', 'TASKNAME': 'CL_STCT_CHECK_SEC_CRYPTO',
    #                                                                           'LNR': '1', 'DESCRIPTION': 'Check SAP Cryptographic Library', 'DOCU_EXIST': 'X',
    #                                                                           'LOG_EXIST': 'X', 'ACTION_SKIP': None, 'ACTION_UNSKIP': None,
    #                                                                           'ACTION_CONFIRM': None, 'ACTION_MAINTAIN': None}}]})

    # def test_success_no_log(self):
    #     """test execute task list success without logs"""

    #     set_module_args({
    #         "conn_username": "DDIC",
    #         "conn_password": "Test1234",
    #         "host": "10.1.8.9",
    #         "task_to_execute": "SAP_BASIS_SSL_CHECK"
    #     })
    #     with patch.object(self.module, 'xml_to_dict') as XML:
    #         XML.return_value = "No logs available."
    #         with self.assertRaises(AnsibleExitJson) as result:
    #             sap_task_list_execute.main()
    #     self.assertEqual(result.exception.args[0]['out'], 'No logs available.')
