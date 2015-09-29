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

from django.utils.translation import ugettext_lazy as _

from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.xfercomponents import XferCompButton, XferCompLabelForm
from lucterios.framework.tools import ActionsManage, FORMTYPE_MODAL, CLOSE_NO, \
    FORMTYPE_REFRESH
from lucterios.framework.models import get_value_if_choices
from diacamma.accounting.tools import current_system_account
from lucterios.CORE.parameters import Params


class ArticleEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components(
            'sell_account').mask = current_system_account().get_revenue_mask()


class BillEditor(LucteriosEditor):

    def show(self, xfer):
        xfer.move(0, 0, 1)
        lbl = XferCompLabelForm('title')
        lbl.set_location(1, 0, 4)
        lbl.set_value_as_title(get_value_if_choices(
            self.item.bill_type, self.item.get_field_by_name('bill_type')))
        xfer.add_component(lbl)
        if self.item.status == 0:
            third = xfer.get_components('third')
            third.colspan -= 2
            btn = XferCompButton('change_third')
            btn.set_location(third.col + third.colspan, third.row)
            modal_name = xfer.item.__class__.__name__
            btn.set_action(xfer.request, ActionsManage.get_act_changed(modal_name, 'third', _('change'), ''),
                           {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO})
            xfer.add_component(btn)

            if self.item.third is not None:
                btn = XferCompButton('show_third')
                btn.set_location(third.col + third.colspan + 1, third.row)
                modal_name = xfer.item.__class__.__name__
                btn.set_action(xfer.request, ActionsManage.get_act_changed('Third', 'show', _('show'), ''),
                               {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO, 'params': {'third': self.item.third.id}})
                xfer.add_component(btn)
            lbl = XferCompLabelForm('info')
            lbl.set_color('red')
            lbl.set_location(1, xfer.get_max_row() + 1, 4)
            lbl.set_value(self.item.get_info_state())
            xfer.add_component(lbl)
        else:
            xfer.get_components('detail').actions = []
        return


class DetailEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components("article").set_action(xfer.request, xfer.get_action('', ''), {
            'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO, 'params': {'CHANGE_ART': 'YES'}})
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components('reduce').prec = currency_decimal
