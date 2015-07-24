# -*- coding: utf-8 -*-
'''
Describe view for Django

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

from diacamma.accounting.models import Third, AccountThird, FiscalYear

from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferShowEditor, XferDelete
from lucterios.framework.xfersearch import XferSearchEditor
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    FORMTYPE_REFRESH, CLOSE_NO
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.xferprint import XferPrintListing
from lucterios.contacts.tools import ContactSelection  # pylint: disable=no-name-in-module,import-error
from lucterios.contacts.models import AbstractContact  # pylint: disable=no-name-in-module,import-error
from lucterios.framework import signal_and_lock
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompEdit
from django.utils import six

MenuManage.add_sub("financial", None, "diacamma.accounting/images/financial.png", _("Financial"), _("Financial tools"), 50)

@ActionsManage.affect('Third', 'list')
@MenuManage.describ('accounting.change_third', FORMTYPE_NOMODAL, 'financial', _('Management of third account'))
class ThirdList(XferListEditor):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Thirds")
    action_list = [('search', _("Search"), "diacamma.accounting/images/thirds.png"), ('listing', _("Listing"), "images/print.png")]

    def fillresponse_header(self):
        contact_filter = self.getparam('filter')
        if contact_filter is None:
            contact_filter = ""
        lbl = XferCompLabelForm('lbl_filtre')
        lbl.set_value_as_name(_('Filtrer by contact'))
        lbl.set_location(0, 2)
        self.add_component(lbl)
        comp = XferCompEdit('filter')
        comp.set_value(contact_filter)
        comp.set_action(self.request, self.get_action(), {'modal':FORMTYPE_REFRESH, 'close':CLOSE_NO})
        comp.set_location(1, 2)
        self.add_component(comp)
        q_filter = Q(status=0)
        if contact_filter != "":
            q_legalentity = Q(contact__legalentity__name__contains=contact_filter)
            q_individual = (Q(contact__individual__firstname__contains=contact_filter) | Q(contact__individual__lastname__contains=contact_filter))
            q_filter = q_filter & (q_legalentity | q_individual)
        self.filter = [q_filter]

@ActionsManage.affect('Third', 'search')
@MenuManage.describ('accounting.change_third')
class ThirdSearch(XferSearchEditor):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Search third")

@MenuManage.describ('accounting.add_third')
class ThirdSave(XferContainerAcknowledge):
    icon = "thirds.png"
    model = Third
    field_id = 'third'

    def fillresponse(self, pkname=''):
        contact_id = self.getparam(pkname)
        last_thirds = Third.objects.filter(contact__pk=contact_id)  # pylint: disable=no-member
        if len(last_thirds) > 0:
            self.item = last_thirds[0]
        else:
            self.item.contact = AbstractContact.objects.get(id=contact_id)  # pylint: disable=no-member
            self.item.status = 0
            self.item.save()
        self.redirect_action(ThirdShow.get_action(), {'params':{self.field_id:self.item.id}})

@ActionsManage.affect('Third', 'add')
@MenuManage.describ('accounting.add_third')
class ThirdAdd(ContactSelection):
    icon = "thirds.png"
    caption = _("Add third")
    select_class = ThirdSave

    def __init__(self):
        ContactSelection.__init__(self)

@ActionsManage.affect('Third', 'modify')
@MenuManage.describ('accounting.add_third')
class ThirdModify(XferAddEditor):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption_modify = _("Modify third")

@ActionsManage.affect('Third', 'show')
@MenuManage.describ('accounting.change_third')
class ThirdShow(XferShowEditor):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Show third")

@ActionsManage.affect('Third', 'delete')
@MenuManage.describ('accounting.delete_third')
class ThirdDel(XferDelete):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Delete third")

@ActionsManage.affect('Third', 'listing')
@MenuManage.describ('accounting.change_third')
class ThirdListing(XferPrintListing):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Listing third")

@ActionsManage.affect('AccountThird', 'modify', 'add')
@MenuManage.describ('accounting.add_third')
class AccountAddModify(XferAddEditor):
    icon = "account.png"
    model = AccountThird
    field_id = 'account'
    caption_add = _("Add account")
    caption_modify = _("Modify account")

@ActionsManage.affect('AccountThird', 'delete')
@MenuManage.describ('accounting.delete_third')
class AccountDel(XferDelete):
    icon = "account.png"
    model = AccountThird
    field_id = 'account'
    caption = _("Delete account")

@signal_and_lock.Signal.decorate('summary')
def summary_accounting(xfer):
    row = xfer.get_max_row() + 1
    lab = XferCompLabelForm('accountingtitle')
    lab.set_value_as_infocenter(_("Financial"))
    lab.set_location(0, row, 4)
    xfer.add_component(lab)

    year = FiscalYear.get_current()
    lbl = XferCompLabelForm("accounting_year")
    lbl.set_value_center(six.text_type(year))
    lbl.set_location(0, row + 1, 4)
    xfer.add_component(lbl)
    lbl = XferCompLabelForm("accounting_result")
    lbl.set_value_center(year.total_result_text)
    lbl.set_location(0, row + 2, 4)
    xfer.add_component(lbl)

    lab = XferCompLabelForm('accountingend')
    lab.set_value_center('{[hr/]}')
    lab.set_location(0, row + 3, 4)
    xfer.add_component(lab)
