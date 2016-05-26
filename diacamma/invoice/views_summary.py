# -*- coding: utf-8 -*-
'''
lucterios.contacts package

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
from django.db.models import Q

from lucterios.framework.tools import MenuManage, FORMTYPE_MODAL, ActionsManage, SELECT_SINGLE
from lucterios.framework.xferadvance import XferListEditor

from lucterios.contacts.models import Individual, LegalEntity

from diacamma.invoice.models import Bill
from diacamma.invoice.views import BillPrint


def current_bill_right(request):
    right = False
    if not request.user.is_anonymous():
        contacts = Individual.objects.filter(user=request.user)
        right = len(contacts) > 0
    return right


@MenuManage.describ(current_bill_right, FORMTYPE_MODAL, 'core.general', _('View my invoices.'))
class CurrentBill(XferListEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("My invoices")

    def fillresponse_header(self):
        contacts = []
        for contact in Individual.objects.filter(user=self.request.user):
            contacts.append(contact.id)
        for contact in LegalEntity.objects.filter(responsability__individual__user=self.request.user):
            contacts.append(contact.id)
        self.filter = Q(third__contact_id__in=contacts)
        add_act = -1
        for idx in range(len(self.action_grid)):
            if self.action_grid[idx][0] == 'add':
                add_act = idx
        if add_act != -1:
            del self.action_grid[add_act]
        self.action_grid.append(
            ('currentprintbill', _("Print"), "images/print.png", SELECT_SINGLE))


@ActionsManage.affect('Bill', 'currentprintbill')
@MenuManage.describ(None)
class CurrentBillPrint(BillPrint):
    pass
