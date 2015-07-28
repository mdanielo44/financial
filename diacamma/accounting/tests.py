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
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from shutil import rmtree

from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir
from lucterios.contacts.tests_contacts import change_ourdetail
from lucterios.contacts.models import Individual, LegalEntity, AbstractContact

from diacamma.accounting.views import ThirdList, ThirdAdd, ThirdSave, ThirdShow, \
    AccountThirdAddModify, AccountThirdDel
from diacamma.accounting.models import Third, AccountThird
from diacamma.accounting.views_admin import Configuration, JournalAddModify, \
    JournalDel, FiscalYearAddModify, FiscalYearActive
from datetime import date, timedelta

def create_individual(firstname, lastname):
    empty_contact = Individual()
    empty_contact.firstname = firstname
    empty_contact.lastname = lastname
    empty_contact.address = "rue de la liberté"
    empty_contact.postal_code = "97250"
    empty_contact.city = "LE PRECHEUR"
    empty_contact.country = "MARTINIQUE"
    empty_contact.tel2 = "02-78-45-12-95"
    empty_contact.email = "%s.%s@worldcompany.com" % (firstname, lastname)
    empty_contact.save()
    return empty_contact

def change_legal(name):
    ourdetails = LegalEntity()
    ourdetails.name = name
    ourdetails.address = "Place des cocotiers"
    ourdetails.postal_code = "97200"
    ourdetails.city = "FORT DE FRANCE"
    ourdetails.country = "MARTINIQUE"
    ourdetails.tel1 = "01-23-45-67-89"
    ourdetails.email = "%s@worldcompany.com" % name
    ourdetails.save()

def initial_contacts():
    change_ourdetail()  # contact 1
    create_individual('Avrel', 'Dalton')  # contact 2
    create_individual('William', 'Dalton')  # contact 3
    create_individual('Jack', 'Dalton')  # contact 4
    create_individual('Joe', 'Dalton')  # contact 5
    create_individual('Lucky', 'Luke')  # contact 6
    change_legal("Minimum")  # contact 7
    change_legal("Maximum")  # contact 8

def create_third(abstractids, codes=None):
    for abstractid in abstractids:
        new_third = Third.objects.create(contact=AbstractContact.objects.get(id=abstractid), status=0)  # pylint: disable=no-member
        if codes is not None:
            for code in codes:
                AccountThird.objects.create(third=new_third, code=code)  # pylint: disable=no-member

class ThirdTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        initial_contacts()
        rmtree(get_user_dir(), True)

    def test_add_abstract(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdAdd()
        self.call('/diacamma.accounting/thirdAdd', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal('COMPONENTS/SELECT[@name="modelname"]', 'contacts.AbstractContact', (2, 0, 3, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="modelname"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="abstractcontact"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="abstractcontact"]/RECORD', 8)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave', {'pkname':'abstractcontact', 'abstractcontact':5}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton Joe')

    def test_add_legalentity(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdAdd()
        self.call('/diacamma.accounting/thirdAdd', {'modelname':'contacts.LegalEntity'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal('COMPONENTS/SELECT[@name="modelname"]', 'contacts.LegalEntity', (2, 0, 3, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="legalentity"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="legalentity"]/RECORD', 3)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave', {'pkname':'legalentity', 'legalentity':7}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Minimum')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third":1}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="contact"]', 'Minimum')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'extension', 'lucterios.contacts')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'action', 'legalEntityShow')
        self.assert_xml_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION/PARAM[@name="legalentity"]', '7')

    def test_add_individual(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdAdd()
        self.call('/diacamma.accounting/thirdAdd', {'modelname':'contacts.Individual'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdAdd')
        self.assert_comp_equal('COMPONENTS/SELECT[@name="modelname"]', 'contacts.Individual', (2, 0, 3, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="individual"]/RECORD', 5)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave', {'pkname':'individual', 'individual':3}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton William')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third":1}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="contact"]', 'Dalton William')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'extension', 'lucterios.contacts')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION', 'action', 'individualShow')
        self.assert_xml_equal('COMPONENTS/BUTTON[@name="show"]/ACTIONS/ACTION/PARAM[@name="individual"]', '3')

    def test_check_double(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 0)

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave', {'pkname':'abstractcontact', 'abstractcontact':5}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave', {'pkname':'abstractcontact', 'abstractcontact':5}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdSave()
        self.call('/diacamma.accounting/thirdSave', {'pkname':'abstractcontact', 'abstractcontact':5}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'thirdSave')
        self.assert_attrib_equal('ACTION', 'action', 'thirdShow')
        self.assert_xml_equal('ACTION/PARAM[@name="third"]', '1')

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 1)

    def test_show(self):
        create_third([3])
        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third":1}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/TAB', 1)
        self.assert_count_equal('COMPONENTS/*', 16 + 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="contact"]', 'Dalton William')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'Actif')
        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER[@name="code"]', "code")
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER[@name="total_txt"]', "total")
        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD', 0)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '0.00€')

        self.factory.xfer = AccountThirdAddModify()
        self.call('/diacamma.accounting/accountThirdAddModify', {"third":1}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'accountThirdAddModify')
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="code"]', None)

        self.factory.xfer = AccountThirdAddModify()
        self.call('/diacamma.accounting/accountThirdAddModify', {'SAVE':'YES', "third":1, 'code':'411000'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'accountThirdAddModify')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third":1}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="code"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="total_txt"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '0.00€')

        self.factory.xfer = AccountThirdDel()
        self.call('/diacamma.accounting/accountThirdDel', {'CONFIRME':'YES', "accountthird":1}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'accountThirdDel')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third":1}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/HEADER', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="accountthird"]/RECORD', 0)

    def test_list(self):
        create_third([2, 8], ['401000'])
        create_third([6, 7], ['411000', '401000'])
        create_third([3, 4, 5], ['411000'])

        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/HEADER', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="contact"]', "contact")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="accountthird_set"]', "compte")
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 7)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Dalton Avrel')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="accountthird_set"]', '401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="contact"]', 'Dalton Jack')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[2]/VALUE[@name="accountthird_set"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[3]/VALUE[@name="contact"]', 'Dalton Joe')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[3]/VALUE[@name="accountthird_set"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[4]/VALUE[@name="contact"]', 'Dalton William')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[4]/VALUE[@name="accountthird_set"]', '411000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[5]/VALUE[@name="contact"]', 'Luke Lucky')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[5]/VALUE[@name="accountthird_set"]', '411000{[br/]}401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[6]/VALUE[@name="contact"]', 'Maximum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[6]/VALUE[@name="accountthird_set"]', '401000')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[7]/VALUE[@name="contact"]', 'Minimum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[7]/VALUE[@name="accountthird_set"]', '411000{[br/]}401000')

class AdminTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        rmtree(get_user_dir(), True)

    def test_default_configuration(self):
        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 2 + 3 + 2 + 1 + 7)

        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="begin"]', "début")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="end"]', "fin")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="status"]', "status")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER[@name="is_actif"]', "actif")
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 0)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="nb"]', 'Nombre total de exercices: 0')

        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/HEADER', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/HEADER[@name="name"]', "nom")
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="1"]/VALUE[@name="name"]', 'Report à nouveau')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="2"]/VALUE[@name="name"]', 'Achat')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="3"]/VALUE[@name="name"]', 'Vente')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="4"]/VALUE[@name="name"]', 'Règlement')
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="5"]/VALUE[@name="name"]', 'Autre')

        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="accounting-devise"]', '€')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="accounting-devise-iso"]', 'EUR')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="accounting-devise-prec"]', '2')

    def test_configuration_journal(self):
        self.factory.xfer = JournalAddModify()
        self.call('/diacamma.accounting/journalAddModify', {'journal':'2'}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'journalAddModify')
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', 'Achat')

        self.factory.xfer = JournalAddModify()
        self.call('/diacamma.accounting/journalAddModify', {'SAVE':'YES', 'journal':'2', 'name':'Dépense'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="2"]/VALUE[@name="name"]', 'Dépense')

        self.factory.xfer = JournalAddModify()
        self.call('/diacamma.accounting/journalAddModify', {'SAVE':'YES', 'name':'Caisse'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 6)
        self.assert_xml_equal('COMPONENTS/GRID[@name="journal"]/RECORD[@id="6"]/VALUE[@name="name"]', 'Caisse')

        self.factory.xfer = JournalDel()
        self.call('/diacamma.accounting/journalAddModify', {'journal':'2'}, False)
        self.assert_observer('CORE.Exception', 'diacamma.accounting', 'journalAddModify')
        self.assert_xml_equal('EXCEPTION/MESSAGE', 'journal réservé!')

        self.factory.xfer = JournalDel()
        self.call('/diacamma.accounting/journalAddModify', {'CONFIRME':'YES', 'journal':'6'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'journalAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="journal"]/RECORD', 5)

    def test_configuration_fiscalyear(self):
        to_day = date.today()
        to_day_plus_1 = date(to_day.year + 1, to_day.month, to_day.day) - timedelta(days=1)

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'en création')

        self.assert_xml_equal('COMPONENTS/DATE[@name="begin"]', to_day.isoformat())
        self.assert_xml_equal('COMPONENTS/DATE[@name="end"]', to_day_plus_1.isoformat())

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {'SAVE':'YES', 'begin':'2015-07-01', 'end':'2016-06-30'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="begin"]', '1 juillet 2015')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="end"]', '30 juin 2016')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="status"]', "en création")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="is_actif"]', "1")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="nb"]', 'Nombre total de exercices: 1')

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'fiscalYearAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'en création')

        self.assert_xml_equal('COMPONENTS/DATE[@name="begin"]', '2016-07-01')
        self.assert_xml_equal('COMPONENTS/DATE[@name="end"]', '2017-06-30')

        self.factory.xfer = FiscalYearAddModify()
        self.call('/diacamma.accounting/fiscalYearAddModify', {'SAVE':'YES', 'begin':'2016-07-01', 'end':'2017-06-30'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearAddModify')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="begin"]', '1 juillet 2016')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="end"]', '30 juin 2017')
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="status"]', "en création")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="is_actif"]', "0")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="nb"]', 'Nombre total de exercices: 2')

        self.factory.xfer = FiscalYearActive()
        self.call('/diacamma.accounting/fiscalYearActive', {'fiscalyear':'2'}, False)
        self.assert_observer('Core.Acknowledge', 'diacamma.accounting', 'fiscalYearActive')

        self.factory.xfer = Configuration()
        self.call('/diacamma.accounting/configuration', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'configuration')
        self.assert_count_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[1]/VALUE[@name="is_actif"]', "0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="fiscalyear"]/RECORD[2]/VALUE[@name="is_actif"]', "1")

def suite():
    # pylint: disable=redefined-outer-name
    suite = TestSuite()
    loader = TestLoader()
    # suite.addTest(loader.loadTestsFromTestCase(ThirdTest))
    suite.addTest(loader.loadTestsFromTestCase(AdminTest))
    return suite
