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
from lucterios.framework.xfercomponents import XferCompButton, XferCompLabelForm,\
    XferCompHeader
from lucterios.framework.tools import ActionsManage, FORMTYPE_MODAL, CLOSE_NO, \
    FORMTYPE_REFRESH
from lucterios.framework.models import get_value_if_choices
from lucterios.CORE.parameters import Params

from diacamma.accounting.tools import current_system_account


class ArticleEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components(
            'sell_account').mask = current_system_account().get_revenue_mask()


class BillEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.get_components('comment').with_hypertext = True
        xfer.get_components('comment').set_size(100, 375)

    def show(self, xfer):
        xfer.move(0, 0, 1)
        lbl = XferCompLabelForm('title')
        lbl.set_location(1, 0, 4)
        lbl.set_value_as_title(get_value_if_choices(
            self.item.bill_type, self.item.get_field_by_name('bill_type')))
        xfer.add_component(lbl)
        details = xfer.get_components('detail')
        if Params.getvalue("invoice-vat-mode") != 0:
            if Params.getvalue("invoice-vat-mode") == 1:
                details.headers[2] = XferCompHeader(details.headers[2].name, _(
                    'price excl. taxes'), details.headers[2].type, details.headers[2].orderable)
                details.headers[6] = XferCompHeader(details.headers[6].name, _(
                    'total excl. taxes'), details.headers[6].type, details.headers[6].orderable)
            elif Params.getvalue("invoice-vat-mode") == 2:
                details.headers[2] = XferCompHeader(details.headers[2].name, _(
                    'price incl. taxes'), details.headers[2].type, details.headers[2].orderable)
                details.headers[6] = XferCompHeader(details.headers[6].name, _(
                    'total incl. taxes'), details.headers[6].type, details.headers[6].orderable)
            xfer.get_components('lbl_total_excltax').set_value_as_name(
                _('total excl. taxes'))
            xfer.filltab_from_model(1, xfer.get_max_row() + 1, True,
                                    [((_('VTA sum'), 'vta_sum'), (_('total incl. taxes'), 'total_incltax'))])
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
            details.actions = []
        return


class DetailEditor(LucteriosEditor):

    def before_save(self, xfer):
        self.item.vta_rate = 0
        if (Params.getvalue("invoice-vat-mode") != 0) and (self.item.article is not None) and (self.item.article.vat is not None):
            self.item.vta_rate = float(self.item.article.vat.rate / 100)
        if Params.getvalue("invoice-vat-mode") == 2:
            self.item.vta_rate = -1 * self.item.vta_rate
        return

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components("article").set_action(xfer.request, xfer.get_action('', ''), {
            'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO, 'params': {'CHANGE_ART': 'YES'}})
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components('reduce').prec = currency_decimal
