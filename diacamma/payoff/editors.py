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
from diacamma.payoff.models import Supporting
from lucterios.framework.error import LucteriosException, IMPORTANT
from django.utils import six
from build.lib.lucterios.framework.xfercomponents import XferCompLabelForm
from lucterios.contacts.models import LegalEntity


class SupportingEditor(LucteriosEditor):

    def before_save(self, xfer):
        self.item.is_revenu = self.item.payoff_is_revenu()
        return LucteriosEditor.before_save(self, xfer)

    def show(self, xfer):
        xfer.params['supporting'] = self.item.id
        xfer.filltab_from_model(
            1, xfer.get_max_row() + 1, True, self.item.get_payoff_fields())
        payoff = xfer.get_components("payoff")
        if not self.item.is_revenu:
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
        supportings = xfer.getparam('supportings', ())
        if len(supportings) > 0:
            supporting_list = Supporting.objects.filter(
                id__in=supportings, is_revenu=True)
            if len(supporting_list) == 0:
                raise LucteriosException(IMPORTANT, _('No-valid selection!'))
        else:
            supporting_list = [self.item.supporting]
        amount_max = 0
        title = []
        for supporting in supporting_list:
            up_supporting = supporting.get_final_child()
            title.append(six.text_type(up_supporting))
            amount_max += up_supporting.get_total_rest_topay()
        xfer.move(0, 0, 1)
        lbl = XferCompLabelForm('supportings')
        lbl.set_value_center("{[br/]}".join(title))
        lbl.set_location(1, 0, 2)
        xfer.add_component(lbl)
        amount = xfer.get_components("amount")
        if self.item.id is None:
            amount.value = amount_max
            xfer.get_components("payer").value = six.text_type(
                supporting_list[0].third)
        amount.prec = currency_decimal
        amount.min = 0
        amount.max = amount_max
        xfer.get_components("mode").set_action(
            xfer.request, xfer.get_action(), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        if self.item.mode == 0:
            xfer.remove_component("bank_account")
            xfer.remove_component("lbl_bank_account")
        else:
            banks = xfer.get_components("bank_account")
            if banks.select_list[0][0] == 0:
                del banks.select_list[0]
        if not supporting_list[0].is_revenu:
            xfer.remove_component("payer")
            xfer.remove_component("lbl_payer")


class DepositSlipEditor(LucteriosEditor):

    def show(self, xfer):
        xfer.move(0, 0, 5)
        xfer.item = LegalEntity.objects.get(id=1)
        xfer.fill_from_model(
            1, 0, True, ["name", 'address', ('postal_code', 'city'), ('tel1', 'email')])
        xfer.item = self.item
        lbl = XferCompLabelForm('sep')
        lbl.set_value_center("{[hr/]}")
        lbl.set_location(1, 4, 4)
        xfer.add_component(lbl)
        xfer.remove_component("lbl_depositdetail_set")
        depositdetail = xfer.get_components("depositdetail")
        depositdetail.col = 1
        depositdetail.colspan = 4
        if self.item.status != 0:
            depositdetail.actions = []
