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

from diacamma.invoice.models import Article, Vat

from diacamma.accounting.models import FiscalYear, CostAccounting
from diacamma.accounting.test_tools import create_account
from diacamma.payoff.models import BankAccount


def default_bankaccount():
    create_account(['581'], 0, FiscalYear.get_current())
    BankAccount.objects.create(
        designation="My bank", reference="0123 456789 321654 12", account_code="512")
    BankAccount.objects.create(
        designation="PayPal", reference="paypal@moi.com", account_code="581")


def default_articles():
    CostAccounting.objects.create(
        name='close', description='Close cost', status=1, is_default=False)
    CostAccounting.objects.create(
        name='open', description='Open cost', status=0, is_default=True)

    create_account(['709'], 3, FiscalYear.get_current())
    create_account(['4455'], 1, FiscalYear.get_current())
    vat1 = Vat.objects.create(name="5%", rate=5.0, isactif=True)
    vat2 = Vat.objects.create(name="20%", rate=20.0, isactif=True)
    Article.objects.create(reference='ABC1', designation="Article 01",
                           price="12.34", unit="kg", isdisabled=False, sell_account="701", vat=None)
    Article.objects.create(reference='ABC2', designation="Article 02",
                           price="56.78", unit="l", isdisabled=False, sell_account="707", vat=vat1)
    Article.objects.create(reference='ABC3', designation="Article 03",
                           price="324.97", unit="", isdisabled=False, sell_account="601", vat=None)
    Article.objects.create(reference='ABC4', designation="Article 04",
                           price="1.31", unit="", isdisabled=False, sell_account="708", vat=None)
    Article.objects.create(reference='ABC5', designation="Article 05",
                           price="64.10", unit="m", isdisabled=True, sell_account="701", vat=vat2)
