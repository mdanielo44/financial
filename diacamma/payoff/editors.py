# -*- coding: utf-8 -*-
'''
diacamma.payoff editors package

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

from lucterios.framework.editors import LucteriosEditor
from lucterios.CORE.parameters import Params
from lucterios.framework.tools import ActionsManage, CLOSE_NO, SELECT_NONE,\
    FORMTYPE_REFRESH


class SupportingEditor(LucteriosEditor):

    def show(self, xfer):
        xfer.params['supporting'] = self.item.id
        xfer.filltab_from_model(
            1, xfer.get_max_row() + 1, True, self.item.get_payoff_fields())
        payoff = xfer.get_components("payoff")
        if not self.item.is_revenu():
            head_idx = 0
            for header in payoff.headers:
                if header.name == 'payer':
                    break
                head_idx += 1
            del payoff.headers[head_idx]
        if self.item.get_total_rest_topay() > 0.001:
            payoff.add_action(xfer.request, ActionsManage.get_act_changed(
                'Payoff', 'append', _("Add"), "images/add.png", ), {'close': CLOSE_NO, 'unique': SELECT_NONE})


class PayoffEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        supporting = self.item.supporting.get_final_child()
        xfer.get_components("mode").set_action(
            xfer.request, xfer.get_action(), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        amount = xfer.get_components("amount")
        amount.prec = currency_decimal
        amount.min = 0
        amount.max = supporting.get_total_rest_topay()
        if self.item.mode == 0:
            xfer.remove_component("bank_account")
            xfer.remove_component("lbl_bank_account")
        else:
            banks = xfer.get_components("bank_account")
            if banks.select_list[0][0] == 0:
                del banks.select_list[0]
        if not supporting.is_revenu():
            xfer.remove_component("payer")
            xfer.remove_component("lbl_payer")
