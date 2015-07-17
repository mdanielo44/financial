# -*- coding: utf-8 -*-
'''
Describe database model for Django

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

from lucterios.framework.models import LucteriosModel, get_value_converted, \
    get_value_if_choices
from lucterios.contacts.models import AbstractContact  # pylint: disable=no-name-in-module,import-error
from lucterios.framework.tools import ActionsManage
from django.utils import six
from datetime import date
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.parameters import Params

class Third(LucteriosModel):
    contact = models.ForeignKey('contacts.AbstractContact', verbose_name=_('contact'), null=False)
    status = models.IntegerField(verbose_name=_('status'), choices=((0, _('Enable')), (1, _('Disable'))))

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
        from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_NO
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
        fiscal_years = FiscalYear.objects.order_by('end') # pylint: disable=no-member
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
        if self.id is None and (len(FiscalYear.objects.all()) == 0): # pylint: disable=no-member
            self.is_actif = True
        return

    def __str__(self):
        status = get_value_if_choices(self.status, self._meta.get_field_by_name('status'))  # pylint: disable=protected-access,no-member
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
        # pylint: disable=no-self-use
        return 0

    def get_current_validated(self):
        # pylint: disable=no-self-use
        return 34.61

    @property
    def last_year_total(self):
        return format_devise(self.get_last_year_total(), 2)

    @property
    def current_total(self):
        return format_devise(self.get_current_total(), 2)

    @property
    def current_validated(self):
        return format_devise(self.get_current_validated(), 2)

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('charts of account')
        verbose_name_plural = _('charts of accounts')

def format_devise(amount, mode):
    # pylint: disable=too-many-branches
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
    else:
        if mode < 5:
            amount_text = currency_format % abs(amount)
        else:
            amount_text = currency_format % amount
        result = result + amount_text + currency_short
    if mode == 2:
        result = result + '{[/font]}'
    return result
