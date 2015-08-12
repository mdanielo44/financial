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
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.views_entries import EntryLineAccountList, EntryLineAccountListing
from diacamma.accounting.test_tools import default_compta, initial_thirds, fill_entries
from lucterios.CORE.views import StatusMenu
from base64 import b64decode
from datetime import date

class CompletedEntryTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        rmtree(get_user_dir(), True)
        fill_entries(1)

    def _goto_entrylineaccountlist(self, journal, filterlist, nb_line):
        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList', {'year':'1', 'journal':journal, 'filter':filterlist}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/HEADER', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', nb_line)

    def test_lastyear(self):
        self._goto_entrylineaccountlist(1, 0, 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[106000] 106000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', '1250.47€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[512000] 512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="debit"]', '1135.93€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry_account"]', '[531000] 531000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="debit"]', '114.45€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.link"]', '---')

    def test_buying(self):
        self._goto_entrylineaccountlist(2, 0, 6)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '2')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[602000] 602000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="debit"]', '63.94€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', 'A')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '2')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[401000 Minimum]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="credit"]', '63.94€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', 'A')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry_account"]', '[607000] 607000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="debit"]', '194.08€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.link"]', 'C')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry_account"]', '[401000 Dalton Avrel]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="credit"]', '194.08€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.link"]', 'C')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry_account"]', '[601000] 601000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="debit"]', '78.24€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry_account"]', '[401000 Maximum]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="credit"]', '78.24€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry.link"]', '---')

    def test_selling(self):
        self._goto_entrylineaccountlist(3, 0, 6)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '4')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[707000] 707000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', 'E')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '4')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[411000 Dalton Joe]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="debit"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', 'E')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.num"]', '6')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry_account"]', '[707000] 707000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="credit"]', '125.97€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.num"]', '6')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry_account"]', '[411000 Dalton William]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="debit"]', '125.97€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry_account"]', '[707000] 707000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="credit"]', '34.01€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry_account"]', '[411000 Minimum]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="debit"]', '34.01€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry.link"]', '---')

    def test_payment(self):
        self._goto_entrylineaccountlist(4, 0, 6)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '3')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[512000] 512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', '63.94€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', 'A')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '3')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[401000 Minimum]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="debit"]', '63.94€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', 'A')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry_account"]', '[531000] 531000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="credit"]', '194.08€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.link"]', 'C')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry_account"]', '[401000 Dalton Avrel]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="debit"]', '194.08€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.link"]', 'C')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.num"]', '5')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry_account"]', '[512000] 512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="debit"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.link"]', 'E')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry.num"]', '5')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry_account"]', '[411000 Dalton Joe]')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="credit"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[6]/VALUE[@name="entry.link"]', 'E')

    def test_other(self):
        self._goto_entrylineaccountlist(5, 0, 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '7')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[512000] 512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', '12.34€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '7')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[627000] 627000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="debit"]', '12.34€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', '---')

    def test_all(self):
        self._goto_entrylineaccountlist(-1, 0, 23)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 230.62€ - {[b]}Charge:{[/b]} 348.60€ = {[b]}Resultat:{[/b]} -117.98€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')  # pylint: disable=line-too-long

    def test_noclose(self):
        self._goto_entrylineaccountlist(-1, 1, 8)

    def test_close(self):
        self._goto_entrylineaccountlist(-1, 2, 15)
        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList', {'year':'1', 'journal':'-1', 'filter':'2'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/HEADER', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 15)

    def test_letter(self):
        self._goto_entrylineaccountlist(-1, 3, 12)

    def test_noletter(self):
        self._goto_entrylineaccountlist(-1, 4, 11)

    def test_summary(self):
        self.factory.xfer = StatusMenu()
        self.call('/CORE/statusMenu', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'statusMenu')
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accounting_year']", "{[center]}Exercice du 1 janvier 2015 au 31 décembre 2015 [en création]{[/center]}")
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accounting_result']", '{[center]}{[b]}Produit:{[/b]} 230.62€ - {[b]}Charge:{[/b]} 348.60€ = {[b]}Resultat:{[/b]} -117.98€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')  # pylint: disable=line-too-long
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='accountingtitle']", "{[center]}{[b]}{[u]}Financier{[/u]}{[/b]}{[/center]}")

    def test_listing(self):
        self.factory.xfer = EntryLineAccountListing()
        self.call('/diacamma.accounting/entryLineAccountListing', {'PRINT_MODE':'4', 'MODEL':7, 'year':'1', 'journal':'-1', 'filter':'0'}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'entryLineAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 29, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Liste d\'écritures"')
        self.assertEqual(content_csv[3].strip(), '"N°";"date d\'écriture";"date de pièce";"compte";"nom";"débit";"crédit";"lettrage";')
        self.assertEqual(content_csv[4].strip(), '"1";"%s";"1 février 2015";"[106000] 106000";"Report à nouveau";"";"1250.47€";"";' % formats.date_format(date.today(), "DATE_FORMAT"))
        self.assertEqual(content_csv[11].strip(), '"---";"---";"13 février 2015";"[607000] 607000";"depense 2";"194.08€";"";"C";')

        self.factory.xfer = EntryLineAccountListing()
        self.call('/diacamma.accounting/entryLineAccountListing', {'PRINT_MODE':'4', 'MODEL':7, 'year':'1', 'journal':'-1', 'filter':'1'}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'entryLineAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 14, str(content_csv))

        self.factory.xfer = EntryLineAccountListing()
        self.call('/diacamma.accounting/entryLineAccountListing', {'PRINT_MODE':'4', 'MODEL':7, 'year':'1', 'journal':'-1', 'filter':'2'}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'entryLineAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 21, str(content_csv))

        self.factory.xfer = EntryLineAccountListing()
        self.call('/diacamma.accounting/entryLineAccountListing', {'PRINT_MODE':'4', 'MODEL':7, 'year':'1', 'journal':'-1', 'filter':'3'}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'entryLineAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 18, str(content_csv))

        self.factory.xfer = EntryLineAccountListing()
        self.call('/diacamma.accounting/entryLineAccountListing', {'PRINT_MODE':'4', 'MODEL':7, 'year':'1', 'journal':'-1', 'filter':'4'}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'entryLineAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 17, str(content_csv))

        self.factory.xfer = EntryLineAccountListing()
        self.call('/diacamma.accounting/entryLineAccountListing', {'PRINT_MODE':'4', 'MODEL':7, 'year':'1', 'journal':'4', 'filter':'0'}, False)
        self.assert_observer('Core.Print', 'diacamma.accounting', 'entryLineAccountListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 12, str(content_csv))
