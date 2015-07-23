# -*- coding: utf-8 -*-
'''
Describe database model for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
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

from datetime import date

from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from lucterios.framework.models import LucteriosModel, get_value_converted, get_value_if_choices
from lucterios.framework.error import LucteriosException, IMPORTANT

from lucterios.CORE.parameters import Params
from lucterios.contacts.models import AbstractContact  # pylint: disable=no-name-in-module,import-error
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum

class Third(LucteriosModel):
    contact = models.ForeignKey('contacts.AbstractContact', verbose_name=_('contact'), null=False)
    status = models.IntegerField(verbose_name=_('status'), choices=((0, _('Enable')), (1, _('Disable'))))

    def __str__(self):
        return six.text_type(self.contact.get_final_child())  # pylint: disable=no-member

    @classmethod
    def get_default_fields(cls):
        return ["contact", "accountthird_set"]

    @classmethod
    def get_edit_fields(cls):
        return ["status"]

    @classmethod
    def get_show_fields(cls):
        return {'':['contact'], _('001@AccountThird information'):["status", "accountthird_set"]}

    @classmethod
    def get_search_fields(cls):
        result = []
        for field_name in AbstractContact.get_search_fields():
            if not isinstance(field_name, tuple):
                result.append("contact." + field_name)

        result.extend(["status", "accountthird_set.code"])
        return result

    def show(self, xfer):
        from lucterios.framework.xfercomponents import XferCompButton
        from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_NO, ActionsManage
        xfer.tab = 0
        old_item = xfer.item
        xfer.item = self.contact.get_final_child()  # pylint: disable=no-member
        xfer.filltab_from_model(1, 1, True, ['address', ('postal_code', 'city'), 'country', ('tel1', 'tel2')])
        btn = XferCompButton('show')
        btn.set_location(2, 5, 3, 1)
        modal_name = xfer.item.__class__.__name__
        btn.set_action(xfer.request, ActionsManage.get_act_changed(modal_name, 'show', _('Show'), 'images/edit.png'), \
                {'modal':FORMTYPE_MODAL, 'close':CLOSE_NO, 'params':{modal_name.lower():six.text_type(xfer.item.id)}})
        xfer.add_component(btn)
        xfer.item = old_item

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('third')
        verbose_name_plural = _('thirds')

class AccountThird(LucteriosModel):
    third = models.ForeignKey(Third, verbose_name=_('third'), null=False)
    code = models.CharField(_('code'), max_length=50)

    def __str__(self):
        return self.code

    @classmethod
    def get_default_fields(cls):
        return ["code"]

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        default_permissions = []

class FiscalYear(LucteriosModel):
    begin = models.DateField(verbose_name=_('begin'))
    end = models.DateField(verbose_name=_('end'))
    status = models.IntegerField(verbose_name=_('status'), choices=((0, _('building')), (1, _('running')), (2, _('finished'))), default=0)
    is_actif = models.BooleanField(verbose_name=_('actif'), default=False)
    last_fiscalyear = models.ForeignKey('FiscalYear', verbose_name=_('last fiscal year'), null=True, on_delete=models.CASCADE)

    def init_dates(self):
        fiscal_years = FiscalYear.objects.order_by('end')  # pylint: disable=no-member
        if len(fiscal_years) == 0:
            self.begin = date.today()
        else:
            last_fiscal_year = fiscal_years[len(fiscal_years) - 1]
            self.begin = date(last_fiscal_year.end.year, last_fiscal_year.end.month, last_fiscal_year.end.day + 1)
        self.end = date(self.begin.year + 1, self.begin.month, self.begin.day - 1)

    def can_delete(self):
        if self.status == 2:
            return _('Fiscal year finished!')
        else:
            return ''

    @classmethod
    def get_default_fields(cls):
        return ['begin', 'end', 'status', 'is_actif']

    @classmethod
    def get_edit_fields(cls):
        return ['status', 'begin', 'end']

    def edit(self, xfer):
        xfer.change_to_readonly('status')
        if self.status != 0:
            xfer.change_to_readonly('begin')
        if self.status == 2:
            xfer.change_to_readonly('end')

    def before_save(self, xfer):
        # pylint: disable=unused-argument,no-self-use
        if self.end < self.begin:
            raise LucteriosException(IMPORTANT, _("end of fiscal year must be after begin!"))
        if self.id is None and (len(FiscalYear.objects.all()) == 0):  # pylint: disable=no-member
            self.is_actif = True
        return

    @property
    def total_revenue(self):
        val = EntryLineAccount.objects.filter(account__type_of_account=3, account__year=self).aggregate(Sum('amount'))  # pylint: disable=no-member
        if val['amount__sum'] is None:
            return 0
        else:
            return val['amount__sum']

    @property
    def total_expense(self):
        val = EntryLineAccount.objects.filter(account__type_of_account=4, account__year=self).aggregate(Sum('amount'))  # pylint: disable=no-member
        if val['amount__sum'] is None:
            return 0
        else:
            return val['amount__sum']

    @property
    def total_cash(self):
        val = EntryLineAccount.objects.filter(account__code__startswith='5', account__year=self).aggregate(Sum('amount'))  # pylint: disable=no-member
        if val['amount__sum'] is None:
            return 0
        else:
            return val['amount__sum']

    @property
    def total_cash_close(self):
        val = EntryLineAccount.objects.filter(entry__close=True, account__code__startswith='5', account__year=self).aggregate(Sum('amount'))  # pylint: disable=no-member
        if val['amount__sum'] is None:
            return 0
        else:
            return val['amount__sum']

    @property
    def total_result_text(self):
        value = {}
        value['revenue'] = format_devise(self.total_revenue, 5)

        value['expense'] = format_devise(self.total_expense, 5)
        value['result'] = format_devise(self.total_revenue - self.total_expense, 5)
        value['cash'] = format_devise(self.total_cash, 5)
        value['closed'] = format_devise(self.total_cash_close, 5)
        res_text = _('{[b]}Revenue:{[/b]} %(revenue)s - {[b]}Expense:{[/b]} %(expense)s = {[b]}Result:{[/b]} %(result)s | {[b]}Cash:{[/b]} %(cash)s - {[b]}Closed:{[/b]} %(closed)s')
        return res_text % value

    @classmethod
    def get_current(cls, select_year=None):
        if select_year is None:
            year = FiscalYear.objects.get(is_actif=True)  # pylint: disable=no-member
        else:
            year = FiscalYear.objects.get(id=select_year)  # pylint: disable=no-member
        return year

    def get_account_list(self, num_cpt_txt):
        account_list = {}
        current_account = None
        for account in self.chartsaccount_set.all().filter(code__startswith=num_cpt_txt):  # pylint: disable=no-member
            account_list[account.id] = six.text_type(account)
            if current_account is None:
                current_account = account
        return account_list, current_account

    def __str__(self):
        status = get_value_if_choices(self.status, self._meta.get_field('status'))  # pylint: disable=protected-access,no-member
        return _("Fiscal year from %(begin)s to %(end)s [%(status)s]") % {'begin':get_value_converted(self.begin), 'end':get_value_converted(self.end), 'status':status}

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('fiscal year')
        verbose_name_plural = _('fiscal years')

class ChartsAccount(LucteriosModel):
    code = models.CharField(_('code'), max_length=50)
    name = models.CharField(_('name'), max_length=200)
    year = models.ForeignKey('FiscalYear', verbose_name=_('fiscal year'), null=False, on_delete=models.CASCADE)
    type_of_account = models.IntegerField(verbose_name=_('type of account'), \
            choices=((0, _('Asset')), (1, _('Liability')), (2, _('Equity')), (3, _('Revenue')), (4, _('Expense')), (5, _('Contra-accounts'))), null=True)

    @classmethod
    def get_default_fields(cls):
        return ['code', 'name', (_('total of last year'), 'last_year_total'), \
                (_('total current'), 'current_total'), (_('total validated'), 'current_validated')]

    @classmethod
    def get_edit_fields(cls):
        return ['code', 'name', 'type_of_account']

    @classmethod
    def get_show_fields(cls):
        return ['code', 'name', 'type_of_account']

    def __str__(self):
        return "[%s] %s" % (self.code, self.name)

    def get_last_year_total(self):
        # pylint: disable=no-self-use
        return -24.98

    def get_current_total(self):
        val = self.entrylineaccount_set.all().aggregate(Sum('amount'))  # pylint: disable=no-member
        if val['amount__sum'] is None:
            return 0
        else:
            return val['amount__sum']

    def get_current_validated(self):
        val = self.entrylineaccount_set.filter(entry__close=True).aggregate(Sum('amount'))  # pylint: disable=no-member
        if val['amount__sum'] is None:
            return 0
        else:
            return val['amount__sum']

    def credit_debit_way(self):
        if self.type_of_account in [0, 4]:
            return -1
        else:
            return 1

    @property
    def last_year_total(self):
        return format_devise(self.credit_debit_way() * self.get_last_year_total(), 2)

    @property
    def current_total(self):
        return format_devise(self.credit_debit_way() * self.get_current_total(), 2)

    @property
    def current_validated(self):
        return format_devise(self.credit_debit_way() * self.get_current_validated(), 2)

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('charts of account')
        verbose_name_plural = _('charts of accounts')
        ordering = ['year', 'code']

class EntryAccount(LucteriosModel):
    year = models.ForeignKey('FiscalYear', verbose_name=_('fiscal year'), null=False, on_delete=models.CASCADE)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)

    date_entry = models.DateField(verbose_name=_('date entry'), null=True)
    date_value = models.DateField(verbose_name=_('date value'), null=True)
    designation = models.CharField(_('name'), max_length=200)
    close = models.BooleanField(verbose_name=_('close'), default=False)

    @classmethod
    def get_default_fields(cls):
        return ['year', 'close', 'num', 'date_entry', 'date_value', 'designation']

    @classmethod
    def get_edit_fields(cls):
        return ['date_value', 'designation']

    @classmethod
    def get_show_fields(cls):
        return ['num', 'date_entry', 'date_value', 'designation']

    def can_delete(self):
        if self.close:
            return _('entries of account closed!')
        else:
            return ''

    def show(self, xfer):
        from lucterios.framework.xfercomponents import XferCompLabelForm
        last_row = xfer.get_max_row() + 10

        lbl = XferCompLabelForm('sep3')
        lbl.set_location(0, last_row + 1, 6)
        lbl.set_value("{[center]}{[hr/]}{[/center]}")
        xfer.add_component(lbl)
        xfer.filltab_from_model(1, last_row + 2, True, ['entrylineaccount_set'])
        grid_lines = xfer.get_components('entrylineaccount_set')
        grid_lines.actions = []

    def get_serial(self, entrylines=None):
        if entrylines is None:
            entrylines = self.entrylineaccount_set.all()  # pylint: disable=no-member
        serial_val = ''
        for line in entrylines:
            if serial_val != '':
                serial_val += '\n'
            serial_val += line.get_serial()
        return serial_val

    def get_entrylineaccounts(self, serial_vals):
        res = QuerySet(model=EntryLineAccount)
        res._result_cache = []  # pylint: disable=protected-access
        for serial_val in serial_vals.split('\n'):
            if serial_val != '':
                new_line = EntryLineAccount.get_entrylineaccount(serial_val)
                new_line.entry = self
                res._result_cache.append(new_line)  # pylint: disable=protected-access
        return res

    def remove_entrylineaccounts(self, serial_vals, entrylineid):
        lines = self.get_entrylineaccounts(serial_vals)
        line_idx = -1
        for idx in range(len(lines)):
            if lines[idx].id == entrylineid:
                line_idx = idx
        del lines._result_cache[line_idx]  # pylint: disable=protected-access
        return self.get_serial(lines)

    def is_serial_changed(self, serial_vals):
        res = True
        serial = self.get_entrylineaccounts(serial_vals)
        current = self.entrylineaccount_set.all()  # pylint: disable=no-member
        if len(serial) == len(current):
            for idx in range(len(current)):
                res = res and current[idx].equals(serial[idx])
        else:
            res = False
        return res

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('entry of account')
        verbose_name_plural = _('entries of account')

class EntryLineAccount(LucteriosModel):

    account = models.ForeignKey('ChartsAccount', verbose_name=_('account'), null=False, on_delete=models.CASCADE)
    entry = models.ForeignKey('EntryAccount', verbose_name=_('entry'), null=False, on_delete=models.CASCADE)
    amount = models.FloatField(_('amount'))
    reference = models.CharField(_('reference'), max_length=100, null=True)
    third = models.ForeignKey('Third', verbose_name=_('entry'), null=True, on_delete=models.CASCADE)

    @classmethod
    def get_default_fields(cls):
        return [(_('account'), 'entry_account'), (_('debit'), 'debit'), (_('credit'), 'credit'), 'reference']

    @classmethod
    def get_edit_fields(cls):
        return ['entry.date_entry', 'entry.date_value', 'entry.designation', \
                    ((_('account'), 'entry_account'),), ((_('debit'), 'debit'),), ((_('credit'), 'credit'),)]

    @classmethod
    def get_show_fields(cls):
        return ['entry.date_entry', 'entry.date_value', 'entry.designation', \
                    ((_('account'), 'entry_account'),), ((_('debit'), 'debit'),), ((_('credit'), 'credit'),)]

    @property
    def entry_account(self):
        if self.third is None:
            return six.text_type(self.account)
        else:
            return "[%s %s]" % (self.account.code, six.text_type(self.third))  # pylint: disable=no-member

    def get_debit(self):
        try:
            return max((0, self.account.credit_debit_way() * self.amount))  # pylint: disable=no-member
        except ObjectDoesNotExist:
            return 0

    @property
    def debit(self):
        return format_devise(self.get_debit(), 0)

    def get_credit(self):
        try:
            return max((0, -1 * self.account.credit_debit_way() * self.amount))  # pylint: disable=no-member
        except ObjectDoesNotExist:
            return 0

    @property
    def credit(self):
        return format_devise(self.get_credit(), 0)

    def set_montant(self, debit_val, credit_val):
        if debit_val > 0:
            self.amount = debit_val * self.account.credit_debit_way()
        elif credit_val > 0:
            self.amount = -1 * credit_val * self.account.credit_debit_way()
        else:
            self.amount = 0

    def equals(self, other):
        res = self.id == other.id
        res = res and (self.account.id == other.account.id)
        res = res and (self.amount == other.amount)
        res = res and (self.reference == other.reference)
        if self.third is None:
            res = res and (other.third is None)
        else:
            res = res and (self.third.id == other.third.id)
        return res

    def get_serial(self):
        if self.third is None:
            third_id = 0
        else:
            third_id = self.third.id
        if self.reference is None:
            reference = 'None'
        else:
            reference = self.reference
        return "%d|%d|%d|%f|%s|" % (self.id, self.account.id, third_id, self.amount, reference)

    @classmethod
    def add_serial(cls, num_cpt, debit_val, credit_val, thirdid=0, reference=None):
        import time
        new_entry_line = cls()
        new_entry_line.id = -1 * int(time.time() * 60)  # pylint: disable=invalid-name,attribute-defined-outside-init
        new_entry_line.account = ChartsAccount.objects.get(id=num_cpt)  # pylint: disable=no-member
        if thirdid == 0:
            new_entry_line.third = None
        else:
            new_entry_line.third = Third.objects.get(id=thirdid)  # pylint: disable=no-member
        new_entry_line.set_montant(debit_val, credit_val)
        if reference == "None":
            new_entry_line.reference = None
        else:
            new_entry_line.reference = reference
        return new_entry_line.get_serial()

    @classmethod
    def get_entrylineaccount(cls, serial_val):
        serial_vals = serial_val.split('|')
        new_entry_line = cls()
        new_entry_line.id = int(serial_vals[0])  # pylint: disable=invalid-name,attribute-defined-outside-init
        new_entry_line.account = ChartsAccount.objects.get(id=int(serial_vals[1]))  # pylint: disable=no-member
        if int(serial_vals[2]) == 0:
            new_entry_line.third = None
        else:
            new_entry_line.third = Third.objects.get(id=int(serial_vals[2]))  # pylint: disable=no-member
        new_entry_line.amount = float(serial_vals[3])
        new_entry_line.reference = "|".join(serial_vals[4:-1])
        if new_entry_line.reference == "None":
            new_entry_line.reference = None
        return new_entry_line

    def _editaccount_for_line(self, xfer, init_col, init_row):
        # pylint: disable=too-many-locals
        from lucterios.framework.tools import CLOSE_NO, FORMTYPE_REFRESH
        from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompEdit, XferCompSelect
        num_cpt_txt = xfer.getparam('num_cpt_txt', '')
        num_cpt = xfer.getparam('num_cpt', 0)

        lbl = XferCompLabelForm('numCptlbl')
        lbl.set_location(init_col, init_row, 2)
        lbl.set_value_as_headername(_('account'))
        xfer.add_component(lbl)
        edt = XferCompEdit('num_cpt_txt')
        edt.set_location(init_col, init_row + 1, 2)
        edt.set_value(num_cpt_txt)
        edt.set_size(20, 25)
        edt.set_action(xfer.request, xfer.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
        xfer.add_component(edt)
        sel_val = {}
        current_account = None
        if num_cpt_txt != '':
            year = FiscalYear.get_current(xfer.getparam('year'))
            sel_val, current_account = year.get_account_list(num_cpt_txt)
        if num_cpt > 0:
            current_account = ChartsAccount.objects.get(id=num_cpt)  # pylint: disable=no-member
        sel = XferCompSelect('num_cpt')
        sel.set_location(init_col, init_row + 2, 2)
        sel.set_select(sel_val)
        sel.set_size(20, 150)
        sel.set_action(xfer.request, xfer.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
        if current_account is not None:
            sel.set_value(current_account.id)
            self.account = current_account
            self.set_montant(float(xfer.getparam('debit_val', 0.0)), float(xfer.getparam('credit_val', 0.0)))
        xfer.add_component(sel)
        return lbl, edt

    def edit_line(self, xfer):
        from lucterios.framework.xfercomponents import XferCompFloat, XferCompLabelForm
        currency_decimal = Params.getvalue("accounting-devise-prec")
        init_col = 0
        init_row = xfer.get_max_row() + 1

        self._editaccount_for_line(xfer, init_col, init_row)

        lbl = XferCompLabelForm('debitlbl')
        lbl.set_location(init_col + 2, init_row)
        lbl.set_value_as_name(_('debit'))
        xfer.add_component(lbl)
        edt = XferCompFloat('debit_val', -10000000, 10000000, currency_decimal)
        edt.set_location(init_col + 2, init_row + 1)
        edt.set_value(self.get_debit())
        edt.set_size(20, 75)
        xfer.add_component(edt)

        lbl = XferCompLabelForm('creditlbl')
        lbl.set_location(init_col + 3, init_row)
        lbl.set_value_as_name(_('credit'))
        xfer.add_component(lbl)
        edt = XferCompFloat('credit_val', -10000000, 10000000, currency_decimal)
        edt.set_location(init_col + 3, init_row + 1)
        edt.set_value(self.get_credit())
        edt.set_size(20, 75)
        xfer.add_component(edt)

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('entry line of account')
        verbose_name_plural = _('entry lines of account')
        default_permissions = []

def format_devise(amount, mode):
    # pylint: disable=too-many-branches
    # mode 0 25.45 => 25,45€ / -25.45 =>

    # mode 1 25.45 => Credit 25,45€ / -25.45 => Debit 25,45€
    # mode 2 25.45 => {[font color="green"]}Credit 25,45€{[/font]}     / -25.45 => {[font color="blue"]}Debit 25,45€{[/font]}

    # mode 3 25.45 => 25,45 / -25.45 => -25.45
    # mode 4 25.45 => 25,45€ / -25.45 => 25.45€
    # mode 5+ 25.45 => 25,45€ / -25.45 => -25.45€
    result = ''
    currency_short = Params.getvalue("accounting-devise")
    currency_decimal = Params.getvalue("accounting-devise-prec")
    currency_format = "%%0.%df" % currency_decimal
    currency_epsilon = pow(10, -1 * currency_decimal - 1)
    if (amount is None) or (abs(amount) < currency_epsilon):
        amount = 0
    if (abs(amount) >= currency_epsilon) or ((mode > 0) and (mode < 6)):
        if amount >= 0:
            if mode == 2:
                result = '{[font color="green"]}'
            if (mode == 1) or (mode == 2):
                result = '%s%s: ' % (result, _('Credit'))
        else:
            if mode == 2:
                result = result + '{[font color="blue"]}'
            if (mode == 1) or (mode == 2):
                result = '%s%s: ' % (result, _('Debit'))
    if mode == 3:
        result = currency_format % amount
    elif mode == 0:
        if amount >= currency_epsilon:
            result = currency_format % abs(amount) + currency_short
    else:
        if mode < 5:
            amount_text = currency_format % abs(amount)
        else:
            amount_text = currency_format % amount
        result = result + amount_text + currency_short
    if mode == 2:
        result = result + '{[/font]}'
    return result
