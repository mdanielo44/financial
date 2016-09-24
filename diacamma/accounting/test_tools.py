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

from lucterios.contacts.models import Individual, LegalEntity, AbstractContact
from lucterios.contacts.tests_contacts import change_ourdetail

from diacamma.accounting.models import Third, AccountThird, FiscalYear, \
    ChartsAccount, EntryAccount, Journal, AccountLink, \
    CostAccounting, ModelEntry, ModelLineEntry
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from diacamma.accounting.tools import clear_system_account


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
        new_third = Third.objects.create(contact=AbstractContact.objects.get(
            id=abstractid), status=0)
        if codes is not None:
            for code in codes:
                AccountThird.objects.create(
                    third=new_third, code=code)


def create_year(status=0):
    new_year = FiscalYear.objects.create(
        begin='2015-01-01', end='2015-12-31', status=status)
    new_year.set_has_actif()
    return new_year


def create_account(codes, type_of_account, year=None):
    if year is None:
        year = FiscalYear.get_current()
    for code in codes:
        ChartsAccount.objects.create(
            code=code, name=code, type_of_account=type_of_account, year=year)


def fill_thirds():
    create_third([2, 8], ['401'])  # 1 2
    create_third([6, 7], ['411', '401'])  # 3 4
    create_third([3, 4, 5], ['411'])  # 5 6 7


def initial_thirds():
    initial_contacts()
    fill_thirds()


def fill_accounts(year=None):
    create_account(['411', '512', '531'], 0, year)  # 1 2 3
    create_account(['401'], 1, year)  # 4
    create_account(['106', '110', '119'], 2, year)  # 5 6 7
    create_account(['701', '706', '707'], 3, year)  # 8 9 10
    # 11 12 13 14 15
    create_account(['601', '602', '604', '607', '627'], 4, year)


def default_costaccounting():
    CostAccounting.objects.create(
        name='close', description='Close cost', status=1, is_default=False)
    CostAccounting.objects.create(
        name='open', description='Open cost', status=0, is_default=True)


def add_models():
    model1 = ModelEntry.objects.create(journal=Journal.objects.get(
        id=2), designation='achat')
    ModelLineEntry.objects.create(model=model1, code='411', third=Third.objects.get(
        id=3), amount=19.37)
    ModelLineEntry.objects.create(
        model=model1, code='512', amount=-19.37)
    model2 = ModelEntry.objects.create(journal=Journal.objects.get(
        id=3), designation='vente')
    ModelLineEntry.objects.create(model=model2, code='401', third=Third.objects.get(
        id=6), amount=-68.47)
    ModelLineEntry.objects.create(
        model=model2, code='531', amount=68.47)


def set_accounting_system():
    Parameter.change_value(
        'accounting-system', 'diacamma.accounting.system.french.FrenchSystemAcounting')
    Params.clear()
    clear_system_account()


def default_compta(status=0):
    set_accounting_system()
    year = create_year(status)
    fill_accounts(year)


def add_entry(yearid, journalid, date_value, designation, serial_entry, closed=False, costaccounting=None):
    year = FiscalYear.objects.get(id=yearid)
    journal = Journal.objects.get(id=journalid)
    new_entry = EntryAccount.objects.create(
        year=year, journal=journal, date_value=date_value, designation=designation, costaccounting=costaccounting)
    new_entry.save_entrylineaccounts(serial_entry)
    if closed:
        new_entry.closed()
    return new_entry


def fill_entries(yearid):

    cost1 = CostAccounting.objects.create(
        name='close', description='Close cost', status=1, is_default=False)
    # cost1: dep=12.34 / rec=0.00 => res=-12.34
    cost2 = CostAccounting.objects.create(
        name='open', description='Open cost', status=0, is_default=True)

    # cost2: dep=258.02 / rec=70.64 => res=-187.38
    _ = add_entry(yearid, 1, '2015-02-01', 'Report à nouveau',
                  '-1|5|0|1250.380000|None|\n-2|2|0|1135.930000|None|\n-3|3|0|114.450000|None|', True)  # 1 2 3
    entry2 = add_entry(yearid, 2, '2015-02-14', 'depense 1',
                       '-1|12|0|63.940000|None|\n-2|4|4|63.940000|None|', True, costaccounting=cost2)  # 4 5
    entry3 = add_entry(yearid, 4, '2015-02-15', 'regement depense 1',
                       '-1|2|0|-63.940000|ch N°34543|\n-2|4|4|-63.940000|None|', True)  # 6 7
    entry4 = add_entry(yearid, 2, '2015-02-13', 'depense 2',
                       '-1|14|0|194.080000|None|\n-2|4|1|194.080000|None|', costaccounting=cost2)  # 8 9
    entry5 = add_entry(yearid, 4, '2015-02-17', 'regement depense 2',
                       '-1|3|0|-194.080000|ch N°34545|\n-2|4|1|-194.080000|None|')  # 10 11
    _ = add_entry(yearid, 2, '2015-02-20', 'depense 3',
                  '-1|11|0|78.240000|None|\n-2|4|2|78.240000|None|')  # 12 13
    entry7 = add_entry(yearid, 3, '2015-02-21', 'vente 1',
                       '-1|10|0|70.640000|None|\n-2|1|7|70.640000|None|', True, costaccounting=cost2)  # 14 15
    entry8 = add_entry(yearid, 4, '2015-02-22', 'regement vente 1',
                       '-1|2|0|70.640000|BP N°654321|\n-2|1|7|-70.640000|None|', True)  # 16 17
    _ = add_entry(yearid, 3, '2015-02-21', 'vente 2',
                  '-1|10|0|125.970000|None|\n-2|1|5|125.970000|None|', True)  # 18 19
    _ = add_entry(yearid, 3, '2015-02-24', 'vente 3',
                  '-1|10|0|34.010000|None|\n-2|1|4|34.010000|None|')  # 20 21
    _ = add_entry(yearid, 5, '2015-02-20', 'Frais bancaire',
                  '-1|2|0|-12.340000|None|\n-2|15|0|12.340000|None|', True, costaccounting=cost1)  # 22 23
    AccountLink.create_link([entry2, entry3])
    AccountLink.create_link([entry4, entry5])
    AccountLink.create_link([entry7, entry8])
