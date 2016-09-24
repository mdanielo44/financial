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


class DefaultSystemAccounting(object):

    def get_general_mask(self):
        return ''

    def get_cash_mask(self):
        return ''

    def get_cash_begin(self):
        return ''

    def get_provider_mask(self):
        return ''

    def get_customer_mask(self):
        return ''

    def get_employed_mask(self):
        return ''

    def get_societary_mask(self):
        return ''

    def get_revenue_mask(self):
        return ''

    def get_expence_mask(self):
        return ''

    def get_third_mask(self):
        return ''

    def new_charts_account(self, code):
        return ''

    def check_begin(self, year, xfer):
        return False

    def finalize_year(self, year):
        return

    def import_lastyear(self, year, import_result):
        return

    def get_export_xmlfiles(self):
        return None
