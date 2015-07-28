# -*- coding: utf-8 -*-
'''
lucterios.contacts package

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

from lucterios.contacts.models import Individual, LegalEntity, AbstractContact
from lucterios.contacts.tests_contacts import change_ourdetail

from diacamma.accounting.models import Third, AccountThird, FiscalYear,\
    ChartsAccount

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

def create_year(status=0):
    FiscalYear.objects.create(begin='2015-01-01', end='2015-12-31', status=status, is_actif=True) # pylint: disable=no-member

def create_account(codes, type_of_account):
    for code in codes:
        ChartsAccount.objects.create(code=code, name=code, type_of_account=type_of_account, year=FiscalYear.get_current()) # pylint: disable=no-member

def default_compta(status=0):
    create_year(status)
    create_account(['411000', '512000', '531000'], 0)
    create_account(['401000'], 1)
    create_account(['106000', '110000', '119000'], 2)
    create_account(['701000', '706000', '707000'], 3)
    create_account(['601000', '602000', '604000', '607000'], 4)
