# -*- coding: utf-8 -*-
'''
Describe report accounting viewer for Django

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

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, CLOSE_NO, \
    FORMTYPE_REFRESH
from lucterios.framework.xfergraphic import XferContainerCustom

from diacamma.accounting.models import FiscalYear, format_devise, \
    EntryLineAccount
from lucterios.framework.xfercomponents import XferCompImage, XferCompSelect, XferCompLabelForm, XferCompGrid
from django.utils import six
from datetime import date
from lucterios.contacts.models import LegalEntity

def get_spaces(size):
    return ''.ljust(size, '-').replace('-', '&nbsp;')

class FiscalYearReport(XferContainerCustom):
    icon = "accountingReport.png"
    model = FiscalYear
    field_id = 'year'

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        self.grid = XferCompGrid('report')
        self.filter = None

    def fillresponse(self):
        self.fill_header()
        self.calcul_table()

        self.fill_body()

    def fill_header(self):
        if self.getparam("year") is None:
            self.item = FiscalYear.get_current()
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 0, 3)
        self.add_component(img)

        lbl = XferCompLabelForm('title')
        lbl.set_location(1, 0, 4)
        own_struct = LegalEntity.objects.get(id=1)  # pylint: disable=no-member
        lbl.set_value_center("{[u]}{[b]}%s{[/b]}{[/u]}{[br/]}{[i]}%s{[/i]}{[br/]}{[b]}%s{[/b]}" % (own_struct, self.__class__.caption, date.today()))
        self.add_component(lbl)
        select_year = XferCompSelect(self.field_id)

        select_year.set_location(1, 1, 4)
        select_year.set_select_query(FiscalYear.objects.all())  # pylint: disable=no-member
        select_year.set_value(self.item.id)
        select_year.set_action(self.request, self.__class__.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
        self.add_component(select_year)
        self.filter = Q(entry__year=self.item)
        if self.item.status != 2:
            self.fill_from_model(1, 2, False, ['begin'])
            self.fill_from_model(3, 2, False, ['end'])
            begin_filter = self.get_components('begin')
            begin_filter.set_action(self.request, self.__class__.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
            end_filter = self.get_components('end')
            end_filter.set_action(self.request, self.__class__.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
            self.filter &= Q(entry__date_value__gte=self.item.begin)
            self.filter &= Q(entry__date_value__lte=self.item.end)

    def calcul_table(self):
        pass

    def fill_body(self):
        self.grid.set_location(0, 3, 6)
        self.add_component(self.grid)
        lbl = XferCompLabelForm("result")
        lbl.set_value_center(self.item.total_result_text)
        lbl.set_location(0, 4, 6)
        self.add_component(lbl)

@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show balance sheet for current fiscal year'))
class FiscalYearBalanceSheet(FiscalYearReport):
    caption = _("Balance sheet")

    def calcul_table(self):
        pass

@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show income statement for current fiscal year'))
class FiscalYearIncomeStatement(FiscalYearReport):
    caption = _("Income statement")

    def calcul_table(self):
        pass

@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show ledger for current fiscal year'))
class FiscalYearLedger(FiscalYearReport):
    caption = _("Ledger")

    def __init__(self, **kwargs):
        FiscalYearReport.__init__(self, **kwargs)
        self.grid.add_header('entry.num', _('numeros'))
        self.grid.add_header('entry.date_entry', _('date entry'))
        self.grid.add_header('entry.date_value', _('date value'))
        self.grid.add_header('entry.designation', _('name'))
        self.grid.add_header('debit', _('debit'))
        self.grid.add_header('credit', _('credit'))
        self.last_account = None
        self.last_third = None
        self.last_total = 0
        self.line_idx = 1

    def _add_total_account(self):
        if self.last_account is not None:
            self.grid.set_value(self.line_idx, 'entry.designation', get_spaces(40) + "{[i]}%s{[/i]}" % _('total'))
            self.grid.set_value(self.line_idx, 'debit', "{[i]}%s{[/i]}" % format_devise(max((0, -1 * self.last_account.credit_debit_way() * self.last_total)), 0))
            self.grid.set_value(self.line_idx, 'credit', "{[i]}%s{[/i]}" % format_devise(max((0, self.last_account.credit_debit_way() * self.last_total)), 0))
            self.line_idx += 1
            self.grid.set_value(self.line_idx, 'entry.designation', '{[br/]}')
            self.line_idx += 1
            self.last_total = 0

    def calcul_table(self):
        self.line_idx = 1
        self.last_account = None
        self.last_third = None
        self.last_total = 0
        for line in EntryLineAccount.objects.filter(self.filter).order_by('account__code', 'entry__date_value', 'third'):  # pylint: disable=no-member
            if self.last_account != line.account:
                self._add_total_account()
                self.last_account = line.account
                self.last_third = None
                self.grid.set_value(self.line_idx, 'entry.designation', get_spaces(20) + "{[u]}{[b]}%s{[/b]}{[/u]}" % six.text_type(self.last_account))
                self.line_idx += 1
            if self.last_third != line.third:
                self.grid.set_value(self.line_idx, 'entry.designation', get_spaces(10) + "{[b]}%s{[/b]}" % six.text_type(line.entry_account))
                self.line_idx += 1

            self.last_third = line.third
            for header in self.grid.headers:
                self.grid.set_value(self.line_idx, header.name, line.evaluate('#' + header.name))
            self.last_total += line.amount
            self.line_idx += 1
        self._add_total_account()

@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show trial balance for current fiscal year'))
class FiscalYearTrialBalance(FiscalYearReport):
    caption = _("Trial balance")

    def calcul_table(self):
        pass
