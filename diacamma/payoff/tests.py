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
from diacamma.payoff.views_conf import PayoffConf, BankAccountAddModify,\
    BankAccountDelete


class PayoffTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        rmtree(get_user_dir(), True)

    def test_vat(self):
        self.factory.xfer = PayoffConf()
        self.call('/diacamma.payoff/payoffConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffConf')
        self.assert_count_equal('COMPONENTS/TAB', 2)
        self.assert_count_equal('COMPONENTS/*', 2 + 2 + 2 + 5)

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
