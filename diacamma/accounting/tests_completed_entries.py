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

from django.utils import six, formats

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir, get_user_path

from diacamma.accounting.views_entries import EntryAccountList, EntryAccountListing, \
    EntryAccountEdit, EntryAccountShow, EntryAccountClose, \
    EntryAccountCostAccounting, EntryAccountSearch
from diacamma.accounting.test_tools import default_compta, initial_thirds, fill_entries
from lucterios.CORE.views import StatusMenu
from base64 import b64decode
from datetime import date
from diacamma.accounting.views_other import CostAccountingList, \
    CostAccountingClose
from diacamma.accounting.views_reports import FiscalYearBalanceSheet,\
    FiscalYearIncomeStatement, FiscalYearLedger, FiscalYearTrialBalance
from diacamma.accounting.views_admin import FiscalYearExport
from os.path import exists


class CompletedEntryTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        rmtree(get_user_dir(), True)
        fill_entries(1)

    def _goto_entrylineaccountlist(self, journal, filterlist, nb_line):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList',
                  {'year': '1', 'journal': journal, 'filter': filterlist}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entryaccount"]/RECORD', nb_line)

    def test_lastyear(self):
        self._goto_entrylineaccountlist(1, 0, 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[106] 106' in description, description)
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[531] 531' in description, description)
        self.assertTrue('1250.38€' in description, description)
        self.assertTrue('1135.93€' in description, description)
        self.assertTrue('114.45€' in description, description)

    def test_buying(self):
        self._goto_entrylineaccountlist(2, 0, 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', 'C')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[607] 607' in description, description)
        self.assertTrue('[401 Dalton Avrel]' in description, description)
        self.assertTrue('194.08€' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="num"]', '2')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[602] 602' in description, description)
        self.assertTrue('[401 Minimum]' in description, description)
        self.assertTrue('63.94' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="description"]').text
        self.assertTrue('[601] 601' in description, description)
        self.assertTrue('[401 Maximum]' in description, description)
        self.assertTrue('78.24€' in description, description)

    def test_selling(self):
        self._goto_entrylineaccountlist(3, 0, 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '4')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', 'E')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[707] 707' in description, description)
        self.assertTrue('[411 Dalton Joe]' in description, description)
        self.assertTrue('70.64€' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="num"]', '6')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[707] 707' in description, description)
        self.assertTrue('[411 Dalton William]' in description, description)
        self.assertTrue('125.97€' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="description"]').text
        self.assertTrue('[707] 707' in description, description)
        self.assertTrue('[411 Minimum]' in description, description)
        self.assertTrue('34.01€' in description, description)

    def test_payment(self):
        self._goto_entrylineaccountlist(4, 0, 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '3')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', 'A')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[401 Minimum]' in description, description)
        self.assertTrue('63.94€' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="link"]', 'C')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[531] 531' in description, description)
        self.assertTrue('[401 Dalton Avrel]' in description, description)
        self.assertTrue('194.08€' in description, description)

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="num"]', '5')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="link"]', 'E')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="description"]').text
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[411 Dalton Joe]' in description, description)
        self.assertTrue('70.64€' in description, description)

    def test_other(self):
        self._goto_entrylineaccountlist(5, 0, 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="num"]', '7')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="link"]', '---')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[512] 512' in description, description)
        self.assertTrue('[627] 627' in description, description)
        self.assertTrue('12.34€' in description, description)

    def _check_result(self):
        return self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 230.62€ - {[b]}Charge:{[/b]} 348.60€ = {[b]}Résultat:{[/b]} -117.98€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')

    def _check_result_with_filter(self):
        return self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 34.01€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 34.01€ | {[b]}Trésorie:{[/b]} 70.64€ - {[b]}Validé:{[/b]} 70.64€{[/center]}')

    def test_all(self):
        self._goto_entrylineaccountlist(-1, 0, 11)
        self._check_result()

    def test_noclose(self):
        self._goto_entrylineaccountlist(-1, 1, 4)

    def test_close(self):
        self._goto_entrylineaccountlist(-1, 2, 7)

    def test_letter(self):
        self._goto_entrylineaccountlist(-1, 3, 6)

    def test_noletter(self):
        self._goto_entrylineaccountlist(-1, 4, 5)

    def test_summary(self):
        self.factory.xfer = StatusMenu()
        self.call('/CORE/statusMenu', {}, False)
        self.assert_observer('core.custom', 'CORE', 'statusMenu')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accounting_year']",
                              "{[center]}Exercice du 1 janvier 2015 au 31 décembre 2015 [en création]{[/center]}")
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accounting_result']",
                              '{[center]}{[b]}Produit:{[/b]} 230.62€ - {[b]}Charge:{[/b]} 348.60€ = {[b]}Résultat:{[/b]} -117.98€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accountingtitle']", "{[center]}{[u]}{[b]}Comptabilité{[/b]}{[/u]}{[/center]}")

    def test_listing(self):
        self.factory.xfer = EntryAccountListing()
        self.call('/diacamma.accounting/entryAccountListing',
                  {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 30, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste d\'écritures"')
        self.assertEqual(content_csv[3].strip(), '"N°";"date d\'écriture";"date de pièce";"compte";"nom";"débit";"crédit";"lettrage";')
        self.assertEqual(content_csv[4].strip(), '"1";"%s";"1 février 2015";"[106] 106";"Report à nouveau";"";"1250.38€";"";' %
                         formats.date_format(date.today(), "DATE_FORMAT"))
        self.assertEqual(content_csv[11].strip(), '"---";"---";"13 février 2015";"[607] 607";"depense 2";"194.08€";"";"C";')

        self.factory.xfer = EntryAccountListing()
        self.call('/diacamma.accounting/entryAccountListing',
                  {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 15, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.call('/diacamma.accounting/entryAccountListing',
                  {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '2'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 22, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.call('/diacamma.accounting/entryAccountListing',
                  {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '3'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 19, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.call('/diacamma.accounting/entryAccountListing',
                  {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '4'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(
            six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 18, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.call('/diacamma.accounting/entryAccountListing',
                  {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '4', 'filter': '0'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(
            six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 13, str(content_csv))

    def test_search(self):
        self.factory.xfer = EntryAccountSearch()
        self.call('/diacamma.accounting/entryAccountSearch',
                  {'year': '1', 'journal': '-1', 'filter': '0', 'CRITERIA': 'year||8||1//entrylineaccount_set.account.code||6||7'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountSearch')
        self.assert_count_equal('COMPONENTS/*', 23)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)

    def test_listing_search(self):
        self.factory.xfer = EntryAccountListing()
        self.call('/diacamma.accounting/entryAccountListing',
                  {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '0', 'CRITERIA': 'year||8||1//entrylineaccount_set.account.code||6||7'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 13, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste d\'écritures"')
        self.assertEqual(content_csv[3].strip(), '"N°";"date d\'écriture";"date de pièce";"compte";"nom";"débit";"crédit";"lettrage";')
        self.assertEqual(content_csv[4].strip(), '"4";"%s";"21 février 2015";"[707] 707";"vente 1";"";"70.64€";"E";' % formats.date_format(date.today(), "DATE_FORMAT"))
        self.assertEqual(content_csv[8].strip(), '"---";"---";"24 février 2015";"[707] 707";"vente 3";"";"34.01€";"";')

    def test_costaccounting(self):
        self.factory.xfer = EntryAccountEdit()
        self.call('/diacamma.accounting/entryAccountEdit',
                  {'year': '1', 'journal': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='costaccounting']", '0')
        self.assert_count_equal("COMPONENTS/SELECT[@name='costaccounting']/CASE", 2)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryAccountShow()
        self.call('/diacamma.accounting/entryAccountShow',
                  {'year': '1', 'journal': '2', 'entryaccount': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('COMPONENTS/*', 19)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='designation']", 'depense 1')
        self.assert_xml_equal("COMPONENTS/SELECT[@name='costaccounting']", '2')
        self.assert_count_equal("COMPONENTS/SELECT[@name='costaccounting']/CASE", 2)
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.factory.xfer = EntryAccountShow()
        self.call('/diacamma.accounting/entryAccountShow',
                  {'year': '1', 'journal': '2', 'entryaccount': '11'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='designation']", 'Frais bancaire')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='costaccounting']", 'close')
        self.assert_count_equal('ACTIONS/ACTION', 1)

    def test_costaccounting_list(self):
        self.factory.xfer = CostAccountingList()
        self.call('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('COMPONENTS/*', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="name"]', 'open')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="description"]', 'Open cost')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="total_revenue"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="total_expense"]', '258.02€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="status"]', 'ouverte')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="is_default"]', '1')

        self.factory.xfer = CostAccountingClose()
        self.call('/diacamma.accounting/costAccountingClose',
                  {'costaccounting': 2}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'costAccountingClose')
        self.assert_xml_equal('EXCEPTION/MESSAGE', 'Cette comptabilité a des écritures non validées!')

        self.factory.xfer = EntryAccountClose()
        self.call('/diacamma.accounting/entryAccountClose',
                  {'CONFIRME': 'YES', 'year': '1', 'journal': '2', "entryaccount": "4"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = CostAccountingClose()
        self.call('/diacamma.accounting/costAccountingClose',
                  {'CONFIRME': 'YES', 'costaccounting': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingClose')

        self.factory.xfer = CostAccountingList()
        self.call('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('COMPONENTS/*', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD', 0)

        self.factory.xfer = CostAccountingList()
        self.call('/diacamma.accounting/costAccountingList', {'all_cost': True}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('COMPONENTS/*', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD', 2)

    def test_costaccounting_change(self):
        self.factory.xfer = CostAccountingList()
        self.call('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="name"]', 'open')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="total_revenue"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="total_expense"]', '258.02€')

        self.factory.xfer = EntryAccountCostAccounting()
        self.call('/diacamma.accounting/entryAccountCostAccounting',
                  {'entryaccount': '4;6;9'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountCostAccounting')

        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal("COMPONENTS/SELECT[@name='costaccounting']", '0')
        self.assert_count_equal("COMPONENTS/SELECT[@name='costaccounting']/CASE", 2)

        self.factory.xfer = EntryAccountCostAccounting()
        self.call('/diacamma.accounting/entryAccountCostAccounting',
                  {"SAVE": "YES", 'entryaccount': '4;6;9', 'costaccounting': '2'}, False)  # -78.24 / +125.97

        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self.factory.xfer = CostAccountingList()
        self.call('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="name"]', 'open')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="total_revenue"]', '196.61€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="total_expense"]', '336.26€')

        self.factory.xfer = EntryAccountCostAccounting()
        self.call('/diacamma.accounting/entryAccountCostAccounting',
                  {"SAVE": "YES", 'entryaccount': '4;6;9', 'costaccounting': '0'}, False)  # - -194.08 / 0

        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self.factory.xfer = CostAccountingList()
        self.call('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="name"]', 'open')
        self.assert_xml_equal('COMPONENTS/GRID[@name="costaccounting"]/RECORD[1]/VALUE[@name="total_revenue"]', '70.64€')

    def test_fiscalyear_balancesheet(self):
        self.factory.xfer = FiscalYearBalanceSheet()
        self.call('/diacamma.accounting/fiscalYearBalanceSheet', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearBalanceSheet')
        self._check_result()

    def test_fiscalyear_balancesheet_filter(self):
        self.factory.xfer = FiscalYearBalanceSheet()
        self.call('/diacamma.accounting/fiscalYearBalanceSheet', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearBalanceSheet')
        self._check_result_with_filter()

    def test_fiscalyear_incomestatement(self):
        self.factory.xfer = FiscalYearIncomeStatement()
        self.call('/diacamma.accounting/fiscalYearIncomeStatement', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearIncomeStatement')
        self._check_result()

    def test_fiscalyear_incomestatement_filter(self):
        self.factory.xfer = FiscalYearIncomeStatement()
        self.call('/diacamma.accounting/fiscalYearIncomeStatement', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearIncomeStatement')
        self._check_result_with_filter()

    def test_fiscalyear_ledger(self):
        self.factory.xfer = FiscalYearLedger()
        self.call('/diacamma.accounting/fiscalYearLedger', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearLedger')
        self._check_result()

    def test_fiscalyear_ledger_filter(self):
        self.factory.xfer = FiscalYearLedger()
        self.call('/diacamma.accounting/fiscalYearLedger', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearLedger')
        self._check_result_with_filter()

    def test_fiscalyear_trialbalance(self):
        self.factory.xfer = FiscalYearTrialBalance()
        self.call('/diacamma.accounting/fiscalYearTrialBalance', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self._check_result()

    def test_fiscalyear_trialbalance_filter(self):
        self.factory.xfer = FiscalYearTrialBalance()
        self.call('/diacamma.accounting/fiscalYearTrialBalance', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self._check_result_with_filter()

    def test_export(self):
        self.assertFalse(
            exists(get_user_path('accounting', 'fiscalyear_export_1.xml')))
        self.factory.xfer = FiscalYearExport()
        self.call('/diacamma.accounting/fiscalYearExport', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearExport')
        self.assertTrue(exists(get_user_path('accounting', 'fiscalyear_export_1.xml')))
