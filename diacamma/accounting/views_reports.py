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
    WrapAction, convert_date, ActionsManage, SELECT_MULTI
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework.xfercomponents import XferCompImage, XferCompSelect, XferCompLabelForm, XferCompGrid, \
    XferCompEdit
from lucterios.contacts.models import LegalEntity
from lucterios.CORE.xferprint import XferPrintAction

from diacamma.accounting.models import FiscalYear, format_devise, EntryLineAccount, \
    ChartsAccount, CostAccounting, Budget, Third
from diacamma.accounting.tools import correct_accounting_code,\
    current_system_account
from lucterios.framework.xferadvance import TITLE_PRINT, TITLE_CLOSE


def get_spaces(size):
    return ''.ljust(size, '-').replace('-', '&#160;')


def convert_query_to_account(query1, query2=None, query_budget=None, sign_value=None, with_third=False):
    def credit_debit_way(data_line):
        if 'account' in data_line.keys():
            account = ChartsAccount.objects.get(id=data_line['account'])
            return account.credit_debit_way()
        elif 'code' in data_line.keys():
            account_code = correct_accounting_code(data_line['code'])
            account = ChartsAccount.get_chart_account(account_code)
            return account.credit_debit_way()
        return 0

    def check_account(data_line):
        if 'account' in data_line.keys():
            account = ChartsAccount.objects.get(id=data_line['account'])
            account_code = correct_accounting_code(account.code)
        elif 'code' in data_line.keys():
            account_code = correct_accounting_code(data_line['code'])
        if ('third' in data_line.keys()) and (data_line['third'] is not None):
            account_code = "%s#%s" % (account_code, data_line['third'])
        if account_code not in dict_account.keys():
            account = ChartsAccount.get_chart_account(account_code.split('#')[0])
            if ('third' in data_line.keys()) and (data_line['third'] is not None):
                third = Third.objects.get(id=data_line['third'])
                account_title = "[%s %s]" % (account.code, six.text_type(third))
            else:
                account_title = account.get_name()
            dict_account[account_code] = [account_title, None, None]
            if isinstance(query_budget, list):
                for _item in query_budget:
                    dict_account[account_code].append(None)
            else:
                dict_account[account_code].append(None)
        return account_code
    total1 = 0
    total2 = None
    total3 = None
    dict_account = {}
    if with_third:
        fields = ['account', 'third']
    else:
        fields = ['account']
    for data_line in EntryLineAccount.objects.filter(query1).values(*fields).annotate(data_sum=Sum('amount')):
        if abs(data_line['data_sum']) > 0.001:
            if sign_value is None:
                account_code = check_account(data_line)
                dict_account[account_code][1] = format_devise(data_line['data_sum'], 5)
                total1 += data_line['data_sum']
            elif isinstance(sign_value, bool):
                spec_sign = 1 if sign_value else -1
                account_code = check_account(data_line)
                dict_account[account_code][1] = format_devise(spec_sign * credit_debit_way(data_line) * data_line['data_sum'], 5)
                total1 += spec_sign * credit_debit_way(data_line) * data_line['data_sum']
            elif (sign_value * credit_debit_way(data_line) * data_line['data_sum'] > 0):
                account_code = check_account(data_line)
                dict_account[account_code][1] = format_devise(abs(data_line['data_sum']), 5)
                total1 += abs(data_line['data_sum'])
    if query2 is not None:
        total2 = 0
        for data_line in EntryLineAccount.objects.filter(query2).values(*fields).annotate(data_sum=Sum('amount')):
            if abs(data_line['data_sum']) > 0.001:
                if sign_value is None:
                    account_code = check_account(data_line)
                    dict_account[account_code][2] = format_devise(data_line['data_sum'], 5)
                    total2 += data_line['data_sum']
                elif isinstance(sign_value, bool):
                    spec_sign = 1 if sign_value else -1
                    account_code = check_account(data_line)
                    dict_account[account_code][2] = format_devise(spec_sign * credit_debit_way(data_line) * data_line['data_sum'], 5)
                    total2 += spec_sign * credit_debit_way(data_line) * data_line['data_sum']
                elif (sign_value * credit_debit_way(data_line) * data_line['data_sum'] > 0):
                    account_code = check_account(data_line)
                    dict_account[account_code][2] = format_devise(abs(data_line['data_sum']), 5)
                    total2 += abs(data_line['data_sum'])
    if isinstance(query_budget, list):
        query_budget_list = query_budget
    else:
        query_budget_list = [query_budget]
    total_b = []
    id_dict = 3
    for query_budget_item in query_budget_list:
        total3 = 0
        if query_budget_item is not None:
            for data_line in Budget.objects.filter(query_budget_item).values('code').annotate(data_sum=Sum('amount')):
                if abs(data_line['data_sum']) > 0.001:
                    if sign_value is None:
                        account_code = check_account(data_line)
                        dict_account[account_code][id_dict] = format_devise(data_line['data_sum'], 5)
                        total3 += data_line['data_sum']
                    elif isinstance(sign_value, bool):
                        spec_sign = 1 if sign_value else -1
                        account_code = check_account(data_line)
                        dict_account[account_code][id_dict] = format_devise(spec_sign * credit_debit_way(data_line) * data_line['data_sum'], 5)
                        total3 += spec_sign * credit_debit_way(data_line) * data_line['data_sum']
                    elif (sign_value * credit_debit_way(data_line) * data_line['data_sum'] > 0):
                        account_code = check_account(data_line)
                        dict_account[account_code][id_dict] = format_devise(abs(data_line['data_sum']), 5)
                        total3 += abs(data_line['data_sum'])
        id_dict += 1
        total_b.append(total3)
    if isinstance(query_budget, list):
        total3 = total_b
    else:
        total3 = total_b[0]
    res = []
    keys = list(dict_account.keys())
    keys.sort()
    for key in keys:
        res.append(dict_account[key])
    return res, total1, total2, total3


class FiscalYearReport(XferContainerCustom):
    icon = "accountingReport.png"
    model = FiscalYear
    field_id = 'year'
    add_filtering = False

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        self.filter = None
        self.lastfilter = None
        self.budgetfilter_left = None
        self.budgetfilter_right = None

    def fillresponse(self):
        self.fill_header()
        self.calcul_table()
        self.fill_body()
        self.fill_buttons()

    def define_gridheader(self):
        pass

    def fill_filterheader(self):
        pass

    def fill_filterCode(self):
        if self.add_filtering:
            filtercode = self.getparam('filtercode', '')
            lbl = XferCompLabelForm('filtercode_lbl')
            lbl.set_value_as_name(_("Accounting code starting with"))
            lbl.set_location(2, 3, 1)
            self.add_component(lbl)
            edt = XferCompEdit('filtercode')
            edt.set_value(filtercode)
            edt.set_location(3, 3, 2)
            edt.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
            self.add_component(edt)
            if filtercode != '':
                self.filter &= Q(account__code__startswith=filtercode)

    def fill_header(self):
        self.item = FiscalYear.get_current(self.getparam("year"))
        new_begin = convert_date(self.getparam("begin"), self.item.begin)
        new_end = convert_date(self.getparam("end"), self.item.end)
        if (new_begin >= self.item.begin) and (new_end <= self.item.end):
            self.item.begin = new_begin
            self.item.end = new_end
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)

        select_year = XferCompSelect(self.field_id)
        select_year.set_location(1, 0, 4)
        select_year.set_select_query(FiscalYear.objects.all())
        select_year.set_value(self.item.id)
        select_year.set_needed(True)
        select_year.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(select_year)
        self.filter = Q(entry__year=self.item)
        if self.item.status != 2:
            self.fill_from_model(1, 1, False, ['begin'])
            self.fill_from_model(3, 1, False, ['end'])
            begin_filter = self.get_components('begin')
            begin_filter.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
            end_filter = self.get_components('end')
            end_filter.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
            self.filter &= Q(entry__date_value__gte=self.item.begin)
            self.filter &= Q(entry__date_value__lte=self.item.end)
        self.fill_filterCode()
        lbl = XferCompLabelForm("result")
        lbl.set_value_center(self.item.total_result_text)
        lbl.set_location(0, 6, 6)
        self.add_component(lbl)
        self.fill_filterheader()
        self.define_gridheader()

    def add_total_in_grid(self, total_in_left, total1_left, total2_left, totalb_left, total1_right, total2_right, totalb_right, line_idx):
        line_idx += 1
        self.grid.set_value(line_idx, 'left', '')
        self.grid.set_value(line_idx, 'right', '')
        line_idx += 1
        if (abs(total1_left - total1_right) > 0.0001) or ((total2_left is not None) and (total2_right is not None) and (abs(total2_left - total2_right) > 0.0001)):
            if total_in_left:
                self.grid.set_value(line_idx, 'left', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (profit)'))
                self.grid.set_value(line_idx, 'right', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (deficit)'))
            else:
                self.grid.set_value(line_idx, 'left', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (deficit)'))
                self.grid.set_value(line_idx, 'right', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (profit)'))
            self.grid.set_value(line_idx, 'right_n', '')
            self.grid.set_value(line_idx, 'right_n_1', '')
            self.grid.set_value(line_idx, 'right_b', '')
            self.grid.set_value(line_idx, 'left_n', '')
            self.grid.set_value(line_idx, 'left_n_1', '')
            self.grid.set_value(line_idx, 'left_b', '')
            result_n = total1_right - total1_left
            if (total2_left is not None) and (total2_right is not None):
                result_n_1 = total2_right - total2_left
            else:
                result_n_1 = 0.0
            if (totalb_left is not None) and (totalb_right is not None):
                result_b = totalb_right - totalb_left
            else:
                result_b = 0.0
            if total_in_left:
                if result_n > 0:
                    pos_n = 'left_n'
                else:
                    pos_n = 'right_n'
                if result_n_1 > 0:
                    pos_n_1 = 'left_n_1'
                else:
                    pos_n_1 = 'right_n_1'
                if result_b > 0:
                    pos_b = 'left_b'
                else:
                    pos_b = 'right_b'
            else:
                result_n = -1 * result_n
                result_n_1 = -1 * result_n_1
                if result_n > 0:
                    pos_n = 'right_n'
                else:
                    pos_n = 'left_n'
                if result_n_1 > 0:
                    pos_n_1 = 'right_n_1'
                else:
                    pos_n_1 = 'left_n_1'
                if result_b > 0:
                    pos_b = 'right_b'
                else:
                    pos_b = 'left_b'
            self.grid.set_value(line_idx, pos_n, format_devise(abs(result_n), 5))
            if (totalb_left is not None) and (abs(result_b) > 0.0001):
                self.grid.set_value(line_idx, pos_b, format_devise(abs(result_b), 5))
            else:
                pos_b = ""
            if (self.lastfilter is not None) and (abs(result_n_1) > 0.0001):
                self.grid.set_value(line_idx, pos_n_1, format_devise(abs(result_n_1), 5))
            else:
                pos_n_1 = ""
            if (pos_n != 'left_n') and (pos_n_1 != 'left_n_1') and (pos_b != 'left_b'):
                self.grid.set_value(line_idx, 'left', '')
            if (pos_n != 'right_n') and (pos_n_1 != 'right_n_1') and (pos_b != 'right_b'):
                self.grid.set_value(line_idx, 'right', '')
            line_idx += 1
        self.grid.set_value(line_idx, 'left', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total'))
        self.grid.set_value(line_idx, 'left_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total1_left, total1_right), 5))
        if self.lastfilter is not None:
            self.grid.set_value(line_idx, 'left_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total2_left, total2_right), 5))
        if self.budgetfilter_left is not None:
            self.grid.set_value(line_idx, 'left_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(totalb_left, totalb_right), 5))
        self.grid.set_value(line_idx, 'right', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total'))
        self.grid.set_value(line_idx, 'right_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total1_left, total1_right), 5))
        if self.lastfilter is not None:
            self.grid.set_value(line_idx, 'right_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total2_left, total2_right), 5))
        if self.budgetfilter_right is not None:
            self.grid.set_value(line_idx, 'right_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(totalb_left, totalb_right), 5))

    def _add_left_right_accounting(self, left_filter, rigth_filter, total_in_left):
        data_line_left, total1_left, total2_left, totalb_left = convert_query_to_account(
            self.filter & left_filter, self.lastfilter & left_filter if self.lastfilter is not None else None, self.budgetfilter_left)
        data_line_right, total1_right, total2_right, totalb_right = convert_query_to_account(
            self.filter & rigth_filter, self.lastfilter & rigth_filter if self.lastfilter is not None else None, self.budgetfilter_right)
        line_idx = 0
        for line_idx in range(max(len(data_line_left), len(data_line_right))):
            if line_idx < len(data_line_left):
                self.grid.set_value(
                    line_idx, 'left', data_line_left[line_idx][0])
                self.grid.set_value(
                    line_idx, 'left_n', data_line_left[line_idx][1])
                if self.lastfilter is not None:
                    self.grid.set_value(
                        line_idx, 'left_n_1', data_line_left[line_idx][2])
                if self.budgetfilter_left is not None:
                    self.grid.set_value(
                        line_idx, 'left_b', data_line_left[line_idx][3])
            if line_idx < len(data_line_right):
                self.grid.set_value(
                    line_idx, 'right', data_line_right[line_idx][0])
                self.grid.set_value(
                    line_idx, 'right_n', data_line_right[line_idx][1])
                if self.lastfilter is not None:
                    self.grid.set_value(
                        line_idx, 'right_n_1', data_line_right[line_idx][2])
                if self.budgetfilter_right is not None:
                    self.grid.set_value(
                        line_idx, 'right_b', data_line_right[line_idx][3])
        self.add_total_in_grid(total_in_left, total1_left, total2_left, totalb_left, total1_right, total2_right, totalb_right, line_idx)

    def calcul_table(self):
        pass

    def fill_body(self):
        self.grid.set_location(0, 10, 6)
        self.add_component(self.grid)

    def fill_buttons(self):
        self.add_action(FiscalYearReportPrint.get_action(TITLE_PRINT, "images/print.png"),
                        close=CLOSE_NO, params={'classname': self.__class__.__name__})
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show balance sheet for current fiscal year'))
class FiscalYearBalanceSheet(FiscalYearReport):
    caption = _("Balance sheet")

    def fill_filterheader(self):
        if self.item.last_fiscalyear is not None:
            self.lastfilter = Q(entry__year=self.item.last_fiscalyear)
            lbl = XferCompLabelForm('sep_last')
            lbl.set_value("{[br/]}{[br/]}")
            lbl.set_location(2, 11, 3)
            self.add_component(lbl)
            lbl = XferCompLabelForm('lbllast_year')
            lbl.set_value_as_name(self.item.last_fiscalyear.get_identify())
            lbl.set_location(1, 12)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_year')
            lbl.set_value(six.text_type(self.item.last_fiscalyear))
            lbl.set_location(2, 12, 4)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_result')
            lbl.set_value(self.item.last_fiscalyear.total_result_text)
            lbl.set_location(2, 13, 4)
            self.add_component(lbl)

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('left', _('Assets'))
        self.grid.add_header('left_n', self.item.get_identify())
        if self.lastfilter is not None:
            self.grid.add_header(
                'left_n_1', self.item.last_fiscalyear.get_identify())
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Liabilities'))
        self.grid.add_header('right_n', self.item.get_identify())
        if self.lastfilter is not None:
            self.grid.add_header(
                'right_n_1', self.item.last_fiscalyear.get_identify())

    def fill_grid(self, index_begin, side, data_line):
        line_idx = index_begin
        for data_item in data_line:
            self.grid.set_value(line_idx, side, data_item[0])
            self.grid.set_value(line_idx, side + '_n', data_item[1])
            if self.item.last_fiscalyear is not None:
                self.grid.set_value(line_idx, side + '_n_1', data_item[2])
            line_idx += 1
        return line_idx

    def calcul_table(self):
        cash_filter = Q(account__code__regex=current_system_account().get_cash_mask())
        data_line_left, total1_lefta, total2_lefta, _b_left = convert_query_to_account(self.filter & cash_filter,
                                                                                       self.lastfilter & cash_filter if self.lastfilter is not None else None,
                                                                                       None)
        left_line_idx = self.fill_grid(0, 'left', data_line_left)

        other_filter = Q(account__type_of_account__in=(0, 1, 2)) & ~cash_filter
        data_line_left, total1_leftb, total2_leftb, _b_left = convert_query_to_account(self.filter & other_filter,
                                                                                       self.lastfilter & other_filter if self.lastfilter is not None else None,
                                                                                       None, sign_value=-1)
        left_line_idx = self.fill_grid(left_line_idx, 'left', data_line_left)
        total1_left = total1_lefta + total1_leftb
        if self.lastfilter is not None:
            total2_left = total2_lefta + total2_leftb
        else:
            total2_left = None
        data_line_right, total1_right, total2_right, _b_right = convert_query_to_account(self.filter & other_filter,
                                                                                         self.lastfilter & other_filter if self.lastfilter is not None else None,
                                                                                         None, sign_value=1)
        right_line_idx = self.fill_grid(0, 'right', data_line_right)
        self.add_total_in_grid(False, total1_left, total2_left, 0, total1_right, total2_right, 0, max(left_line_idx, right_line_idx))


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show income statement for current fiscal year'))
class FiscalYearIncomeStatement(FiscalYearReport):
    caption = _("Income statement")

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('left', _('Expense'))
        self.grid.add_header('left_n', self.item.get_identify())
        self.grid.add_header('left_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header(
                'left_n_1', self.item.last_fiscalyear.get_identify())
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Revenue'))
        self.grid.add_header('right_n', self.item.get_identify())
        self.grid.add_header('right_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header(
                'right_n_1', self.item.last_fiscalyear.get_identify())

    def fill_filterheader(self):
        if self.item.last_fiscalyear is not None:
            self.lastfilter = Q(entry__year=self.item.last_fiscalyear)
            lbl = XferCompLabelForm('sep_last')
            lbl.set_value("{[br/]}{[br/]}")
            lbl.set_location(2, 11, 3)
            self.add_component(lbl)
            lbl = XferCompLabelForm('lbllast_year')
            lbl.set_value_as_name(self.item.last_fiscalyear.get_identify())
            lbl.set_location(1, 12)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_year')
            lbl.set_value(six.text_type(self.item.last_fiscalyear))
            lbl.set_location(2, 12, 4)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_result')
            lbl.set_value(self.item.last_fiscalyear.total_result_text)
            lbl.set_location(2, 13, 4)
            self.add_component(lbl)

    def calcul_table(self):
        self.budgetfilter_right = Q(year=self.item) & Q(code__regex=current_system_account().get_revenue_mask())
        self.budgetfilter_left = Q(year=self.item) & Q(code__regex=current_system_account().get_expence_mask())
        self._add_left_right_accounting(Q(account__type_of_account=4), Q(account__type_of_account=3), True)


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show ledger for current fiscal year'))
class FiscalYearLedger(FiscalYearReport):
    caption = _("Ledger")
    add_filtering = True

    def __init__(self, **kwargs):
        FiscalYearReport.__init__(self, **kwargs)
        self.last_account = None
        self.last_third = None
        self.last_total = 0
        self.line_idx = 1

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('entry.num', _('numeros'))
        self.grid.add_header('entry.date_entry', _('date entry'))
        self.grid.add_header('entry.date_value', _('date value'))
        self.grid.add_header('entry.designation', _('name'))
        self.grid.add_header('debit', _('debit'))
        self.grid.add_header('credit', _('credit'))

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

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
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
    with_text_export = True
    tab_change_page = True

    def __init__(self):
        XferPrintAction.__init__(self)
        self.action_class = self.__class__.action_class
        self.caption = self.__class__.caption

    def get_report_generator(self):
        self.action_class = getattr(sys.modules[self.getparam("modulename", __name__)], self.getparam("classname", ''))
        gen = XferPrintAction.get_report_generator(self)
        own_struct = LegalEntity.objects.get(id=1)
        gen.title = "{[u]}{[b]}%s{[/b]}{[/u]}{[br/]}{[i]}%s{[/i]}{[br/]}{[b]}%s{[/b]}" % (
            own_struct, self.action_class.caption, formats.date_format(date.today(), "DATE_FORMAT"))
        gen.page_width = 297
        gen.page_height = 210
        return gen


class CostAccountingReport(FiscalYearReport):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'

    def fillresponse(self):
        for self.item in self.items:
            self.new_tab(six.text_type(self.item))
            self.fill_header()
            self.calcul_table()
            self.fill_body()
        self.fill_buttons()

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('left', _('Expenses'))
        self.grid.add_header('left_n', _('Value'))
        self.grid.add_header('left_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header('left_n_1', _('Last'))
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Revenues'))
        self.grid.add_header('right_n', _('Value'))
        self.grid.add_header('right_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header('right_n_1', _('Last'))

    def fill_filterheader(self):
        pass

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
        lbl.set_location(2, 2, 4)
        self.add_component(lbl)
        self.filltab_from_model(1, 6, True, [(
            (_('total revenue'), 'total_revenue'), (_('total expense'), 'total_expense'))])
        self.filter = Q(entry__costaccounting=self.item)
        self.fill_filterCode()
        self.fill_filterheader()
        self.define_gridheader()


@ActionsManage.affect_grid(_("Report"), 'images/print.png', unique=SELECT_MULTI, modal=FORMTYPE_NOMODAL)
@MenuManage.describ('accounting.change_entryaccount')
class CostAccountingIncomeStatement(CostAccountingReport, FiscalYearIncomeStatement):
    caption = _("Income statement of cost accounting")

    def fill_header(self):
        CostAccountingReport.fill_header(self)

    def fill_filterheader(self):
        if self.item.last_costaccounting is not None:
            self.lastfilter = Q(
                entry__costaccounting=self.item.last_costaccounting)
            lbl = XferCompLabelForm('sep_last')
            lbl.set_value("{[br/]}{[br/]}")
            lbl.set_location(2, 11, 3)
            self.add_component(lbl)
            lbl = XferCompLabelForm('lbllast')
            lbl.set_value_as_name(_("Last"))
            lbl.set_location(1, 12)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last')
            lbl.set_value(six.text_type(self.item.last_costaccounting))
            lbl.set_location(2, 12, 4)
            self.add_component(lbl)
            old_accounting = self.item
            self.item = self.item.last_costaccounting
            try:
                self.filltab_from_model(1, 13, True, [(
                    (_('total revenue'), 'total_revenue'), (_('total expense'), 'total_expense'))])
            finally:
                self.item = old_accounting

    def calcul_table(self):
        self.budgetfilter_right = Q(cost_accounting=self.item) & Q(code__regex=current_system_account().get_revenue_mask())
        self.budgetfilter_left = Q(cost_accounting=self.item) & Q(code__regex=current_system_account().get_expence_mask())
        self._add_left_right_accounting(Q(account__type_of_account=4), Q(account__type_of_account=3), True)


@ActionsManage.affect_grid(_("Ledger"), 'images/print.png', unique=SELECT_MULTI, modal=FORMTYPE_NOMODAL)
@MenuManage.describ('accounting.change_entryaccount')
class CostAccountingLedger(CostAccountingReport, FiscalYearLedger):
    caption = _("Ledger of cost accounting")
    add_filtering = True

    def fill_header(self):
        CostAccountingReport.fill_header(self)

    def define_gridheader(self):
        FiscalYearLedger.define_gridheader(self)

    def calcul_table(self):
        FiscalYearLedger.calcul_table(self)


@ActionsManage.affect_grid(_("Trial balance"), 'images/print.png', unique=SELECT_MULTI, modal=FORMTYPE_NOMODAL)
@MenuManage.describ('accounting.change_entryaccount')
class CostAccountingTrialBalance(CostAccountingReport, FiscalYearTrialBalance):
    caption = _("Trial balance of cost accounting")
    add_filtering = True

    def fill_header(self):
        CostAccountingReport.fill_header(self)

    def define_gridheader(self):
        FiscalYearTrialBalance.define_gridheader(self)

    def calcul_table(self):
        FiscalYearTrialBalance.calcul_table(self)
