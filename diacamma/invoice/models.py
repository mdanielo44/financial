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

from lucterios.framework.models import LucteriosModel
from diacamma.accounting.models import FiscalYear, Third, EntryAccount,\
    CostAccounting
from django.core.validators import MaxValueValidator, MinValueValidator


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
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=3, default=10.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    unit = models.CharField(_('unit'), max_length=10)
    isdisabled = models.BooleanField(
        verbose_name=_('is disabled'), default=False)
    sell_account = models.CharField(_('sell account'), max_length=50)
    vat = models.ForeignKey(
        Vat, verbose_name=_('vat'), null=True, default=None, on_delete=models.PROTECT)

    def __str__(self):
        return "[%s] %s" % (six.text_type(self.reference), six.text_type(self.designation))

    @classmethod
    def get_default_fields(cls):
        return ["reference", "designation", "price", "isdisabled"]

    @classmethod
    def get_edit_fields(cls):
        return ["reference", "designation", ("price", "unit"), "sell_account", "isdisabled"]

    @classmethod
    def get_show_fields(cls):
        return ["reference", "designation", ("price", "unit"), "sell_account", "isdisabled"]

    class Meta(object):
        verbose_name = _('article')
        verbose_name_plural = _('articles')


class Bill(LucteriosModel):
    fiscal_year = models.ForeignKey(
        FiscalYear, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    bill_type = models.IntegerField(verbose_name=_('bill type'),
                                    choices=((0, 'quotation'), (1, 'bill'), (2, 'asset'), (3, 'batch bill'),
                                             (4, 'receipt')), null=True, db_index=True)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=True)
    third = models.ForeignKey(
        Third, verbose_name=_('third'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    comment = models.TextField(_('comment'), default="")
    status = models.IntegerField(verbose_name=_('status'),
                                 choices=((0, 'building'), (1, 'valid'), (2, 'cancel'), (3, 'close')), null=True, db_index=True)
    entry = models.ForeignKey(
        EntryAccount, verbose_name=_('entry'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    cost_accounting = models.ForeignKey(
        CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    def __str__(self):
        return "[%s] %s %d" % (self.bill_type, self.date, self.num)

    @classmethod
    def get_default_fields(cls):
        return ["bill_type", "date", "status", "num", "third"]

    @classmethod
    def get_edit_fields(cls):
        return ["bill_type", "date", "comment"]

    @classmethod
    def get_show_fields(cls):
        return [("bill_type", "status"), ("date", "num"), "third", "detail_set", "comment"]

    class Meta(object):
        verbose_name = _('bill')
        verbose_name_plural = _('bills')


class Detail(LucteriosModel):
    bill = models.ForeignKey(
        Bill, verbose_name=_('bill'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(_('designation'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=3, default=10.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    unit = models.CharField(_('unit'), max_length=10)
    quantity = models.FloatField(_('quantity'))
    reduce = models.FloatField(_('reduce'))

    def __str__(self):
        return "[%s] %s:%f" % (six.text_type(self.reference), six.text_type(self.designation), self.price)

    @classmethod
    def get_default_fields(cls):
        return ["article", "desingation", "price", "unit", "quantity", "reduce"]

    @classmethod
    def get_edit_fields(cls):
        return ["article", "desingation", "price", "unit", "quantity", "reduce"]

    @classmethod
    def get_show_fields(cls):
        return ["article", "desingation", "price", "unit", "quantity", "reduce"]

    class Meta(object):
        verbose_name = _('detail')
        verbose_name_plural = _('details')
        default_permissions = []


class BatchBill(Bill):
    thirds = models.ManyToManyField(Third, verbose_name=_('thirds'))

    @classmethod
    def get_default_fields(cls):
        return ["bill_type", "date", "status", "num", "thirds"]

    @classmethod
    def get_show_fields(cls):
        return [("bill_type", "status"), ("date", "num"), "thirds", "detail_set", "comment"]

    class Meta(object):
        verbose_name = _('bill batch')
        verbose_name_plural = _('bill batches')
        default_permissions = []
