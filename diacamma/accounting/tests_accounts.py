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

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.test_tools import initial_thirds, default_compta, fill_entries,\
    set_accounting_system
from diacamma.accounting.views_accounts import ChartsAccountList, \
     ChartsAccountDel, ChartsAccountShow, ChartsAccountAddModify

class ChartsAccountTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        set_accounting_system()
        initial_thirds()
        default_compta()
        fill_entries(1)
        rmtree(get_user_dir(), True)

    def test_all(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 15)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 230.62€ - {[b]}Charge:{[/b]} 348.60€ = {[b]}Resultat:{[/b]} -117.98€ | {[b]}Trésorie:{[/b]} 1050.66€ - {[b]}Validé:{[/b]} 1244.74€{[/center]}')  # pylint: disable=line-too-long

    def test_asset(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'0'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 159.98€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="code"]', '512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="name"]', '512000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="last_year_total"]', '{[font color="blue"]}Débit: 1135.93€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 1130.29€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_validated"]', '{[font color="blue"]}Débit: 1130.29€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="code"]', '531000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="name"]', '531000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="last_year_total"]', '{[font color="blue"]}Débit: 114.45€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 79.63€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_validated"]', '{[font color="blue"]}Débit: 114.45€{[/font]}')

    def test_liability(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 78.24€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')

    def test_equity(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'2'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '106000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '106000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 1250.47€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 1250.47€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 1250.47€{[/font]}')

    def test_revenue(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'3'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="code"]', '707000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_total"]', '{[font color="green"]}Crédit: 230.62€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[3]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 70.64€{[/font]}')

    def test_expense(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'4'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="code"]', '601000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="name"]', '601000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 78.24€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[1]/VALUE[@name="current_validated"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="code"]', '602000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="name"]', '602000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="last_year_total"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_total"]', '{[font color="blue"]}Débit: 63.94€{[/font]}')
        self.assert_xml_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD[2]/VALUE[@name="current_validated"]', '{[font color="blue"]}Débit: 63.94€{[/font]}')

    def test_contraaccounts(self):
        self.factory.xfer = ChartsAccountList()
        self.call('/diacamma.accounting/chartsAccountList', {'year':'1', 'type_of_account':'5'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="chartsaccount"]/RECORD', 0)

    def test_show(self):
        self.factory.xfer = ChartsAccountShow()
        self.call('/diacamma.accounting/chartsAccountShow', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountShow')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="code"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/HEADER', 7)
        self.assert_count_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '4')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_value"]', '21 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.designation"]', 'vente 1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', '70.64€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', 'E')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_value"]', '21 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.designation"]', 'vente 2')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="credit"]', '125.97€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', '---')

        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.date_value"]', '24 février 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.designation"]', 'vente 3')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="credit"]', '34.01€')
        self.assert_xml_equal('COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.link"]', '---')

    def test_delete(self):
        self.factory.xfer = ChartsAccountDel()
        self.call('/diacamma.accounting/chartsAccountDel', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'5', 'chartsaccount':'10'}, False)
        self.assert_observer('CORE.Exception', 'diacamma.accounting', 'chartsAccountDel')
        self.assert_xml_equal('EXCEPTION/MESSAGE', "Impossible de supprimer cet enregistrement: il est associé avec d'autres sous-enregistrements")

        self.factory.xfer = ChartsAccountDel()
        self.call('/diacamma.accounting/chartsAccountDel', {'CONFIRME':'YES', 'year':'1', 'type_of_account':'5', 'chartsaccount':'9'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'chartsAccountDel')

    def test_add(self):
        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', None)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', '---')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'code':'2301'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '2301')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', 'Immobilisations en cours')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Actif')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'code':'3015'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '3015!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', '---')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'code':'abcd'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', 'abcd!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', '---')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

    def test_modify(self):
        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '707000')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'7061'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '7061')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'3015'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '3015!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'abcd'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', 'abcd!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Code invalide!{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.call('/diacamma.accounting/chartsAccountAddModify', {'year':'1', 'type_of_account':'-1', 'chartsaccount':'10', 'code':'6125'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', '6125!')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', '707000')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_of_account"]', 'Produit')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="error_code"]', "{[center]}{[font color='red']}Changement non permis!{[/font]}{[/center]}")
