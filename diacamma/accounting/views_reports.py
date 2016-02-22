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
import sys
from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.utils import six, formats

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, CLOSE_NO, FORMTYPE_REFRESH, \
    WrapAction
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework.xfercomponents import XferCompImage, XferCompSelect, XferCompLabelForm, XferCompGrid, \
    XferCompEdit
from lucterios.contacts.models import LegalEntity
from lucterios.CORE.xferprint import XferPrintAction

from diacamma.accounting.models import FiscalYear, format_devise, EntryLineAccount, \
    ChartsAccount, CostAccounting


def get_spaces(size):
    return ''.ljust(size, '-').replace('-', '&#160;')


def convert_query_to_account(query):
    total = 0
    dict_account = {}
    for data_line in query:
        account = ChartsAccount.objects.get(
            id=data_line['account'])
        account_txt = six.text_type(account)
        if abs(data_line['data_sum']) > 0.0001:
            dict_account[account.code] = [
                account_txt, format_devise(data_line['data_sum'], 5)]
            total += data_line['data_sum']
    res = []
    keys = list(dict_account.keys())
    keys.sort()
    for key in keys:
        res.append(dict_account[key])
    return res, total


class FiscalYearReport(XferContainerCustom):
    icon = "accountingReport.png"
    model = FiscalYear
    field_id = 'year'
    add_filtering = False

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        self.grid = XferCompGrid('report')
        self.filter = None

    def fillresponse(self):
        self.fill_header()
        self.calcul_table()
        self.fill_body()

    def fill_header(self):
        self.item = FiscalYear.get_current(self.getparam("year"))
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)

        select_year = XferCompSelect(self.field_id)
        select_year.set_location(1, 0, 4)
        select_year.set_select_query(
            FiscalYear.objects.all())
        select_year.set_value(self.item.id)
        select_year.set_action(self.request, self.__class__.get_action(), {
                               'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        self.add_component(select_year)
        self.filter = Q(entry__year=self.item)
        if self.item.status != 2:
            self.fill_from_model(1, 1, False, ['begin'])
            self.fill_from_model(3, 1, False, ['end'])
            begin_filter = self.get_components('begin')
            begin_filter.set_action(self.request, self.__class__.get_action(), {
                                    'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
            end_filter = self.get_components('end')
            end_filter.set_action(self.request, self.__class__.get_action(), {
                                  'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
            self.filter &= Q(entry__date_value__gte=self.item.begin)
            self.filter &= Q(entry__date_value__lte=self.item.end)

        if self.add_filtering:
            filtercode = self.getparam('filtercode', '')
            lbl = XferCompLabelForm('filtercode_lbl')
            lbl.set_value_as_name(_("Accounting code starting with"))
            lbl.set_location(2, 3, 1)
            self.add_component(lbl)
            edt = XferCompEdit('filtercode')
            edt.set_value(filtercode)
            edt.set_location(3, 3, 2)
            edt.set_action(self.request, self.__class__.get_action(), {
                           'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
            self.add_component(edt)
            if filtercode != '':
                self.filter &= Q(account__code__startswith=filtercode)

        lbl = XferCompLabelForm('sep1')
        lbl.set_value("{[br/]}")
        lbl.set_location(0, 5)
        self.add_component(lbl)
        lbl = XferCompLabelForm("result")
        lbl.set_value_center(self.item.total_result_text)
        lbl.set_location(0, 6, 6)
        self.add_component(lbl)
        lbl = XferCompLabelForm('sep2')
        lbl.set_value("{[br/]}")
        lbl.set_location(0, 7)
        self.add_component(lbl)

    def _add_left_right_accounting(self, left_filter, rigth_filter, total_in_left):
        data_line_left, total_left = convert_query_to_account(EntryLineAccount.objects.filter(
            self.filter & left_filter).values('account').annotate(data_sum=Sum('amount')))
        data_line_right, total_right = convert_query_to_account(EntryLineAccount.objects.filter(
            self.filter & rigth_filter).values('account').annotate(data_sum=Sum('amount')))
        line_idx = 0
        for line_idx in range(max(len(data_line_left), len(data_line_right))):
            if line_idx < len(data_line_left):
                self.grid.set_value(
                    line_idx, 'left', data_line_left[line_idx][0])
                self.grid.set_value(
                    line_idx, 'left_n', data_line_left[line_idx][1])
            if line_idx < len(data_line_right):
                self.grid.set_value(
                    line_idx, 'right', data_line_right[line_idx][0])
                self.grid.set_value(
                    line_idx, 'right_n', data_line_right[line_idx][1])
        line_idx += 1
        self.grid.set_value(line_idx, 'left', '')
        self.grid.set_value(line_idx, 'right', '')
        line_idx += 1
        if abs(total_left - total_right) > 0.0001:
            if total_in_left:
                self.grid.set_value(
                    line_idx, 'left', get_spaces(5) + "{[i]}%s{[/i]}" % _('result'))
                self.grid.set_value(
                    line_idx, 'left_n', format_devise(total_right - total_left, 5))
                self.grid.set_value(line_idx, 'right', '')
                self.grid.set_value(line_idx, 'right_n', '')
            else:
                self.grid.set_value(line_idx, 'left', '')
                self.grid.set_value(line_idx, 'left_n', '')
                self.grid.set_value(
                    line_idx, 'right', get_spaces(5) + "{[i]}%s{[/i]}" % _('result'))
                self.grid.set_value(
                    line_idx, 'right_n', "{[i]}%s{[/i]}" % format_devise(total_left - total_right, 5))
            line_idx += 1
        self.grid.set_value(
            line_idx, 'left', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total'))
        self.grid.set_value(
            line_idx, 'left_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total_left, total_right), 5))
        self.grid.set_value(
            line_idx, 'right', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total'))
        self.grid.set_value(
            line_idx, 'right_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total_left, total_right), 5))

    def calcul_table(self):
        pass

    def fill_body(self):
        self.grid.set_location(0, 10, 6)
        self.add_component(self.grid)
        self.add_action(FiscalYearReportPrint.get_action(
            _("Print"), "images/print.png"), {'close': CLOSE_NO, 'params': {'classname': self.__class__.__name__}})
        self.add_action(WrapAction(_('Close'), 'images/close.png'), {})


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show balance sheet for current fiscal year'))
class FiscalYearBalanceSheet(FiscalYearReport):
    caption = _("Balance sheet")

    def __init__(self, **kwargs):
        FiscalYearReport.__init__(self, **kwargs)
        self.grid.add_header('left', _('Assets'))
        self.grid.add_header('left_n', _('Value'))
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Liabilities'))
        self.grid.add_header('right_n', _('Value'))

    def calcul_table(self):
        self._add_left_right_accounting(
            Q(account__type_of_account=0), Q(account__type_of_account__in=(1, 2)), False)


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show income statement for current fiscal year'))
class FiscalYearIncomeStatement(FiscalYearReport):
    caption = _("Income statement")

    def __init__(self, **kwargs):
        FiscalYearReport.__init__(self, **kwargs)
        self.grid.add_header('left', _('Expenses'))
        self.grid.add_header('left_n', _('Value'))
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Revenues'))
        self.grid.add_header('right_n', _('Value'))

    def calcul_table(self):
        self._add_left_right_accounting(
            Q(account__type_of_account=4), Q(account__type_of_account=3), True)


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show ledger for current fiscal year'))
class FiscalYearLedger(FiscalYearReport):
    caption = _("Ledger")
    add_filtering = True

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
            self.grid.set_value(self.line_idx, 'entry.designation', get_spaces(
                30) + "{[i]}%s{[/i]}" % _('total'))
            self.grid.set_value(self.line_idx, 'debit', "{[i]}%s{[/i]}" % format_devise(
                max((0, -1 * self.last_account.credit_debit_way() * self.last_total)), 0))
            self.grid.set_value(self.line_idx, 'credit', "{[i]}%s{[/i]}" % format_devise(
                max((0, self.last_account.credit_debit_way() * self.last_total)), 0))
            self.line_idx += 1
            self.grid.set_value(self.line_idx, 'entry.designation', '{[br/]}')
            self.line_idx += 1
            self.last_total = 0

    def calcul_table(self):
        self.line_idx = 1
        self.last_account = None
        self.last_third = None
        self.last_total = 0
        for line in EntryLineAccount.objects.filter(self.filter).order_by('account__code', 'entry__date_value', 'third'):
            if self.last_account != line.account:
                self._add_total_account()
                self.last_account = line.account
                self.last_third = None
                self.grid.set_value(self.line_idx, 'entry.designation', get_spaces(
                    15) + "{[u]}{[b]}%s{[/b]}{[/u]}" % six.text_type(self.last_account))
                self.line_idx += 1
            if self.last_third != line.third:
                self.grid.set_value(self.line_idx, 'entry.designation', get_spaces(
                    8) + "{[b]}%s{[/b]}" % six.text_type(line.entry_account))
                self.line_idx += 1
            self.last_third = line.third
            for header in self.grid.headers:
                self.grid.set_value(
                    self.line_idx, header.name, line.evaluate('#' + header.name))
            self.last_total += line.amount
            self.line_idx += 1
        self._add_total_account()


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show trial balance for current fiscal year'))
class FiscalYearTrialBalance(FiscalYearReport):
    caption = _("Trial balance")
    add_filtering = True

    def __init__(self, **kwargs):
        FiscalYearReport.__init__(self, **kwargs)
        self.grid.add_header('designation', _('name'))
        self.grid.add_header('total_debit', _('debit sum'))
        self.grid.add_header('total_credit', _('credit sum'))
        self.grid.add_header('solde_debit', _('debit'))
        self.grid.add_header('solde_credit', _('credit'))

    def _get_balance_values(self):
        balance_values = {}
        data_line_positifs = list(EntryLineAccount.objects.filter(self.filter & Q(amount__gt=0)).values(
            'account').annotate(data_sum=Sum('amount')))
        data_line_negatifs = list(EntryLineAccount.objects.filter(self.filter & Q(amount__lt=0)).values(
            'account').annotate(data_sum=Sum('amount')))
        for data_line in data_line_positifs + data_line_negatifs:
            if abs(data_line['data_sum']) > 0.0001:
                account = ChartsAccount.objects.get(
                    id=data_line['account'])
                if account.code not in balance_values.keys():
                    balance_values[account.code] = [
                        six.text_type(account), 0, 0]
                if (account.credit_debit_way() * data_line['data_sum']) > 0.0001:
                    balance_values[account.code][
                        2] = account.credit_debit_way() * data_line['data_sum']
                else:
                    balance_values[account.code][
                        1] = -1 * account.credit_debit_way() * data_line['data_sum']
        return balance_values

    def calcul_table(self):
        line_idx = 1
        balance_values = self._get_balance_values()
        keys = list(balance_values.keys())
        keys.sort()
        for key in keys:
            self.grid.set_value(
                line_idx, 'designation', balance_values[key][0])
            self.grid.set_value(
                line_idx, 'total_debit', format_devise(balance_values[key][1], 5))
            self.grid.set_value(
                line_idx, 'total_credit', format_devise(balance_values[key][2], 5))
            diff = balance_values[key][1] - balance_values[key][2]
            self.grid.set_value(
                line_idx, 'solde_debit', format_devise(max(0, diff), 0))
            if abs(diff) < 0.0001:
                self.grid.set_value(
                    line_idx, 'solde_credit', format_devise(0, 5))
            else:
                self.grid.set_value(
                    line_idx, 'solde_credit', format_devise(max(0, -1 * diff), 0))
            line_idx += 1


@MenuManage.describ('accounting.change_fiscalyear')
class FiscalYearReportPrint(XferPrintAction):
    caption = _("Print report fiscal year")
    icon = "accountingReport.png"
    model = FiscalYear
    field_id = 'year'

    def __init__(self):
        XferPrintAction.__init__(self)
        self.action_class = self.__class__.action_class
        self.caption = self.__class__.caption

    def get_report_generator(self):
        self.action_class = getattr(
            sys.modules[__name__], self.getparam("classname", ''))
        gen = XferPrintAction.get_report_generator(self)
        own_struct = LegalEntity.objects.get(id=1)
        gen.title = "{[u]}{[b]}%s{[/b]}{[/u]}{[br/]}{[i]}%s{[/i]}{[br/]}{[b]}%s{[/b]}" % (
            own_struct, self.action_class.caption, formats.date_format(date.today(), "DATE_FORMAT"))
        gen.page_width = 297
        gen.page_height = 210
        return gen


@MenuManage.describ('accounting.change_entryaccount')
class CostAccountingIncomeStatement(FiscalYearReport):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Income statement of cost accounting")

    def __init__(self, **kwargs):
        FiscalYearReport.__init__(self, **kwargs)
        self.grid.add_header('left', _('Expenses'))
        self.grid.add_header('left_n', _('Value'))
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Revenues'))
        self.grid.add_header('right_n', _('Value'))

    def fill_header(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)
        lbl = XferCompLabelForm('lblname')
        lbl.set_value_as_name(
            self.model._meta.verbose_name)
        lbl.set_location(1, 2)
        self.add_component(lbl)
        lbl = XferCompLabelForm('name')
        lbl.set_value(self.item)
        lbl.set_location(2, 2)
        self.add_component(lbl)
        lbl = XferCompLabelForm('sep1')
        lbl.set_value("{[br/]}")
        lbl.set_location(0, 3)
        self.add_component(lbl)
        self.filter = Q(entry__costaccounting=self.item)

    def calcul_table(self):
        self._add_left_right_accounting(
            Q(account__type_of_account=4), Q(account__type_of_account=3), True)
