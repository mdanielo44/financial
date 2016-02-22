# -*- coding: utf-8 -*-
'''
diacamma.invoice views_conf package

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

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage
from lucterios.framework.xfercomponents import XferCompButton
from lucterios.framework import signal_and_lock
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.CORE.models import Parameter

from diacamma.accounting.tools import correct_accounting_code
from diacamma.invoice.models import Vat, Article


@ActionsManage.affect('Vat', 'list')
@MenuManage.describ('invoice.change_vat', FORMTYPE_NOMODAL, 'financial.conf', _('Management of parameters and configuration of invoice'))
class InvoiceConf(XferListEditor):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption = _("Invoice configuration")

    def fillresponse_header(self):
        self.new_tab(_('Parameters'))
        param_lists = ['invoice-vat-mode', 'invoice-default-sell-account', 'invoice-vatsell-account',
                       'invoice-reduce-account', 'invoice-account-third']
        Params.fill(self, param_lists, 1, 1)
        btn = XferCompButton('editparam')
        btn.set_location(1, self.get_max_row() + 1, 2, 1)
        btn.set_action(self.request, ParamEdit.get_action(
            _('Modify'), 'images/edit.png'), {'close': 0, 'params': {'params': param_lists}})
        self.add_component(btn)
        self.new_tab(_('VAT'))


@ActionsManage.affect('Vat', 'edit', 'add')
@MenuManage.describ('invoice.add_vat')
class VatAddModify(XferAddEditor):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption_add = _("Add VAT")
    caption_modify = _("Modify VAT")


@ActionsManage.affect('Vat', 'delete')
@MenuManage.describ('invoice.delete_vat')
class VatDel(XferDelete):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption = _("Delete VAT")


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_invoice(known_codes, accompt_returned):
    article_unknown = Article.objects.filter(
        isdisabled=False).exclude(sell_account__in=known_codes).values_list('sell_account', flat=True).distinct()
    param_unknown = Parameter.objects.filter(name__in=('invoice-default-sell-account', 'invoice-vatsell-account',
                                                       'invoice-reduce-account')).exclude(value__in=known_codes).values_list('value', flat=True).distinct()
    comptenofound = ""
    if (len(article_unknown) > 0):
        comptenofound = _("articles") + ":" + ",".join(article_unknown) + " "
    if (len(param_unknown) > 0):
        comptenofound += _("parameters") + ":" + ",".join(param_unknown)
    if comptenofound != "":
        accompt_returned.append(
            "- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Invoice'), comptenofound))
    return True


@signal_and_lock.Signal.decorate('param_change')
def paramchange_invoice(params):
    invoice_params = ['invoice-default-sell-account', 'invoice-vatsell-account',
                      'invoice-reduce-account', 'invoice-account-third']
    if 'accounting-sizecode' in params:
        for param_item in invoice_params:
            Parameter.change_value(
                param_item, correct_accounting_code(Params.getvalue(param_item)))
        Params.clear()
        for art in Article.objects.all():
            if art.sell_account != correct_accounting_code(art.sell_account):
                art.sell_account = correct_accounting_code(art.sell_account)
                art.save()
    for invoice_param in invoice_params:
        if invoice_param in params:
            Parameter.change_value(
                invoice_param, correct_accounting_code(Params.getvalue(invoice_param)))
