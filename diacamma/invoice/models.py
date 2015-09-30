# -*- coding: utf-8 -*-
'''
diacamma.invoice models package

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
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from lucterios.framework.models import LucteriosModel, get_value_if_choices, \
    get_value_converted
from diacamma.accounting.models import FiscalYear, Third, EntryAccount, \
    CostAccounting, Journal, EntryLineAccount, ChartsAccount
from django.core.validators import MaxValueValidator, MinValueValidator
from diacamma.accounting.tools import current_system_account, format_devise, currency_round
from django.db.models.aggregates import Max
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.parameters import Params
from re import match
from datetime import date


class Vat(LucteriosModel):
    name = models.CharField(_('name'), max_length=20)
    rate = models.DecimalField(_('rate'), max_digits=6, decimal_places=2, default=10.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(100.0)])
    isactif = models.BooleanField(
        verbose_name=_('is actif'), default=True)

    def __str__(self):
        return six.text_type(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "rate", "isactif"]

    class Meta(object):
        verbose_name = _('VAT')
        verbose_name_plural = _('VATs')


class Article(LucteriosModel):
    reference = models.CharField(_('reference'), max_length=20)
    designation = models.TextField(_('designation'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    unit = models.CharField(_('unit'), null=True, default='', max_length=10)
    isdisabled = models.BooleanField(
        verbose_name=_('is disabled'), default=False)
    sell_account = models.CharField(_('sell account'), max_length=50)
    vat = models.ForeignKey(
        Vat, verbose_name=_('vat'), null=True, default=None, on_delete=models.PROTECT)

    def __str__(self):
        return six.text_type(self.reference)

    @classmethod
    def get_default_fields(cls):
        return ["reference", "designation", (_('price'), "price_txt"), 'unit', "isdisabled", 'sell_account']

    @classmethod
    def get_edit_fields(cls):
        return ["reference", "designation", ("price", "unit"), ("sell_account", 'vat'), "isdisabled"]

    @classmethod
    def get_show_fields(cls):
        return ["reference", "designation", ("price", "unit"), ("sell_account", 'vat'), "isdisabled"]

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

    class Meta(object):
        verbose_name = _('article')
        verbose_name_plural = _('articles')


class Bill(LucteriosModel):
    fiscal_year = models.ForeignKey(
        FiscalYear, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    bill_type = models.IntegerField(verbose_name=_('bill type'),
                                    choices=((0, _('quotation')), (1, _('bill')), (2, _('asset')), (3, _('receipt'))), null=False, default=0, db_index=True)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    third = models.ForeignKey(
        Third, verbose_name=_('third'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    comment = models.TextField(_('comment'), null=True, default="")
    status = models.IntegerField(verbose_name=_('status'),
                                 choices=((0, _('building')), (1, _('valid')), (2, _('cancel')), (3, _('archive'))), null=False, default=0, db_index=True)
    entry = models.ForeignKey(
        EntryAccount, verbose_name=_('entry'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    cost_accounting = models.ForeignKey(
        CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    def __str__(self):
        billtype = get_value_if_choices(
            self.bill_type, self.get_field_by_name('bill_type'))
        return "%s %s - %s" % (billtype, self.num_txt, get_value_converted(self.date))

    @classmethod
    def get_default_fields(cls):
        return ["bill_type", (_('numeros'), "num_txt"), "date", "third", "comment", (_('total'), 'total'), "status"]

    @classmethod
    def get_edit_fields(cls):
        return ["bill_type", "date", "comment"]

    @classmethod
    def get_show_fields(cls):
        return [((_('numeros'), "num_txt"), "date"), "third", "detail_set", "comment", ("status", (_('total'), 'total'))]

    def get_total(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_total()
        return val

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    @property
    def num_txt(self):
        if (self.fiscal_year is None) or (self.num is None):
            return None
        else:
            return "%s-%d" % (self.fiscal_year.letter, self.num)

    def get_info_state(self):
        info = []
        if self.status == 0:
            if self.third is None:
                info.append(six.text_type(_("no third selected")))
            else:
                accounts = self.third.accountthird_set.filter(
                    code__regex=current_system_account().get_customer_mask())
                if (len(accounts) == 0) or (ChartsAccount.get_account(accounts[0].code, FiscalYear.get_current()) is None):
                    info.append(
                        six.text_type(_("third has not customer account")))
        details = self.detail_set.all()
        if len(details) == 0:
            info.append(six.text_type(_("no detail")))
        else:
            for detail in details:
                if detail.article is not None:
                    detail_code = detail.article.sell_account
                else:
                    detail_code = Params.getvalue(
                        "invoice-default-sell-account")
                if match(current_system_account().get_revenue_mask(), detail_code) is not None:
                    detail_account = ChartsAccount.get_account(
                        detail_code, FiscalYear.get_current())
                else:
                    detail_account = None
                if detail_account is None:
                    info.append(
                        six.text_type(_("article has code account unknown!")))
        fiscal_year = FiscalYear.get_current()
        if (fiscal_year.begin > self.date) or (fiscal_year.end < self.date):
            info.append(
                six.text_type(_("date not include in current fiscal year")))
        return "{[br/]}".join(info)

    def can_delete(self):
        if self.status != 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    def generate_entry(self):
        if self.bill_type == 2:
            is_bill = -1
        else:
            is_bill = 1
        self.entry = EntryAccount.objects.create(
            year=self.fiscal_year, date_value=self.date, designation=self.__str__(),
            journal=Journal.objects.get(id=3))
        accounts = self.third.accountthird_set.filter(
            code__regex=current_system_account().get_customer_mask())
        if len(accounts) == 0:
            raise LucteriosException(
                IMPORTANT, _("third has not customer account"))
        third_account = ChartsAccount.get_account(
            accounts[0].code, self.fiscal_year)
        if third_account is None:
            raise LucteriosException(
                IMPORTANT, _("third has not customer account"))
        EntryLineAccount.objects.create(
            account=third_account, amount=is_bill * self.get_total(), third=self.third, entry=self.entry)

        remise_total = 0
        detail_list = {}
        for detail in self.detail_set.all():
            if detail.article is not None:
                detail_code = detail.article.sell_account
            else:
                detail_code = Params.getvalue("invoice-default-sell-account")
            detail_account = ChartsAccount.get_account(
                detail_code, self.fiscal_year)
            if detail_account is None:
                raise LucteriosException(
                    IMPORTANT, _("article has code account unknown!"))
            if detail_account.id not in detail_list.keys():
                detail_list[detail_account.id] = [detail_account, 0]
            detail_list[detail_account.id][
                1] += currency_round(detail.price * detail.quantity)
            remise_total += currency_round(detail.reduce)
        if remise_total > 0.001:
            remise_code = Params.getvalue("invoice-reduce-account")
            remise_account = ChartsAccount.get_account(
                remise_code, self.fiscal_year)
            if remise_account is None:
                raise LucteriosException(
                    IMPORTANT, _("reduce-account is not defined!"))
            EntryLineAccount.objects.create(
                account=remise_account, amount=-1 * is_bill * remise_total, entry=self.entry)
        for detail_item in detail_list.values():
            EntryLineAccount.objects.create(
                account=detail_item[0], amount=is_bill * detail_item[1], entry=self.entry)

    def valid(self):
        if (self.status == 0) and (self.get_info_state() == ''):
            self.fiscal_year = FiscalYear.get_current()
            bill_list = self.fiscal_year.bill_set.filter(
                bill_type=self.bill_type).exclude(status=0)
            val = bill_list.aggregate(Max('num'))
            if val['num__max'] is None:
                self.num = 1
            else:
                self.num = val['num__max'] + 1
            self.status = 1
            if self.bill_type != 0:
                self.generate_entry()
            self.save()

    def cancel(self):
        if (self.status == 1) and (self.bill_type in (1, 3)):
            new_asset = Bill.objects.create(
                bill_type=2, date=date.today(), third=self.third, status=0)
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_asset
                detail.save()
            self.status = 2
            self.save()
            return new_asset.id
        else:
            return None

    def archive(self):
        if self.status == 1:
            self.status = 3
            self.save()

    class Meta(object):
        verbose_name = _('bill')
        verbose_name_plural = _('bills')


class Detail(LucteriosModel):
    bill = models.ForeignKey(
        Bill, verbose_name=_('bill'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, verbose_name=_('article'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    unit = models.CharField(
        verbose_name=_('unit'), null=False, default='', max_length=10)
    quantity = models.DecimalField(verbose_name=_('quantity'), max_digits=10, decimal_places=2, default=1.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.99)])
    reduce = models.DecimalField(verbose_name=_('reduce'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])

    def __str__(self):
        return "[%s] %s:%f" % (six.text_type(self.reference), six.text_type(self.designation), self.price)

    @classmethod
    def get_default_fields(cls):
        return ["article", "designation", (_('price'), "price_txt"), "unit", "quantity", (_('reduce'), "reduce_txt"), (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ["article", "designation", "price", "unit", "quantity", "reduce"]

    @classmethod
    def get_show_fields(cls):
        return ["article", "designation", (_('price'), "price_txt"), "unit", "quantity", (_('reduce'), "reduce_txt")]

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

    @property
    def reduce_txt(self):
        if self.reduce > 0.0001:
            return "%s(%.2f%%)" % (format_devise(self.reduce, 5), 100 * self.reduce / (self.price * self.quantity))
        else:
            return None

    def get_total(self):
        return currency_round(self.price * self.quantity - self.reduce)

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    class Meta(object):
        verbose_name = _('detail')
        verbose_name_plural = _('details')
        default_permissions = []
