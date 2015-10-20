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

from diacamma.invoice.models import Vat

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage
from lucterios.CORE.parameters import Params
from lucterios.framework.xfercomponents import XferCompButton
from lucterios.CORE.views import ParamEdit


@ActionsManage.affect('Vat', 'list')
@MenuManage.describ('invoice.change_vat', FORMTYPE_NOMODAL, 'contact.conf', _('Management of parameters and configuration of invoice'))
class InvoiceConf(XferListEditor):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption = _("Invoice configuration")

    def fillresponse_header(self):
        self.new_tab(_('Parameters'))
        param_lists = ['invoice-vat-mode', 'invoice-default-sell-account', 'invoice-vatsell-account',
                       'invoice-reduce-account', 'invoice-bankcharges-account', 'invoice-cash-account']
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
