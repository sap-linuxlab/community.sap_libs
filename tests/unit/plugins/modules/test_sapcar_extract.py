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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.sap_libs.plugins.modules import sapcar_extract
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args
from unittest.mock import patch
from ansible.module_utils import basic


def get_bin_path(*args, **kwargs):
    """Function to return path of SAPCAR"""
    return "/tmp/sapcar"


class Testsapcar_extract(ModuleTestCase):
    """Main class for testing sapcar_extract module."""

    def setUp(self):
        """Setup."""
        super(Testsapcar_extract, self).setUp()
        self.module = sapcar_extract
        self.mock_get_bin_path = patch.object(basic.AnsibleModule, 'get_bin_path', get_bin_path)
        self.mock_get_bin_path.start()
        self.addCleanup(self.mock_get_bin_path.stop)  # ensure that the patching is 'undone'

    def tearDown(self):
        """Teardown."""
        super(Testsapcar_extract, self).tearDown()

    def test_without_required_parameters(self):
        """Failure must occurs when all parameters are missing."""
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def test_sapcar_extract(self):
        """Check that result is changed."""
        args = {
            'path': "/tmp/HANA_CLIENT_REV2_00_053_00_LINUX_X86_64.SAR",
            'dest': "/tmp/test2",
            'binary_path': "/tmp/sapcar"
        }
        with patch('os.path.isfile', return_value=True), \
             patch('os.access', return_value=True), \
             patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=[]), \
             patch.object(basic.AnsibleModule, 'run_command') as run_command:
            run_command.return_value = 0, 'file1\nfile2', ''
            with self.assertRaises(AnsibleExitJson) as result:
                with set_module_args(args):
                    sapcar_extract.main()
            self.assertTrue(result.exception.args[0]['changed'])
        self.assertGreaterEqual(run_command.call_count, 1)

    def test_file_missing(self):
        """Failure must occur when SAR file does not exist."""
        args = {
            'path': "/tmp/nonexistent.SAR",
            'dest': "/tmp/test2",
            'binary_path': "/tmp/sapcar"
        }
        with patch('os.path.isfile', return_value=False):
            with self.assertRaises(AnsibleFailJson) as result:
                with set_module_args(args):
                    sapcar_extract.main()
            self.assertIn('File missing', result.exception.args[0]['msg'])
