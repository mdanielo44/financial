# -*- coding: utf-8 -*-
'''
diacamma.invoice test_tools package

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

from diacamma.accounting.test_tools import create_account
from diacamma.accounting.models import FiscalYear
from diacamma.payoff.models import BankAccount


def default_bankaccount():
    create_account(['581'], 0, FiscalYear.get_current())
    BankAccount.objects.create(
        designation="My bank", reference="0123 456789 321654 12", account_code="512")
    BankAccount.objects.create(
        designation="PayPal", reference="paypal@moi.com", account_code="581")
