# -*- coding: utf-8 -*-
'''
diacamma.payoff tests package

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

from lucterios.contacts.tests_contacts import change_ourdetail

from diacamma.payoff.views_conf import PayoffConf, BankAccountAddModify,\
    BankAccountDelete, PaymentMethodAddModify


class PayoffTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        rmtree(get_user_dir(), True)
        change_ourdetail()

    def test_bank(self):
        self.factory.xfer = PayoffConf()
        self.call('/diacamma.payoff/payoffConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffConf')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 2 + 2 + 2 + 3 + 7)

        self.assert_count_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/HEADER', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/HEADER[@name="designation"]', "désignation")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/HEADER[@name="reference"]', "référence")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/HEADER[@name="account_code"]', "code comptable")
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/RECORD', 0)

        self.factory.xfer = BankAccountAddModify()
        self.call('/diacamma.payoff/bankAccountAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.payoff', 'bankAccountAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)

        self.factory.xfer = BankAccountAddModify()
        self.call('/diacamma.payoff/bankAccountAddModify',
                  {'designation': 'My bank', 'reference': '0123 456789 654 12', 'account_code': '512', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'bankAccountAddModify')

        self.factory.xfer = PayoffConf()
        self.call('/diacamma.payoff/payoffConf', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/RECORD[1]/VALUE[@name="designation"]', 'My bank')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/RECORD[1]/VALUE[@name="reference"]', '0123 456789 654 12')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/RECORD[1]/VALUE[@name="account_code"]', '512')

        self.factory.xfer = BankAccountDelete()
        self.call('/diacamma.payoff/bankAccountDelete',
                  {'bankaccount': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'bankAccountDelete')

        self.factory.xfer = PayoffConf()
        self.call('/diacamma.payoff/payoffConf', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="bankaccount"]/RECORD', 0)

    def test_method(self):
        self.factory.xfer = BankAccountAddModify()
        self.call('/diacamma.payoff/bankAccountAddModify',
                  {'designation': 'My bank', 'reference': '0123 456789 654 12', 'account_code': '512', 'SAVE': 'YES'}, False)

        self.factory.xfer = PayoffConf()
        self.call('/diacamma.payoff/payoffConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffConf')
        self.assert_count_equal('COMPONENTS/TAB', 3)
        self.assert_count_equal('COMPONENTS/*', 2 + 2 + 2 + 3 + 7)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/HEADER', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/HEADER[@name="paytype"]', "type")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/HEADER[@name="bank_account"]', "compte bancaire")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/HEADER[@name="info"]', "paramètres")
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD', 0)

        self.factory.xfer = PaymentMethodAddModify()
        self.call('/diacamma.payoff/paymentMethodAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.payoff', 'paymentMethodAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/SELECT[@name="bank_account"]/CASE', 1)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_item_1"]', "{[b]}IBAN{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="item_1"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_item_2"]', "{[b]}BIC{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="item_2"]', None)

        self.factory.xfer = PaymentMethodAddModify()
        self.call('/diacamma.payoff/paymentMethodAddModify', {'paytype': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.payoff', 'paymentMethodAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_item_1"]', "{[b]}IBAN{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="item_1"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_item_2"]', "{[b]}BIC{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="item_2"]', None)

        self.factory.xfer = PaymentMethodAddModify()
        self.call('/diacamma.payoff/paymentMethodAddModify', {'paytype': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.payoff', 'paymentMethodAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_item_1"]', "{[b]}libellé à{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="item_1"]', "WoldCompany")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_item_2"]', "{[b]}adresse{[/b]}")
        self.assert_xml_equal('COMPONENTS/MEMO[@name="item_2"]', "Place des cocotiers{[newline]}97200 FORT DE FRANCE")

        self.factory.xfer = PaymentMethodAddModify()
        self.call('/diacamma.payoff/paymentMethodAddModify', {'paytype': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.payoff', 'paymentMethodAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_item_1"]', "{[b]}compte Paypal{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="item_1"]', None)

        self.factory.xfer = PaymentMethodAddModify()
        self.call('/diacamma.payoff/paymentMethodAddModify',
                  {'paytype': 0, 'bank_account': 1, 'item_1': '123456798', 'item_2': 'AADDVVCC', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'paymentMethodAddModify')

        self.factory.xfer = PaymentMethodAddModify()
        self.call('/diacamma.payoff/paymentMethodAddModify',
                  {'paytype': 1, 'bank_account': 1, 'item_1': 'Truc', 'item_2': '1 rue de la Paix{[newline]}99000 LA-BAS', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'paymentMethodAddModify')

        self.factory.xfer = PaymentMethodAddModify()
        self.call('/diacamma.payoff/paymentMethodAddModify',
                  {'paytype': 2, 'bank_account': 1, 'item_1': 'monney@truc.org', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'paymentMethodAddModify')

        self.factory.xfer = PayoffConf()
        self.call('/diacamma.payoff/payoffConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffConf')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/HEADER', 3)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD[1]/VALUE[@name="paytype"]', "virement")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD[1]/VALUE[@name="bank_account"]', "My bank")
        self.assert_xml_equal('COMPONENTS/GRID[@name="paymentmethod"]/RECORD[1]/VALUE[@name="info"]', '{[b]}IBAN{[/b]}{[br/]}123456798{[br/]}{[b]}BIC{[/b]}{[br/]}AADDVVCC{[br/]}')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD[2]/VALUE[@name="paytype"]', "chèque")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD[2]/VALUE[@name="bank_account"]', "My bank")
        self.assert_xml_equal('COMPONENTS/GRID[@name="paymentmethod"]/RECORD[2]/VALUE[@name="info"]', '{[b]}libellé à{[/b]}{[br/]}Truc{[br/]}', True)

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD[3]/VALUE[@name="paytype"]', "PayPal")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="paymentmethod"]/RECORD[3]/VALUE[@name="bank_account"]', "My bank")
        self.assert_xml_equal('COMPONENTS/GRID[@name="paymentmethod"]/RECORD[3]/VALUE[@name="info"]', '{[b]}compte Paypal{[/b]}{[br/]}monney@truc.org{[br/]}')
