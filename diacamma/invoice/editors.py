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
from django.db.models import Q
from django.utils import six

from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompHeader
from lucterios.framework.tools import CLOSE_NO, FORMTYPE_REFRESH
from lucterios.framework.models import get_value_if_choices
from lucterios.CORE.parameters import Params

from diacamma.accounting.tools import current_system_account
from diacamma.accounting.models import CostAccounting
from diacamma.payoff.editors import SupportingEditor


class ArticleEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components(
            'sell_account').mask = current_system_account().get_revenue_mask()


class BillEditor(SupportingEditor):

    def edit(self, xfer):
        xfer.get_components('comment').with_hypertext = True
        xfer.get_components('comment').set_size(100, 375)
        com_type = xfer.get_components('bill_type')
        com_type.set_action(xfer.request, xfer.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        if xfer.item.bill_type == 0:
            xfer.remove_component("cost_accounting")
            xfer.remove_component("lbl_cost_accounting")
        else:
            comp = xfer.get_components("cost_accounting")
            sel_list = []
            sel_list.append((0, "---"))
            comp.set_value(0)
            for select_obj in CostAccounting.objects.filter(Q(status=0)):
                sel_list.append((select_obj.id, six.text_type(select_obj)))
                if select_obj.is_default:
                    comp.set_value(select_obj.id)
            if xfer.item.id is not None:
                comp.set_value(xfer.item.cost_accounting_id)
            comp.set_select(sel_list)

    def show(self, xfer):
        if xfer.item.cost_accounting is None:
            xfer.remove_component("cost_accounting")
            xfer.remove_component("lbl_cost_accounting")
        xfer.params['new_account'] = Params.getvalue('invoice-account-third')
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
            SupportingEditor.show_third(self, xfer, 'invoice.add_bill')
        else:
            SupportingEditor.show_third_ex(self, xfer)
            details.actions = []
            if self.item.bill_type != 0:
                SupportingEditor.show(self, xfer)
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
        xfer.get_components("article").set_action(
            xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components('reduce').prec = currency_decimal
