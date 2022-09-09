# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber (@rainerleber) <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import mock
__metaclass__ = type

from ansible_collections.community.sap_libs.plugins.modules import sap_system_facts
from ansible_collections.community.sap_libs.tests.unit.plugins.modules.utils import AnsibleExitJson, ModuleTestCase
from ansible_collections.community.sap_libs.tests.unit.compat.mock import patch, MagicMock
from ansible.module_utils import basic


def get_bin_path(*args, **kwargs):
    """Function to return path of sapcontrol"""
    return "/usr/sap/hostctrl/exe/sapcontrol"


class Testsap_system_facts(ModuleTestCase):
    """Main class for testing sap_system_facts module."""

    def setUp(self):
        """Setup."""
        super(Testsap_system_facts, self).setUp()
        self.module = sap_system_facts
        self.mock_get_bin_path = patch.object(basic.AnsibleModule, 'get_bin_path', get_bin_path)
        self.mock_get_bin_path.start()
        self.addCleanup(self.mock_get_bin_path.stop)

    def tearDown(self):
        """Teardown."""
        super(Testsap_system_facts, self).tearDown()

    def test_no_systems_available(self):
        """No SAP Systems"""
        with self.assertRaises(AnsibleExitJson) as result:
            self.module.main()
        self.assertEqual(result.exception.args[0]['ansible_facts'], {})

    def test_sap_system_facts_all(self):
        """Check that result is changed when all is one system."""
        with patch.object(self.module, 'get_all_hana_sid') as get_all_hana_sid:
            get_all_hana_sid.return_value = ['HDB']
            with patch.object(self.module, 'get_hana_nr') as get_hana_nr:
                get_hana_nr.return_value = [{"InstanceType": "HANA", "NR": "01", "SID": "HDB", "TYPE": "HDB"}]
                with patch.object(self.module, 'get_all_nw_sid') as get_all_nw_sid:
                    get_all_nw_sid.return_value = ['ABC']
                    with patch.object(self.module, 'get_nw_nr') as get_nw_nr:
                        get_nw_nr.return_value = [{"InstanceType": "NW", "NR": "00", "SID": "ABC", "TYPE": "ASCS"},
                                                  {"InstanceType": "NW", "NR": "01", "SID": "ABC", "TYPE": "PAS"}]
                        with self.assertRaises(AnsibleExitJson) as result:
                            self.module.main()
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{"InstanceType": "HANA", "NR": "01", "SID": "HDB", "TYPE": "HDB"},
                                                                             {"InstanceType": "NW", "NR": "00", "SID": "ABC", "TYPE": "ASCS"},
                                                                             {"InstanceType": "NW", "NR": "01", "SID": "ABC", "TYPE": "PAS"}]})

    def test_sap_system_facts_command_hana(self):
        """Check that result for HANA is correct."""
        with patch.object(self.module, 'get_all_hana_sid') as mock_all_hana_sid:
            mock_all_hana_sid.return_value = ['HDB']
            with patch.object(self.module.os, 'listdir') as mock_listdir:
                mock_listdir.return_value = ['HDB01']
                with patch.object(basic.AnsibleModule, 'run_command') as run_command:
                    run_command.return_value = [0, '', '']
                    with self.assertRaises(AnsibleExitJson) as result:
                        self.module.main()
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{"InstanceType": "HANA", "NR": "01", "SID": "HDB", "TYPE": "HDB"}]})

    def test_sap_system_facts_pas_nw(self):
        """Check that result for NW is correct."""
        with patch.object(self.module, 'get_all_nw_sid') as mock_all_nw_sid:
            mock_all_nw_sid.return_value = ['ABC']
            with patch.object(self.module.os, 'listdir') as mock_listdir:
                mock_listdir.return_value = ['D00']
                with patch.object(basic.AnsibleModule, 'run_command') as run_command:
                    run_command.return_value = [0, 'SAP\nINSTANCE_NAME, Attribute, D00\nSAP', '']
                    with self.assertRaises(AnsibleExitJson) as result:
                        self.module.main()
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{'InstanceType': 'NW', 'NR': '00', 'SID': 'ABC', 'TYPE': 'PAS'}]})

    def test_sap_system_facts_future_nw(self):
        """Check that future apps for NW are correct handled."""
        with patch.object(self.module, 'get_all_nw_sid') as mock_all_nw_sid:
            mock_all_nw_sid.return_value = ['ABC']
            with patch.object(self.module.os, 'listdir') as mock_listdir:
                mock_listdir.return_value = ['XY00']
                with patch.object(basic.AnsibleModule, 'run_command') as run_command:
                    run_command.return_value = [0, 'SAP\nINSTANCE_NAME, Attribute, XY00\nSAP', '']
                    with self.assertRaises(AnsibleExitJson) as result:
                        self.module.main()
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{'InstanceType': 'NW', 'NR': '00', 'SID': 'ABC', 'TYPE': 'XXX'}]})

    def test_sap_system_facts_wd_nw(self):
        """Check that WD for NW is correct handled."""
        with patch.object(self.module, 'get_all_nw_sid') as mock_all_nw_sid:
            mock_all_nw_sid.return_value = ['ABC']
            with patch.object(self.module.os, 'listdir') as mock_listdir:
                mock_listdir.return_value = ['WD80']
                with patch.object(basic.AnsibleModule, 'run_command') as run_command:
                    run_command.return_value = [0, 'SAP\nINSTANCE_NAME, Attribute, WD80\nSAP', '']
                    with self.assertRaises(AnsibleExitJson) as result:
                        self.module.main()
        self.assertEqual(result.exception.args[0]['ansible_facts'], {'sap': [{'InstanceType': 'NW', 'NR': '80', 'SID': 'ABC', 'TYPE': 'WebDisp'}]})
