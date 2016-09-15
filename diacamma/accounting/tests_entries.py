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
from datetime import date

from django.utils import formats

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.views_entries import EntryAccountList, \
    EntryAccountEdit, EntryAccountAfterSave, EntryLineAccountAdd, \
    EntryLineAccountEdit, EntryAccountValidate, EntryAccountClose, \
    EntryAccountReverse, EntryAccountCreateLinked, EntryAccountLink, \
    EntryAccountDel, EntryAccountOpenFromLine, EntryAccountShow, \
    EntryLineAccountDel, EntryAccountUnlock
from diacamma.accounting.test_tools import default_compta, initial_thirds
from diacamma.accounting.models import EntryAccount


class EntryTest(LucteriosTest):

    def setUp(self):
        initial_thirds()
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        default_compta()
        rmtree(get_user_dir(), True)

    def test_empty_list(self):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='year']", '1')
        self.assert_count_equal("COMPONENTS/SELECT[@name='year']/CASE", 1)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='journal']", '4')
        self.assert_count_equal("COMPONENTS/SELECT[@name='journal']/CASE", 6)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='filter']", '1')
        self.assert_count_equal("COMPONENTS/SELECT[@name='filter']/CASE", 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

    def test_add_entry(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='journal']", '2')
        self.assert_xml_equal("COMPONENTS/DATE[@name='date_value']", '2015-12-31')
        self.assert_xml_equal("COMPONENTS/EDIT[@name='designation']", None)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='costaccounting']", '0')
        self.assert_count_equal("COMPONENTS/SELECT[@name='costaccounting']/CASE", 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_attrib_equal("ACTION", "id", "diacamma.accounting/entryAccountAfterSave")
        self.assert_count_equal("ACTION/PARAM", 1)
        self.assert_xml_equal("ACTION/PARAM[@name='entryaccount']", "1")
        self.assert_count_equal("CONTEXT/*", 4)
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")
        self.assert_xml_equal("CONTEXT/PARAM[@name='date_value']", "2015-02-13")
        self.assert_xml_equal("CONTEXT/PARAM[@name='designation']", "un plein cadie")

        self.factory.xfer = EntryAccountAfterSave()
        self.call('/diacamma.accounting/entryAccountAfterSave', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                 'date_value': '2015-02-13', 'designation': 'un plein cadie', 'entryaccount': "1"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountAfterSave')
        self.assert_attrib_equal("ACTION", "id", "diacamma.accounting/entryAccountEdit")
        self.assert_count_equal("ACTION/PARAM", 0)
        self.assert_count_equal("CONTEXT/*", 3)
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")

    def test_add_entry_bad_date(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2017-04-20', 'designation': 'Truc'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_xml_equal("ACTION/PARAM[@name='entryaccount']", "1")

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='journal']", '2')
        self.assert_xml_equal("COMPONENTS/DATE[@name='date_value']", '2015-12-31')
        self.assert_xml_equal("COMPONENTS/EDIT[@name='designation']", 'Truc')
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2010-04-20', 'designation': 'Machin'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_xml_equal("ACTION/PARAM[@name='entryaccount']", "2")

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='journal']", '2')
        self.assert_xml_equal("COMPONENTS/DATE[@name='date_value']", '2015-01-01')
        self.assert_xml_equal("COMPONENTS/EDIT[@name='designation']", 'Machin')
        self.assert_count_equal('ACTIONS/ACTION', 2)

    def test_add_line_third(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)

        self.assert_xml_equal("COMPONENTS/SELECT[@name='journal']", '2')
        self.assert_xml_equal("COMPONENTS/DATE[@name='date_value']", '2015-02-13')
        self.assert_xml_equal("COMPONENTS/EDIT[@name='designation']", 'un plein cadie')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 0)
        self.assert_xml_equal("COMPONENTS/EDIT[@name='num_cpt_txt']", None)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='num_cpt']", 'NULL')
        self.assert_count_equal("COMPONENTS/SELECT[@name='num_cpt']/CASE", 0)
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='debit_val']", '0.00')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='credit_val']", '0.00')
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'num_cpt_txt': '401'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 24)

        self.assert_xml_equal("COMPONENTS/EDIT[@name='num_cpt_txt']", '401')
        self.assert_xml_equal("COMPONENTS/SELECT[@name='num_cpt']", '4')
        self.assert_count_equal("COMPONENTS/SELECT[@name='num_cpt']/CASE", 1)
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='debit_val']", '0.00')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='credit_val']", '0.00')
        self.assert_xml_equal("COMPONENTS/SELECT[@name='third']", '0')
        self.assert_count_equal("COMPONENTS/SELECT[@name='third']/CASE", 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryLineAccountAdd()
        self.call('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '2', 'entryaccount': '1', 'num_cpt_txt': '401',
                                                               'num_cpt': '4', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assert_count_equal("CONTEXT/*", 3)
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)

        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="entry_account"]', '[401] 401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="debit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="credit"]', '{[font color="green"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="reference"]', '---')
        self.assert_count_equal('ACTIONS/ACTION', 2)

    def test_add_line_revenue(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|None|", 'num_cpt_txt': '60'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 24)

        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 1)
        self.assert_xml_equal("COMPONENTS/EDIT[@name='num_cpt_txt']", '60')
        self.assert_xml_equal("COMPONENTS/SELECT[@name='num_cpt']", '11')
        self.assert_count_equal("COMPONENTS/SELECT[@name='num_cpt']/CASE", 4)
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='debit_val']", '152.34')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='credit_val']", '0.00')
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryLineAccountAdd()
        self.call('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|None|",
                                                               'num_cpt_txt': '60', 'num_cpt': '12', 'debit_val': '152.34', 'credit_val': '0.0'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assert_count_equal("CONTEXT/*", 3)
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|None|\n-2|12|0|152.340000|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)

        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="entry_account"]', '[401] 401')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="debit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="credit"]', '{[font color="green"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="reference"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="entry_account"]', '[602] 602')

        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="debit"]',
                              '{[font color="blue"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="credit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="reference"]', '---')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_attrib_equal("ACTIONS/ACTION[1]", "id", "diacamma.accounting/entryAccountValidate")

    def test_change_line_third(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryLineAccountEdit()
        self.call('/diacamma.accounting/entryLineAccountEdit', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                                'serial_entry': "-1|4|0|152.340000|None|\n-2|12|0|152.340000|None|", 'entrylineaccount_serial': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryLineAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 9)

        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='account']", '[401] 401')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='debit_val']", '0.00')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='credit_val']", '152.34')
        self.assert_xml_equal("COMPONENTS/SELECT[@name='third']", '0')
        self.assert_count_equal("COMPONENTS/SELECT[@name='third']/CASE", 5)
        self.assert_attrib_equal("ACTIONS/ACTION[1]", "id", "diacamma.accounting/entryLineAccountAdd")
        self.assert_count_equal("ACTIONS/ACTION[1]/PARAM", 1)
        self.assert_xml_equal("ACTIONS/ACTION[1]/PARAM[@name='num_cpt']", '4')

        self.factory.xfer = EntryLineAccountAdd()
        self.call('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                               'serial_entry': "-1|4|0|152.340000|None|\n-2|12|0|152.340000|None|", 'debit_val': '0.0',
                                                               'credit_val': '152.34', 'entrylineaccount_serial': '-1', 'third': '3', 'num_cpt': '4'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assert_count_equal("CONTEXT/*", 3)
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|None|\n-3|4|3|152.340000|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)

        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="entry_account"]', '[602] 602')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="debit"]', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="credit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="reference"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="entry_account"]', '[401 Luke Lucky]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="debit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="credit"]', '{[font color="green"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="reference"]', '---')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_attrib_equal("ACTIONS/ACTION[1]", "id", "diacamma.accounting/entryAccountValidate")

        self.factory.xfer = EntryLineAccountEdit()
        self.call('/diacamma.accounting/entryLineAccountEdit', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                                'serial_entry': "-1|4|3|152.340000|None|\n-2|12|0|152.340000|None|", 'entrylineaccount_serial': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryLineAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 9)

        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='account']", '[401] 401')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='debit_val']", '0.00')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='credit_val']", '152.34')
        self.assert_xml_equal("COMPONENTS/SELECT[@name='third']", '3')
        self.assert_count_equal("COMPONENTS/SELECT[@name='third']/CASE", 5)
        self.assert_attrib_equal("ACTIONS/ACTION[1]", "id", "diacamma.accounting/entryLineAccountAdd")
        self.assert_count_equal("ACTIONS/ACTION[1]/PARAM", 1)
        self.assert_xml_equal("ACTIONS/ACTION[1]/PARAM[@name='num_cpt']", '4')

    def test_valid_entry(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|None|\n-3|4|3|152.340000|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_entry"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_value"]', '13 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('un plein cadie' in description, description)
        self.assertTrue('[602] 602' in description, description)
        self.assertTrue('[401 Luke Lucky]' in description, description)
        self.assertTrue('152.34€' in description, description)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 152.34€ = {[b]}Résultat:{[/b]} -152.34€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountOpenFromLine()
        self.call('/diacamma.accounting/entryAccountOpenFromLine',
                  {'year': '1', 'journal': '2', 'filter': '0', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountOpenFromLine')
        self.assert_attrib_equal("ACTION", "id", "diacamma.accounting/entryAccountEdit")
        self.assert_count_equal("ACTION/PARAM", 0)
        self.assert_count_equal("CONTEXT/*", 4)
        self.assert_xml_equal("CONTEXT/PARAM[@name='filter']", "0")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")

        self.factory.xfer = EntryAccountClose()
        self.call('/diacamma.accounting/entryAccountClose',
                  {'CONFIRME': 'YES', 'year': '1', 'journal': '2', "entryaccount": "1"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_entry"]',
                              formats.date_format(date.today(), "DATE_FORMAT"))
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_value"]', '13 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('un plein cadie' in description, description)
        self.assertTrue('[602] 602' in description, description)
        self.assertTrue('[401 Luke Lucky]' in description, description)
        self.assertTrue('152.34€' in description, description)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 152.34€ = {[b]}Résultat:{[/b]} -152.34€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountOpenFromLine()
        self.call('/diacamma.accounting/entryAccountOpenFromLine',
                  {'year': '1', 'journal': '2', 'filter': '0', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountOpenFromLine')
        self.assert_attrib_equal("ACTION", "id", "diacamma.accounting/entryAccountShow")
        self.assert_count_equal("ACTION/PARAM", 0)
        self.assert_count_equal("CONTEXT/*", 4)
        self.assert_xml_equal("CONTEXT/PARAM[@name='filter']", "0")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")

        self.factory.xfer = EntryAccountShow()
        self.call('/diacamma.accounting/entryAccountShow',
                  {'year': '1', 'journal': '2', 'filter': '0', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='num']", '1')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='journal']", 'Achats')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='date_entry']", formats.date_format(date.today(), "DATE_FORMAT"))
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='date_value']", '13 février 2015')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='designation']", 'un plein cadie')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 2)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_attrib_equal("ACTIONS/ACTION[2]", "id", "diacamma.accounting/entryAccountCreateLinked")

    def test_inverse_entry(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|None|\n-3|4|3|152.340000|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)

        self.assert_count_equal('ACTIONS/ACTION', 5)
        self.assert_attrib_equal("ACTIONS/ACTION[2]", "id", "diacamma.accounting/entryAccountClose")
        self.assert_attrib_equal("ACTIONS/ACTION[3]", "id", "diacamma.accounting/entryAccountCreateLinked")
        self.assert_attrib_equal("ACTIONS/ACTION[4]", "id", "diacamma.accounting/entryAccountReverse")

        self.factory.xfer = EntryAccountReverse()
        self.call('/diacamma.accounting/entryAccountReverse',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountReverse')

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 24)

        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='asset_warning']", "{[center]}{[i]}écriture d'un avoir{[/i]}{[/center]}")

    def test_valid_payment(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|None|\n-3|4|3|152.340000|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountCreateLinked()
        self.call('/diacamma.accounting/entryAccountCreateLinked',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCreateLinked')
        self.assert_attrib_equal("ACTION", "id", "diacamma.accounting/entryAccountEdit")
        self.assert_count_equal("ACTION/PARAM", 4)
        self.assert_xml_equal("ACTION/PARAM[@name='entryaccount']", "2")
        self.assert_xml_equal("ACTION/PARAM[@name='serial_entry']", "|4|3|-152.340000|None", (-22, -1))
        self.assert_xml_equal("ACTION/PARAM[@name='num_cpt_txt']", "5")
        self.assert_xml_equal("ACTION/PARAM[@name='journal']", "4")
        self.assert_count_equal("CONTEXT/*", 3)
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '4', 'entryaccount': '2',
                                                            'serial_entry': "-3|4|3|-152.340000|None|", 'num_cpt_txt': '5'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 27)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='journal']", '4')
        self.assert_xml_equal("COMPONENTS/DATE[@name='date_value']", '2015-12-31')
        self.assert_xml_equal("COMPONENTS/EDIT[@name='designation']", 'règlement de un plein cadie')

        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 1)
        self.assert_xml_equal("COMPONENTS/EDIT[@name='num_cpt_txt']", '5')
        self.assert_xml_equal("COMPONENTS/SELECT[@name='num_cpt']", '2')
        self.assert_count_equal("COMPONENTS/SELECT[@name='num_cpt']/CASE", 2)
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='debit_val']", '0.00')
        self.assert_xml_equal("COMPONENTS/FLOAT[@name='credit_val']", '152.34')
        self.assert_xml_equal("COMPONENTS/EDIT[@name='reference']", None)

        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="entry_account"]', '[401 Luke Lucky]')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="debit"]', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="credit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="reference"]', '---')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount_link"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount_link"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount_link"]/RECORD[1]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount_link"]/RECORD[1]/VALUE[@name="date_entry"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount_link"]/RECORD[1]/VALUE[@name="date_value"]', '13 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount_link"]/RECORD[1]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount_link"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('un plein cadie' in description, description)
        self.assertTrue('[602] 602' in description, description)
        self.assertTrue('[401 Luke Lucky]' in description, description)
        self.assertTrue('152.34€' in description, description)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '2', 'entryaccount': '2',
                                                            'serial_entry': "-3|4|3|-152.340000|None|\n-4|2|0|-152.340000|Ch N°12345|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 26)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="entry_account"]', '[401 Luke Lucky]')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="debit"]', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="credit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[1]/VALUE[@name="reference"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="entry_account"]', '[512] 512')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="debit"]', '{[font color="green"]}{[/font]}')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="credit"]', '{[font color="green"]}152.34€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD[2]/VALUE[@name="reference"]', 'Ch N°12345')
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '2', 'serial_entry': "-3|4|3|-152.340000|None||\n-4|2|0|-152.340000|Ch N°12345|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 2)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_entry"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_value"]', '13 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('un plein cadie' in description, description)
        self.assertTrue('[602] 602' in description, description)
        self.assertTrue('[401 Luke Lucky]' in description, description)
        self.assertTrue('152.34€' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="date_entry"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="date_value"]', '31 décembre 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('règlement de un plein cadie' in description, description)
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[401 Luke Lucky]' in description, description)
        self.assertTrue('152.34€' in description, description)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 152.34€ = {[b]}Résultat:{[/b]} -152.34€ | {[b]}Trésorie:{[/b]} -152.34€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

    def test_valid_payment_canceled(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|None|\n-3|4|3|152.340000|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.assertEqual(1, EntryAccount.objects.all().count())

        self.factory.xfer = EntryAccountCreateLinked()
        self.call('/diacamma.accounting/entryAccountCreateLinked',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCreateLinked')
        self.assert_attrib_equal("ACTION", "id", "diacamma.accounting/entryAccountEdit")
        self.assert_count_equal("ACTION/PARAM", 4)
        self.assert_xml_equal("ACTION/PARAM[@name='serial_entry']", "|4|3|-152.340000|None", (-22, -1))
        self.assert_count_equal("CONTEXT/*", 3)

        self.assertEqual(2, EntryAccount.objects.all().count())

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '4', 'entryaccount': '2',
                                                            'serial_entry': "-3|4|3|-152.340000|None|", 'num_cpt_txt': '5'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 27)

        self.factory.xfer = EntryAccountUnlock()
        self.call('/diacamma.accounting/entryAccountUnlock', {'year': '1', 'journal': '4', 'entryaccount': '2',
                                                              'serial_entry': "-3|4|3|-152.340000|None|", 'num_cpt_txt': '5'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountUnlock')

        self.assertEqual(1, EntryAccount.objects.all().count())

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_entry"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_value"]', '13 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('un plein cadie' in description, description)
        self.assertTrue('[602] 602' in description, description)
        self.assertTrue('[401 Luke Lucky]' in description, description)
        self.assertTrue('152.34€' in description, description)

    def test_link_unlink_entries(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-04-27', 'designation': 'Une belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-6|9|0|364.91|None|\n-7|1|5|364.91|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '4',
                                                            'date_value': '2015-05-03', 'designation': 'Règlement de belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '4', 'entryaccount': '2', 'serial_entry': "-9|1|5|-364.91|None|\n-8|2|0|364.91|BP N°987654|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_entry"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="date_value"]', '27 avril 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('Une belle facture' in description, description)
        self.assertTrue('[706] 706' in description, description)
        self.assertTrue('[411 Dalton William]' in description, description)
        self.assertTrue('364.91€' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="date_entry"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="date_value"]', '3 mai 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('Règlement de belle facture' in description, description)
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[411 Dalton William]' in description, description)
        self.assertTrue('364.91€' in description, description)
        self.assertTrue('BP N°987654' in description, description)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 364.91€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 364.91€ | {[b]}Trésorie:{[/b]} 364.91€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountLink()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '-1', 'filter': '0', 'entryaccount': '1;2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', 'A')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', 'A')

        self.factory.xfer = EntryAccountLink()
        self.call('/diacamma.accounting/entryAccountLink',
                  {'CONFIRME': 'YES', 'year': '1', 'journal': '-1', 'filter': '0', 'entryaccount': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountLink')
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', '---')

    def test_delete_lineentry(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-04-27', 'designation': 'Une belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-6|9|0|364.91|None|\n-7|1|5|364.91|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 2)
        self.assert_count_equal('ACTIONS/ACTION', 5)

        self.factory.xfer = EntryLineAccountDel()
        self.call('/diacamma.accounting/entryLineAccountDel', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                               'serial_entry': "1|9|0|364.91|None|\n2|1|5|364.91|None|", "entrylineaccount_serial": '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountDel')
        self.assert_attrib_equal(
            "ACTION", "id", "diacamma.accounting/entryAccountEdit")
        self.assert_count_equal("ACTION/PARAM", 1)
        self.assert_xml_equal("ACTION/PARAM[@name='serial_entry']", "1|9|0|364.910000|None|")
        self.assert_count_equal("CONTEXT/*", 3)
        self.assert_xml_equal("CONTEXT/PARAM[@name='entryaccount']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='year']", "1")
        self.assert_xml_equal("CONTEXT/PARAM[@name='journal']", "2")

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', "entrylineaccount_serial": '2', 'serial_entry': "1|9|0|364.91|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 23)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount_serial"]/RECORD', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)

    def test_delete_entries(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                            'date_value': '2015-04-27', 'designation': 'Une belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-6|9|0|364.91|None|\n-7|1|5|364.91|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '4',
                                                            'date_value': '2015-05-03', 'designation': 'Règlement de belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.call('/diacamma.accounting/entryAccountValidate',
                  {'year': '1', 'journal': '4', 'entryaccount': '2', 'serial_entry': "-9|1|5|-364.91|None|\n-8|2|0|364.91|BP N°987654|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountLink()
        self.call('/diacamma.accounting/entryAccountLink',
                  {'year': '1', 'journal': '-1', 'filter': '0', 'entryaccount': '1;2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountLink')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[706] 706' in description, description)
        self.assertTrue('[411 Dalton William]' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[411 Dalton William]' in description, description)

        self.factory.xfer = EntryAccountDel()
        self.call('/diacamma.accounting/entryAccountDel',
                  {'CONFIRME': 'YES', 'year': '1', 'journal': '-1', 'filter': '0', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountDel')

        self.factory.xfer = EntryAccountClose()
        self.call('/diacamma.accounting/entryAccountClose',
                  {'CONFIRME': 'YES', 'year': '1', 'journal': '-1', 'filter': '0', "entryaccount": "2"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('Règlement de belle facture' in description, description)
        self.assertTrue('BP N°987654' in description, description)
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[411 Dalton William]' in description, description)
        self.assertTrue('364.91€' in description, description)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 364.91€ - {[b]}Validé:{[/b]} 364.91€{[/center]}')

        self.factory.xfer = EntryAccountDel()
        self.call('/diacamma.accounting/entryAccountDel',
                  {'year': '1', 'journal': '-1', 'filter': '0', 'entryaccount': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryAccountDel')
        self.assert_xml_equal('EXCEPTION/MESSAGE', 'écriture validée!')

    def test_buyingselling_in_report(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '1',
                                                            'date_value': '2015-03-21', 'designation': 'mauvais report'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryLineAccountAdd()
        self.call('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '1', 'entryaccount': '1', 'num_cpt_txt': '70',
                                                               'num_cpt': '9', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Ce type d'écriture n'est pas permis dans ce journal")

        self.factory.xfer = EntryLineAccountAdd()
        self.call('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '1', 'entryaccount': '1', 'num_cpt_txt': '60',
                                                               'num_cpt': '13', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Ce type d'écriture n'est pas permis dans ce journal")

        self.factory.xfer = EntryLineAccountAdd()
        self.call('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '1', 'entryaccount': '1', 'num_cpt_txt': '401',
                                                               'num_cpt': '4', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
