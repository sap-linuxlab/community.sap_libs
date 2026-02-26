# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber (@rainerleber) <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.sap_libs.plugins.modules import sap_hdbsql
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
from unittest.mock import patch
from ansible.module_utils import basic


def get_bin_path(*args, **kwargs):
    """Function to return path of hdbsql"""
    return "/usr/sap/HDB/HDB01/exe/hdbsql"


class Testsap_hdbsql(ModuleTestCase):
    """Main class for testing sap_hdbsql module."""

    def setUp(self):
        """Setup."""
        super(Testsap_hdbsql, self).setUp()
        self.module = sap_hdbsql
        self.mock_get_bin_path = patch.object(basic.AnsibleModule, 'get_bin_path', get_bin_path)
        self.mock_get_bin_path.start()
        self.addCleanup(self.mock_get_bin_path.stop)  # ensure that the patching is 'undone'

    def tearDown(self):
        """Teardown."""
        super(Testsap_hdbsql, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing."""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_sap_hdbsql(self):
        """Check that result is processed."""
        args = {
            'sid': "HDB",
            'instance': "01",
            'encrypted': False,
            'host': "localhost",
            'user': "SYSTEM",
            'password': "1234Qwer",
            'database': "HDB",
            'query': ["SELECT * FROM users;"]
        }
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, 'username,name\n  testuser,test user  \n myuser, my user   \n', ''
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    sap_hdbsql.main()
            self.assertEqual(result.exception.args[0]['query_result'], [[
                {'username': 'testuser', 'name': 'test user'},
                {'username': 'myuser', 'name': 'my user'},
            ]])
        self.assertEqual(run_command.call_count, 1)

    def test_hana_userstore_query(self):
        """Check that result is processed with userstore."""
        args = {
            'sid': "HDB",
            'instance': "01",
            'encrypted': False,
            'host': "localhost",
            'user': "SYSTEM",
            'userstore': True,
            'database': "HDB",
            'query': ["SELECT * FROM users;"]
        }
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, 'username,name\n  testuser,test user  \n myuser, my user   \n', ''
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    sap_hdbsql.main()
            self.assertEqual(result.exception.args[0]['query_result'], [[
                {'username': 'testuser', 'name': 'test user'},
                {'username': 'myuser', 'name': 'my user'},
            ]])
        self.assertEqual(run_command.call_count, 1)

    def test_hana_failed_no_passwd(self):
        """Check that result is failed with no password."""
        with self.assertRaises(AnsibleFailJson):
            args = {
                'sid': "HDB",
                'instance': "01",
                'encrypted': False,
                'host': "localhost",
                'user': "SYSTEM",
                'database': "HDB",
                'query': ["SELECT * FROM users;"]
            }
            with set_module_args(args):
                self.module.main()

    def test_changed_status_select(self):
        """Verify SELECT query returns changed=False"""
        args = {
            'sid': "HDB",
            'instance': "01",
            'password': "pwd",
            'query': ["SELECT * FROM users;"]
        }
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, 'col1\nval1', ''
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    self.module.main()
            self.assertFalse(result.exception.args[0]['changed'])

    def test_changed_status_update(self):
        """Verify UPDATE query returns changed=True"""
        args = {
            'sid': "HDB",
            'instance': "01",
            'password': "pwd",
            'query': ["UPDATE users SET name='test';"]
        }
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, '', '' # Updates often return empty string
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    self.module.main()
            self.assertTrue(result.exception.args[0]['changed'])

    def test_authentication_failure(self):
        """Verify specific error message for Auth Failure"""
        args = {
            'sid': "HDB",
            'instance': "01",
            'password': "wrong",
            'query': ["SELECT 1 FROM DUMMY;"]
        }
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 10, '', 'Authentication failed'
            with self.assertRaises(AnsibleFailJson) as result:
                with set_module_args(args):
                    self.module.main()
            self.assertIn("Authentication Failed", result.exception.args[0]['msg'])

    def test_insufficient_privilege(self):
        """Verify specific error message for Privilege Error (Error 258)"""
        args = {
            'sid': "HDB",
            'instance': "01",
            'password': "pwd",
            'query': ["DROP TABLE important_stuff;"]
        }
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 1, '', '* 258: insufficient privilege'
            with self.assertRaises(AnsibleFailJson) as result:
                with set_module_args(args):
                    self.module.main()
            self.assertIn("Authorization Error", result.exception.args[0]['msg'])

    def test_encrypted_connection_flags(self):
        """Verify that encryption flags are correctly added to the command"""
        args = {
            'sid': "HDB",
            'instance': "01",
            'password': "pwd",
            'encrypted': True,
            'query': ["SELECT 1 FROM DUMMY;"]
        }
        with patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, '1', ''
            with self.assertRaises(AnsibleExitJson):
                with set_module_args(args):
                    self.module.main()
            
            # Get the actual command executed
            executed_cmd = run_command.call_args[0][0]
            self.assertIn('-e', executed_cmd)
            self.assertIn('-ssltrustcert', executed_cmd)
            self.assertIn('-sslcreatecert', executed_cmd)
