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
from diacamma.accounting.system.default import DefaultSystemAccounting

GENERAL_MASK = r'[0-8][0-9]{2}[0-9]*'
CASH_MASK = r'5[0-9][0-9]+'
CASH_MASK_BEGIN = '5'

PROVIDER_MASK = r'40[0-9]+'
CUSTOMER_MASK = r'41[0-9]+'
EMPLOYED_MASK = r'42[0-9]+'
SOCIETARY_MASK = r'45[0-9]+'
THIRD_MASK = "%s|%s|%s|%s" % (PROVIDER_MASK, CUSTOMER_MASK, EMPLOYED_MASK, SOCIETARY_MASK)

class FrenchSystemAcounting(DefaultSystemAccounting):

    def get_general_mask(self):
        return GENERAL_MASK

    def get_cash_mask(self):
        return CASH_MASK

    def get_cash_begin(self):
        return CASH_MASK_BEGIN

    def get_provider_mask(self):
        return PROVIDER_MASK

    def get_customer_mask(self):
        return CUSTOMER_MASK

    def get_employed_mask(self):
        return EMPLOYED_MASK

    def get_societary_mask(self):
        return SOCIETARY_MASK

    def get_third_mask(self):
        return THIRD_MASK
