# -*- coding: utf-8 -*-
'''
Describe test for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from shutil import rmtree
from datetime import date, timedelta
from base64 import b64decode
from django.utils import six

from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir
from lucterios.CORE.views import StatusMenu

from diacamma.accounting.views import ThirdList, ThirdAdd, ThirdSave, ThirdShow, AccountThirdAddModify, AccountThirdDel, ThirdListing, ThirdDisable
from diacamma.accounting.views_admin import Configuration, JournalAddModify, JournalDel, FiscalYearAddModify, FiscalYearActive, FiscalYearDel
from diacamma.accounting.views_other import ModelEntryList, ModelEntryAddModify, ModelLineEntryAddModify
from diacamma.accounting.test_tools import initial_contacts, fill_entries, initial_thirds, create_third, fill_accounts, fill_thirds, default_compta, set_accounting_system, add_models
from diacamma.accounting.models import FiscalYear
from diacamma.accounting.system import get_accounting_system
from diacamma.accounting.tools import current_system_account, clear_system_account
from diacamma.accounting.views_entries import EntryAccountModelSelector


class ThirdTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        initial_contacts()
        rmtree(get_user_dir(), True)
        clear_system_account()

    def test_add_abstract(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdAdd()
        self.call('/diacamma.accounting/thirdAdd', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal(
            'COMPONENTS/SELECT[@name="modelname"]', 'contacts.AbstractContact', (2, 0, 3, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="modelname"]/CASE', 3)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="abstractcontact"]/HEADER', 4)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="abstractcontact"]/RECORD', 8)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave',
                  {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton Joe')

    def test_add_legalentity(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdAdd()
        self.call('/diacamma.accounting/thirdAdd',
                  {'modelname': 'contacts.LegalEntity'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal(
            'COMPONENTS/SELECT[@name="modelname"]', 'contacts.LegalEntity', (2, 0, 3, 1))
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="legalentity"]/HEADER', 4)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="legalentity"]/RECORD', 3)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave',
                  {'pkname': 'legalentity', 'legalentity': 7}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Minimum')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="contact"]', 'Minimum')
        self.assert_attrib_equal(
            'COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'extension', 'lucterios.contacts')
        self.assert_attrib_equal(
            'COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'action', 'legalEntityShow')
        self.assert_xml_equal(
            'COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION/PARAM[@name="legal_entity"]', '7')

    def test_add_individual(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdAdd()
        self.call('/diacamma.accounting/thirdAdd',
                  {'modelname': 'contacts.Individual'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal(
            'COMPONENTS/SELECT[@name="modelname"]', 'contacts.Individual', (2, 0, 3, 1))
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="individual"]/HEADER', 5)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="individual"]/RECORD', 5)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave',
                  {'pkname': 'individual', 'individual': 3}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton William')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="contact"]', 'Dalton William')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'extension', 'lucterios.contacts')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'action', 'individualShow')
        self.assert_xml_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION/PARAM[@name="individual"]', '3')

    def test_check_double(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave',
                  {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave',
                  {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave',
                  {'pkname': 'abstractcontact', 'abstractcontact': 5}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)

    def test_show(self):
        create_third([3])
        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/TAB', 1)
        self.assert_count_equal('COMPONENTS/*', 16 + 7)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="contact"]', 'Dalton William')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'Actif')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/HEADER', 2)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/HEADER[@name="code"]', "code")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/HEADER[@name="total_txt"]', "total")
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 0)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '0.00€')

        self.factory.xfer = AccountThirdAddModify()
        self.call(
            '/diacamma.accounting/accountThirdAddModify', {"third": 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'accountThirdAddModify')
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', None)

        self.factory.xfer = AccountThirdAddModify()
        self.call('/diacamma.accounting/accountThirdAddModify',
                  {'SAVE': 'YES', "third": 1, 'code': '411'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'accountThirdAddModify')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/HEADER', 2)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="code"]', '411')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="total_txt"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '0.00€')

        self.factory.xfer = AccountThirdDel()
        self.call('/diacamma.accounting/accountThirdDel',
                  {'CONFIRME': 'YES', "accountthird": 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.accounting', 'accountThirdDel')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/HEADER', 2)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 0)

    def test_show_withdata(self):
        fill_thirds()
        default_compta()
        fill_entries(1)
        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 16 + 7 + 4 + 4)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="contact"]', 'Minimum')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'Actif')
        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER[@name="code"]', "code")
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER[@name="total_txt"]', "total")

        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD', 2)
        self.assert_attrib_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[1]', 'id', '5')

        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="code"]', '411')
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="total_txt"]',
                              '{[font color="blue"]}Débit: 34.01€{[/font]}')
        self.assert_attrib_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[2]', 'id', '6')

        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[2]/VALUE[@name="code"]', '401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[2]/VALUE[@name="total_txt"]',
                              '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '-34.01€')

        self.assert_xml_equal('COMPONENTS/SELECT[@name="lines_filter"]', '0')
        self.assert_count_equal('COMPONENTS/SELECT[@name="lines_filter"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '2')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('63.94€' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="num"]', '3')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('63.94€' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="description"]').text
        self.assertTrue('34.01€' in description, description)

        self.factory.xfer = AccountThirdDel()
        self.call('/diacamma.accounting/accountThirdDel', {"accountthird": 5}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'accountThirdDel')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Ce compte n'est pas soldé!")

        self.factory.xfer = AccountThirdDel()
        self.call('/diacamma.accounting/accountThirdDel', {"accountthird": 6}, False)
        self.assert_observer('core.dialogbox', 'diacamma.accounting', 'accountThirdDel')

    def test_show_withdata_linesfilter(self):
        fill_thirds()
        default_compta()
        fill_entries(1)

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow',
                  {"third": 4, 'lines_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 16 + 7 + 4 + 4)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="lines_filter"]', '0')
        self.assert_count_equal('COMPONENTS/SELECT[@name="lines_filter"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow',
                  {"third": 4, 'lines_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 16 + 7 + 4 + 4)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="lines_filter"]', '1')
        self.assert_count_equal('COMPONENTS/SELECT[@name="lines_filter"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)

        default_compta()

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow',
                  {"third": 4, 'lines_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 16 + 7 + 4 + 4)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="lines_filter"]', '0')
        self.assert_count_equal('COMPONENTS/SELECT[@name="lines_filter"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 4, 'lines_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 16 + 7 + 4 + 4)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="lines_filter"]', '2')
        self.assert_count_equal('COMPONENTS/SELECT[@name="lines_filter"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)

    def test_list(self):
        fill_thirds()

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/HEADER', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="contact"]', "contact")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="accountthird_set"]', "compte")
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 7)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton Avrel')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="accountthird_set"]', '401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="contact"]', 'Dalton Jack')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="accountthird_set"]', '411')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[3]/VALUE[@name="contact"]', 'Dalton Joe')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[3]/VALUE[@name="accountthird_set"]', '411')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[4]/VALUE[@name="contact"]', 'Dalton William')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[4]/VALUE[@name="accountthird_set"]', '411')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[5]/VALUE[@name="contact"]', 'Luke Lucky')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[5]/VALUE[@name="accountthird_set"]', '411{[br/]}401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[6]/VALUE[@name="contact"]', 'Maximum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[6]/VALUE[@name="accountthird_set"]', '401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[7]/VALUE[@name="contact"]', 'Minimum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[7]/VALUE[@name="accountthird_set"]', '411{[br/]}401')

    def test_list_withfilter(self):
        fill_thirds()
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {'filter': 'joe'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/HEADER', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="contact"]', "contact")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="accountthird_set"]', "compte")
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton Joe')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="accountthird_set"]', '411')

    def test_list_display(self):
        fill_thirds()
        default_compta()
        fill_entries(1)
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {'show_filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/HEADER', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="contact"]', "contact")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="accountthird_set"]', "compte")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="total"]', "total")
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 7)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="contact"]', 'Dalton Jack')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="accountthird_set"]', '411')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="total"]', '0.00€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[4]/VALUE[@name="contact"]', 'Dalton William')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[4]/VALUE[@name="accountthird_set"]', '411')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[4]/VALUE[@name="total"]', '-125.97€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[7]/VALUE[@name="contact"]', 'Minimum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[7]/VALUE[@name="accountthird_set"]', '411{[br/]}401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[7]/VALUE[@name="total"]', '-34.01€')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {'show_filter': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/HEADER', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="contact"]', "contact")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="accountthird_set"]', "compte")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="total"]', "total")
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton William')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="accountthird_set"]', '411')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="total"]', '-125.97€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="contact"]', 'Maximum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="accountthird_set"]', '401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="total"]', '78.24€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[3]/VALUE[@name="contact"]', 'Minimum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[3]/VALUE[@name="accountthird_set"]', '411{[br/]}401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[3]/VALUE[@name="total"]', '-34.01€')

    def test_listing(self):
        fill_thirds()
        default_compta()
        fill_entries(1)
        self.factory.xfer = ThirdListing()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_comp_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]', "3", (1, 0, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]/CASE', 2)
        self.assert_comp_equal('COMPONENTS/SELECT[@name="MODEL"]', "5", (1, 1, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="MODEL"]/CASE', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = ThirdListing()
        self.call('/diacamma.accounting/thirdListing',
                  {'PRINT_MODE': '4', 'MODEL': 5}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'thirdListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 14, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste de tiers"')
        self.assertEqual(content_csv[3].strip(), '"contact";"compte";"total";')
        self.assertEqual(content_csv[4].strip(), '"Dalton Avrel";"401";"0.00€";')
        self.assertEqual(content_csv[5].strip(), '"Dalton Jack";"411";"0.00€";')
        self.assertEqual(content_csv[6].strip(), '"Dalton Joe";"411";"0.00€";')
        self.assertEqual(content_csv[7].strip(), '"Dalton William";"411";"-125.97€";')
        self.assertEqual(content_csv[8].strip(), '"Luke Lucky";"411 401";"0.00€";')
        self.assertEqual(content_csv[9].strip(), '"Maximum";"401";"78.24€";')
        self.assertEqual(content_csv[10].strip(), '"Minimum";"411 401";"-34.01€";')

        self.factory.xfer = ThirdListing()
        self.call('/diacamma.accounting/individualListing', {'PRINT_MODE': '4', 'MODEL': 5, 'filter': 'joe'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'individualListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 8, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste de tiers"')
        self.assertEqual(content_csv[3].strip(), '"contact";"compte";"total";')
        self.assertEqual(content_csv[4].strip(), '"Dalton Joe";"411";"0.00€";')

        self.factory.xfer = ThirdListing()
        self.call('/diacamma.accounting/individualListing', {'PRINT_MODE': '4', 'MODEL': 5, 'show_filter': '2'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'individualListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 10, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste de tiers"')
        self.assertEqual(content_csv[3].strip(), '"contact";"compte";"total";')
        self.assertEqual(content_csv[4].strip(), '"Dalton William";"411";"-125.97€";')
        self.assertEqual(content_csv[5].strip(), '"Maximum";"401";"78.24€";')
        self.assertEqual(content_csv[6].strip(), '"Minimum";"411 401";"-34.01€";')

    def test_list_disable(self):
        fill_thirds()
        default_compta()
        fill_entries(1)
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {'show_filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 7)

        self.factory.xfer = ThirdDisable()
        self.call('/diacamma.accounting/thirdDisable', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdDisable')
        self.assert_count_equal('COMPONENTS/*', 3)

        self.factory.xfer = ThirdDisable()
        self.call('/diacamma.accounting/thirdDisable', {'limit_date': '2015-02-18'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'thirdDisable')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {'show_filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 4)


class AdminTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        rmtree(get_user_dir(), True)

    def test_summary(self):
        self.factory.xfer = StatusMenu()
        self.call('/CORE/statusMenu', {}, False)
        self.assert_observer('core.custom', 'CORE', 'statusMenu')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accountingtitle']", "{[center]}{[u]}{[b]}Comptabilité{[/b]}{[/u]}{[/center]}")
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accounting_error']", "{[center]}Pas d'exercice défini!{[/center]}")
        self.assert_action_equal("COMPONENTS/BUTTON[@name='accounting_conf']/ACTIONS/ACTION",
                                 ("conf.", None, 'diacamma.accounting', 'configuration', 0, 1, 1))

    def test_default_configuration(self):
        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 2 + 3 + 5 + 2 + 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="begin"]', "début")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="end"]', "fin")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="status"]', "status")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="is_actif"]', "actif")
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 0)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="nb_fiscalyear"]', 'Nombre total de exercices: 0')

        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/HEADER', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/HEADER[@name="name"]', "nom")
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="1"]/VALUE[@name="name"]', 'Report à nouveau')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="2"]/VALUE[@name="name"]', 'Achats')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="3"]/VALUE[@name="name"]', 'Ventes')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="4"]/VALUE[@name="name"]', 'Règlement')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="5"]/VALUE[@name="name"]', 'Opérations diverses')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="nb_journal"]', 'Nombre total de journaux: 5')

        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="accounting-devise"]', '€')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="accounting-devise-iso"]', 'EUR')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="accounting-devise-prec"]', '2')

    def test_configuration_journal(self):
        self.factory.xfer = JournalAddModify()
        self.call('/diacamma.accounting/journalAddModify', {'journal': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'journalAddModify')
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', 'Achats')

        self.factory.xfer = JournalAddModify()
        self.call('/diacamma.accounting/journalAddModify', {'SAVE': 'YES', 'journal': '2', 'name': 'Dépense'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="2"]/VALUE[@name="name"]', 'Dépense')

        self.factory.xfer = JournalAddModify()
        self.call('/diacamma.accounting/journalAddModify', {'SAVE': 'YES', 'name': 'Caisse'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 6)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="6"]/VALUE[@name="name"]', 'Caisse')

        self.factory.xfer = JournalDel()
        self.call('/diacamma.accounting/journalAddModify', {'journal': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'journalAddModify')
        self.assert_xml_equal('EXCEPTION/MESSAGE', 'journal réservé!')

        self.factory.xfer = JournalDel()
        self.call('/diacamma.accounting/journalAddModify', {'CONFIRME': 'YES', 'journal': '6'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 5)

    def test_configuration_fiscalyear(self):
        to_day = date.today()
        try:
            to_day_plus_1 = date(to_day.year + 1, to_day.month, to_day.day) - timedelta(days=1)
        except ValueError:
            to_day_plus_1 = date(to_day.year + 1, to_day.month, to_day.day - 1)

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Système comptable non défini!")

        set_accounting_system()

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'en création')
        self.assert_xml_equal('COMPONENTS/DATE[@name="begin"]', to_day.isoformat())
        self.assert_xml_equal('COMPONENTS/DATE[@name="end"]', to_day_plus_1.isoformat())

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {'SAVE': 'YES', 'begin': '2015-07-01', 'end': '2016-06-30'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="begin"]', '1 juillet 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="end"]', '30 juin 2016')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="status"]', "en création")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="is_actif"]', "1")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="nb_fiscalyear"]', 'Nombre total de exercices: 1')

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal("CONTEXT/PARAM[@name='begin']", "2016-07-01")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'en création')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="begin"]', '1 juillet 2016')
        self.assert_xml_equal('COMPONENTS/DATE[@name="end"]', '2017-06-30')

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {'SAVE': 'YES', 'begin': '2016-07-01', 'end': '2017-06-30'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="begin"]', '1 juillet 2016')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="end"]', '30 juin 2017')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="status"]', "en création")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="is_actif"]', "0")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="nb_fiscalyear"]', 'Nombre total de exercices: 2')

        self.factory.xfer = FiscalYearActive()
        self.call('/diacamma.accounting/fiscalYearActive', {'fiscalyear': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearActive')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="is_actif"]', "0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="is_actif"]', "1")

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {'fiscalyear': '1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Cet exercice n'est pas le dernier!")

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {'fiscalyear': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'en création')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="begin"]', '1 juillet 2016')
        self.assert_xml_equal('COMPONENTS/DATE[@name="end"]', '2017-06-30')

    def test_confi_delete(self):
        year1 = FiscalYear.objects.create(
            begin='2014-07-01', end='2015-06-30', status=2, is_actif=False, last_fiscalyear=None)
        year2 = FiscalYear.objects.create(
            begin='2015-07-01', end='2016-06-30', status=1, is_actif=False, last_fiscalyear=year1)
        FiscalYear.objects.create(begin='2016-07-01', end='2017-06-30', status=0,
                                  is_actif=True, last_fiscalyear=year2)
        set_accounting_system()
        initial_thirds()
        fill_accounts()
        fill_entries(3)

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 3)

        self.factory.xfer = FiscalYearDel()
        self.call(
            '/diacamma.accounting/fiscalYearDel', {'fiscalyear': '1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearDel')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Cet exercice n'est pas le dernier!")

        self.factory.xfer = FiscalYearDel()
        self.call(
            '/diacamma.accounting/fiscalYearDel', {'fiscalyear': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearDel')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Cet exercice n'est pas le dernier!")

        self.factory.xfer = FiscalYearDel()
        self.call('/diacamma.accounting/fiscalYearDel', {'CONFIRME': 'YES', 'fiscalyear': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearDel')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 2)

        self.factory.xfer = FiscalYearDel()
        self.call('/diacamma.accounting/fiscalYearDel',
                  {'CONFIRME': 'YES', 'fiscalyear': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearDel')

        self.factory.xfer = FiscalYearDel()
        self.call('/diacamma.accounting/fiscalYearDel', {'fiscalyear': '1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearDel')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Cet exercice est terminé!")

    def test_system_accounting(self):
        self.assertEqual(get_accounting_system('').__class__.__name__, "DefaultSystemAccounting")
        self.assertEqual(get_accounting_system('accountingsystem.foo.DummySystemAcounting').__class__.__name__, "DefaultSystemAccounting")
        self.assertEqual(get_accounting_system(
            'diacamma.accounting.system.french.DummySystemAcounting').__class__.__name__, "DefaultSystemAccounting")
        self.assertEqual(get_accounting_system('diacamma.accounting.system.french.FrenchSystemAcounting').__class__.__name__, "FrenchSystemAcounting")

        self.assertEqual(current_system_account().__class__.__name__, "DefaultSystemAccounting")
        set_accounting_system()
        self.assertEqual(current_system_account().__class__.__name__, "FrenchSystemAcounting")


class ModelTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        initial_thirds()
        rmtree(get_user_dir(), True)
        clear_system_account()
        default_compta()

    def test_add(self):
        self.factory.xfer = ModelEntryList()
        self.call('/diacamma.accounting/modelEntryList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryList')
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="modelentry"]/HEADER', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/HEADER[@name="journal"]', "journal")
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/HEADER[@name="designation"]', "nom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/HEADER[@name="total"]', "total")
        self.assert_count_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD', 0)

        self.factory.xfer = ModelEntryAddModify()
        self.call('/diacamma.accounting/modelEntryAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_count_equal('COMPONENTS/SELECT[@name="journal"]/CASE', 4)
        self.assert_count_equal('COMPONENTS/SELECT[@name="costaccounting"]/CASE', 1)

        self.factory.xfer = ModelEntryAddModify()
        self.call('/diacamma.accounting/modelEntryAddModify', {'SAVE': 'YES', 'journal': '2', 'designation': 'foo'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'modelEntryAddModify')

        self.factory.xfer = ModelEntryList()
        self.call('/diacamma.accounting/modelEntryList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryList')
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="modelentry"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD[1]/VALUE[@name="journal"]', "Achats")
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD[1]/VALUE[@name="designation"]', "foo")
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD[1]/VALUE[@name="total"]', "0.00€")

    def test_addline(self):
        self.factory.xfer = ModelEntryAddModify()
        self.call('/diacamma.accounting/modelEntryAddModify', {'SAVE': 'YES', 'journal': '2', 'designation': 'foo'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'modelEntryAddModify')

        self.factory.xfer = ModelLineEntryAddModify()
        self.call('/diacamma.accounting/modelLineEntryAddModify',
                  {'modelentry': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelLineEntryAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', None)
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="credit_val"]', '0.00')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="debit_val"]', '0.00')

        self.factory.xfer = ModelLineEntryAddModify()
        self.call('/diacamma.accounting/modelLineEntryAddModify',
                  {'modelentry': '1', 'code': '411'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelLineEntryAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '411')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="third"]', '0')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="credit_val"]', '0.00')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="debit_val"]', '0.00')

        self.factory.xfer = ModelLineEntryAddModify()
        self.call('/diacamma.accounting/modelLineEntryAddModify',
                  {'SAVE': 'YES', 'model': '1', 'modelentry': '1', 'code': '411', 'third': '3', 'credit_val': '19.37', 'debit_val': '0.0'}, False)

        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'modelLineEntryAddModify')

        self.factory.xfer = ModelEntryList()
        self.call('/diacamma.accounting/modelEntryList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'modelEntryList')
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="modelentry"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD[1]/VALUE[@name="journal"]', "Achats")
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD[1]/VALUE[@name="designation"]', "foo")
        self.assert_xml_equal('COMPONENTS/GRID[@name="modelentry"]/RECORD[1]/VALUE[@name="total"]', "19.37€")

    def test_selector(self):
        add_models()
        self.factory.xfer = EntryAccountModelSelector()
        self.call('/diacamma.accounting/entryAccountModelSelector', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountModelSelector')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('COMPONENTS/SELECT[@name="model"]/CASE', 2)
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="factor"]', '1.00')

        self.factory.xfer = EntryAccountModelSelector()
        self.call('/diacamma.accounting/entryAccountModelSelector', {'journal': 2}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountModelSelector')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('COMPONENTS/SELECT[@name="model"]/CASE', 1)
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="factor"]', '1.00')

    def test_insert(self):
        add_models()
        self.factory.xfer = EntryAccountModelSelector()
        self.call('/diacamma.accounting/entryAccountModelSelector', {'SAVE': 'YES', 'journal': '2', 'model': 1, 'factor': 2.50}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountModelSelector')
        self.assert_count_equal("CONTEXT/*", 2)
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")
        self.assert_attrib_equal("ACTION", "id", "diacamma.accounting/entryAccountEdit")
        self.assert_count_equal("ACTION/PARAM", 1)
        serial_entry = self.get_first_xpath("ACTION/PARAM[@name='serial_entry']").text.split('\n')
        self.assertEqual(serial_entry[0][-20:], "|1|3|48.430000|None|", serial_entry[0])
        self.assertEqual(serial_entry[1][-21:], "|2|0|-48.430000|None|", serial_entry[1])
