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
from lucterios.contacts.models import Individual, LegalEntity

from diacamma.accounting.views import ThirdList, ThirdAdd, ThirdSave, ThirdShow

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

class ThirdTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        change_ourdetail()  # contact 1
        create_individual('Avrel', 'Dalton')  # contact 2
        create_individual('William', 'Dalton')  # contact 3
        create_individual('Jack', 'Dalton')  # contact 4
        create_individual('Joe', 'Dalton')  # contact 5
        create_individual('Lucky', 'Luke')  # contact 6
        change_legal("Minimum")  # contact 7
        change_legal("Maximum")  # contact 8
        rmtree(get_user_dir(), True)

    def test_add_abstract(self):
        self.factory.xfer = ThirdList()
        self.call('/diacamma.accounting/thirdListing', {}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdListing')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/HEADER', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="contact"]', "contact")
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/HEADER[@name="accountthird_set"]', "compte")
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
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'Joe Dalton')

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
        self.assert_xml_equal('COMPONENTS/GRID[@name="third"]/RECORD[1]/VALUE[@name="contact"]', 'William Dalton')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third":1}, False)
        self.assert_observer('Core.Custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="contact"]', 'William Dalton')
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

def suite():
    # pylint: disable=redefined-outer-name
    suite = TestSuite()
    loader = TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(ThirdTest))
    return suite
