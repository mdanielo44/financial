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
from datetime import timedelta, date

from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet
from django.db.models import Q
from django.utils import six

from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferShowEditor, XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    FORMTYPE_REFRESH, CLOSE_NO, WrapAction
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.xferprint import XferPrintListing
from lucterios.contacts.tools import ContactSelection
from lucterios.contacts.models import AbstractContact
from lucterios.framework import signal_and_lock
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompEdit, XferCompButton, \
    XferCompSelect, XferCompImage, XferCompDate
from lucterios.framework.error import LucteriosException

from diacamma.accounting.models import Third, AccountThird, FiscalYear, \
    EntryLineAccount
from diacamma.accounting.views_admin import Configuration
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor

MenuManage.add_sub("financial", None, "diacamma.accounting/images/financial.png",
                   _("Financial"), _("Financial tools"), 50)


@ActionsManage.affect('Third', 'list')
@MenuManage.describ('accounting.change_third', FORMTYPE_NOMODAL, 'financial', _('Management of third account'))
class ThirdList(XferListEditor):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Thirds")
    action_list = [('disable', _('Disabled'), ''),
                   ('search', _("Search"),
                    "diacamma.accounting/images/thirds.png"),
                   ('listing', _("Listing"), "images/print.png")]

    def get_items_from_filter(self):
        items = XferListEditor.get_items_from_filter(self)
        items = sorted(items, key=lambda t: six.text_type(
            t))
        if self.getparam('show_filter', 0) == 2:
            items = [item for item in items if abs(item.get_total()) > 0.0001]
        res = QuerySet(model=Third)
        res._result_cache = items
        return res

    def fillresponse_header(self):
        contact_filter = self.getparam('filter', '')
        show_filter = self.getparam('show_filter', 0)
        lbl = XferCompLabelForm('lbl_filtre')
        lbl.set_value_as_name(_('Filtrer by contact'))
        lbl.set_location(0, 2)
        self.add_component(lbl)
        comp = XferCompEdit('filter')
        comp.set_value(contact_filter)
        comp.set_action(self.request, self.get_action(),
                        {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        comp.set_location(1, 2)
        self.add_component(comp)

        lbl = XferCompLabelForm('lbl_showing')
        lbl.set_value_as_name(_('Accounts displayed'))
        lbl.set_location(0, 3)
        self.add_component(lbl)
        edt = XferCompSelect("show_filter")
        edt.set_select([(0, _('Hide the account total of thirds')), (1, _('Show the account total of thirds')),
                        (2, _('Filter any thirds unbalanced'))])
        edt.set_value(show_filter)
        edt.set_location(1, 3)
        edt.set_action(self.request, self.get_action(),
                       {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        self.add_component(edt)
        if show_filter != 0:
            self.fieldnames = Third.get_other_fields()

        self.filter = Q(status=0)
        if contact_filter != "":
            q_legalentity = Q(
                contact__legalentity__name__contains=contact_filter)
            q_individual = (Q(contact__individual__firstname__contains=contact_filter) | Q(
                contact__individual__lastname__contains=contact_filter))
            self.filter &= (q_legalentity | q_individual)


@ActionsManage.affect('Third', 'search')
@MenuManage.describ('accounting.change_third')
class ThirdSearch(XferSavedCriteriaSearchEditor):
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
        last_thirds = Third.objects.filter(
            contact__pk=contact_id)
        if len(last_thirds) > 0:
            self.item = last_thirds[0]
        else:
            self.item.contact = AbstractContact.objects.get(
                id=contact_id)
            self.item.status = 0
            self.item.save()
        self.redirect_action(
            ThirdShow.get_action(), {'params': {self.field_id: self.item.id}})


@ActionsManage.affect('Third', 'disable')
@MenuManage.describ('accounting.add_third')
class ThirdDisable(XferContainerAcknowledge):
    model = Third
    icon = "thirds.png"
    caption = _("Disable third")

    def fillresponse(self, limit_date=''):
        if limit_date == '':
            dlg = self.create_custom()
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0, 1, 6)
            dlg.add_component(img)
            lbl = XferCompLabelForm('lb_limit_date')
            lbl.set_value_as_name(_('limit date'))
            lbl.set_location(1, 1, 1)
            dlg.add_component(lbl)
            limite_date = XferCompDate('limit_date')
            limite_date.set_value((date.today() - timedelta(weeks=25)))
            limite_date.set_location(1, 2, 1)
            dlg.add_component(limite_date)
            dlg.add_action(
                self.get_action(_('Ok'), 'images/ok.png'), {'params': {"SAVE": "YES"}})
            dlg.add_action(WrapAction(_('Cancel'), 'images/cancel.png'), {})
        else:
            third_ids = [val_third['third'] for val_third in EntryLineAccount.objects.filter(
                entry__date_value__gt=limit_date, third__gt=0).values('third')]
            for third in Third.objects.filter(status=0):
                if third.id not in third_ids:
                    third.status = 1
                    third.save()


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

    def filter_callback(self, items):
        items = sorted(items, key=lambda t: six.text_type(
            t))
        if (self.getparam('CRITERIA') is None) and (self.getparam('show_filter', 0) == 2):
            items = [item for item in items if abs(item.get_total()) > 0.0001]
        res = QuerySet(model=Third)
        res._result_cache = items
        return res

    def get_filter(self):
        if self.getparam('CRITERIA') is None:
            contact_filter = self.getparam('filter', '')
            new_filter = Q(status=0)
            if contact_filter != "":
                q_legalentity = Q(
                    contact__legalentity__name__contains=contact_filter)
                q_individual = (Q(contact__individual__firstname__contains=contact_filter) | Q(
                    contact__individual__lastname__contains=contact_filter))
                new_filter &= (q_legalentity | q_individual)
        else:
            new_filter = XferPrintListing.get_filter(self)
        return new_filter


@ActionsManage.affect('AccountThird', 'add')
@MenuManage.describ('accounting.add_third')
class AccountThirdAddModify(XferAddEditor):
    icon = "account.png"
    model = AccountThird
    field_id = 'accountthird'
    caption_add = _("Add account")
    caption_modify = _("Modify account")


@ActionsManage.affect('AccountThird', 'delete')
@MenuManage.describ('accounting.add_third')
class AccountThirdDel(XferDelete):
    icon = "account.png"
    model = AccountThird
    field_id = 'accountthird'
    caption = _("Delete account")


@signal_and_lock.Signal.decorate('summary')
def summary_accounting(xfer):
    row = xfer.get_max_row() + 1
    lab = XferCompLabelForm('accountingtitle')
    lab.set_value_as_infocenter(_("Financial"))
    lab.set_location(0, row, 4)
    xfer.add_component(lab)

    try:
        year = FiscalYear.get_current()
        lbl = XferCompLabelForm("accounting_year")
        lbl.set_value_center(six.text_type(year))
        lbl.set_location(0, row + 1, 4)
        xfer.add_component(lbl)
        lbl = XferCompLabelForm("accounting_result")
        lbl.set_value_center(year.total_result_text)
        lbl.set_location(0, row + 2, 4)
        xfer.add_component(lbl)
    except LucteriosException as lerr:
        lbl = XferCompLabelForm("accounting_error")
        lbl.set_value_center(six.text_type(lerr))
        lbl.set_location(0, row + 1, 4)
        xfer.add_component(lbl)
        btn = XferCompButton("accounting_conf")
        btn.set_action(xfer.request, Configuration.get_action(
            _("conf."), ""), {'close': CLOSE_NO})
        btn.set_location(0, row + 2, 4)
        xfer.add_component(btn)

    lab = XferCompLabelForm('accountingend')
    lab.set_value_center('{[hr/]}')
    lab.set_location(0, row + 3, 4)
    xfer.add_component(lab)
