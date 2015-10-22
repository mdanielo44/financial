# -*- coding: utf-8 -*-
'''
diacamma.payoff models package

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

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.models import LucteriosModel

from diacamma.accounting.models import EntryAccount, FiscalYear, Third, Journal,\
    ChartsAccount, EntryLineAccount
from diacamma.accounting.tools import format_devise, currency_round,\
    current_system_account
from lucterios.framework.error import LucteriosException, IMPORTANT
from django.utils import six
from lucterios.CORE.parameters import Params


class Supporting(LucteriosModel):

    fiscal_year = models.ForeignKey(
        FiscalYear, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    third = models.ForeignKey(
        Third, verbose_name=_('third'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    @classmethod
    def get_payoff_fields(cls):
        return ['payoff_set', ((_('total payed'), 'total_payed'), (_('rest to pay'), 'total_rest_topay'))]

    @classmethod
    def get_print_fields(cls):
        return ['payoff_set', (_('total payed'), 'total_payed'), (_('rest to pay'), 'total_rest_topay')]

    class Meta(object):
        verbose_name = _('supporting')
        verbose_name_plural = _('supporting')

    def get_total(self):
        raise Exception('no implemented!')

    def is_revenu(self):
        raise Exception('no implemented!')

    def get_total_payed(self):
        val = 0
        for payoff in self.payoff_set.all():
            val += currency_round(payoff.amount)
        return val

    @property
    def total_payed(self):
        return format_devise(self.get_total_payed(), 5)

    def get_total_rest_topay(self):
        return self.get_total() - self.get_total_payed()

    @property
    def total_rest_topay(self):
        return format_devise(self.get_total_rest_topay(), 5)


class BankAccount(LucteriosModel):
    designation = models.TextField(_('designation'), null=False)
    reference = models.CharField(_('reference'), max_length=200, null=False)
    account_code = models.CharField(
        _('account code'), max_length=50, null=False)

    @classmethod
    def get_default_fields(cls):
        return ["designation", "reference", "account_code"]

    def __str__(self):
        return self.designation

    class Meta(object):
        verbose_name = _('bank account')
        verbose_name_plural = _('bank accounts')


class Payoff(LucteriosModel):
    supporting = models.ForeignKey(
        Supporting, verbose_name=_('supporting'), null=False, db_index=True, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_('date'), null=False)
    amount = models.DecimalField(verbose_name=_('amount'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    mode = models.IntegerField(verbose_name=_('mode'),
                               choices=((0, _('cash')), (1, _('cheque')), (2, _('transfer')), (3, _('crédit card')), (4, _('other'))), null=False, default=0, db_index=True)
    payer = models.CharField(_('payer'), max_length=150, null=True, default='')
    reference = models.CharField(
        _('reference'), max_length=100, null=True, default='')
    entry = models.ForeignKey(
        EntryAccount, verbose_name=_('entry'), null=True, default=None, db_index=True, on_delete=models.SET_NULL)
    bank_account = models.ForeignKey(BankAccount, verbose_name=_(
        'bank account'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    @classmethod
    def get_default_fields(cls):
        return ["date", (_('value'), "value"), "mode", "reference", "payer"]

    @classmethod
    def get_edit_fields(cls):
        return ["date", "amount", "payer", "mode", "bank_account", "reference"]

    @property
    def value(self):
        return format_devise(self.amount, 5)

    def delete_accounting(self):
        if self.entry is not None:
            payoff_entry = self.entry
            if payoff_entry.close:
                raise LucteriosException(
                    IMPORTANT, _("an entry associated to this payoff is closed!"))
            self.entry = None
            payoff_entry.delete()

    def generate_accounting(self):
        supporting = self.supporting.get_final_child()
        if supporting.is_revenu():
            is_revenu = -1
        else:
            is_revenu = 1
        fiscal_year = FiscalYear.get_current()
        new_entry = EntryAccount.objects.create(
            year=fiscal_year, date_value=self.date, designation=_(
                "payoff for %s") % six.text_type(supporting),
            journal=Journal.objects.get(id=4))
        accounts = supporting.third.accountthird_set.filter(
            code__regex=current_system_account().get_customer_mask())
        if len(accounts) == 0:
            raise LucteriosException(
                IMPORTANT, _("third has not customer account"))
        third_account = ChartsAccount.get_account(
            accounts[0].code, fiscal_year)
        if third_account is None:
            raise LucteriosException(
                IMPORTANT, _("third has not customer account"))
        EntryLineAccount.objects.create(
            account=third_account, amount=is_revenu * float(self.amount), third=supporting.third, entry=new_entry)
        if self.bank_account is None:
            cash_code = Params.getvalue("payoff-cash-account")
        else:
            cash_code = self.bank_account.account_code
        cash_account = ChartsAccount.get_account(cash_code, fiscal_year)
        if cash_account is None:
            raise LucteriosException(
                IMPORTANT, _("cash-account is not defined!"))
        EntryLineAccount.objects.create(
            account=cash_account, amount=-1 * is_revenu * float(self.amount), entry=new_entry)
        self.entry = new_entry

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, do_generate=True):
        if not force_insert and do_generate:
            self.delete_accounting()
            self.generate_accounting()
        return LucteriosModel.save(self, force_insert, force_update, using, update_fields)

    def delete(self, using=None):
        self.delete_accounting()
        LucteriosModel.delete(self, using)

    class Meta(object):
        verbose_name = _('payoff')
        verbose_name_plural = _('payoffs')
