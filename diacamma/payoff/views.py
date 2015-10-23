# -*- coding: utf-8 -*-
'''
diacamma.invoice views package

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

from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import ActionsManage, MenuManage

from diacamma.payoff.models import Payoff
from lucterios.framework.xfergraphic import XferContainerAcknowledge


@ActionsManage.affect('Payoff', 'edit', 'append')
@MenuManage.describ('payoff.add_payoff')
class PayoffAddModify(XferAddEditor):
    icon = "payoff.png"
    model = Payoff
    field_id = 'payoff'
    caption_add = _("Add payoff")
    caption_modify = _("Modify payoff")

    def fillresponse_multisave(self, supportings=(), amount=0.0, mode=0, payer='', reference='', bank_account=0, date=None):
        Payoff.multi_save(
            supportings, amount, mode, payer, reference, bank_account, date)

    def run_save(self, request, *args, **kwargs):
        supportings = self.getparam('supportings', ())
        if len(supportings) > 0:
            multisave = XferContainerAcknowledge()
            multisave.is_view_right = self.is_view_right
            multisave.locked = self.locked
            multisave.model = self.model
            multisave.field_id = self.field_id
            multisave.caption = self.caption
            multisave.closeaction = self.closeaction
            multisave.fillresponse = self.fillresponse_multisave
            return multisave.get(request, *args, **kwargs)
        else:
            return XferAddEditor.run_save(self, request, *args, **kwargs)


@ActionsManage.affect('Payoff', 'delete')
@MenuManage.describ('payoff.delete_payoff')
class PayoffDel(XferDelete):
    icon = "payoff.png"
    model = Payoff
    field_id = 'payoff'
    caption = _("Delete payoff")
