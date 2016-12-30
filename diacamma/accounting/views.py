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

from lucterios.framework import signal_and_lock
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferShowEditor, XferDelete,\
    TITLE_ADD, TITLE_EDIT, TITLE_DELETE, TITLE_OK, TITLE_CANCEL, XferTransition
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompEdit, XferCompButton, XferCompSelect, XferCompImage, XferCompDate, XferCompGrid
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, FORMTYPE_REFRESH, CLOSE_NO, WrapAction, FORMTYPE_MODAL, SELECT_SINGLE,\
    SELECT_MULTI, SELECT_NONE
from lucterios.framework.error import LucteriosException
from lucterios.CORE.xferprint import XferPrintListing
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor
from lucterios.contacts.tools import ContactSelection
from lucterios.contacts.models import AbstractContact

from diacamma.accounting.models import Third, AccountThird, FiscalYear, \
    EntryLineAccount, ModelLineEntry, EntryAccount, ChartsAccount
from diacamma.accounting.views_admin import Configuration, add_year_info
from diacamma.accounting.tools import correct_accounting_code

MenuManage.add_sub("financial", None, "diacamma.accounting/images/financial.png", _("Financial"), _("Financial tools"), 50)


@MenuManage.describ('accounting.change_third', FORMTYPE_NOMODAL, 'financial', _('Management of third account'))
class ThirdList(XferListEditor):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Thirds")

    def get_items_from_filter(self):
        items = XferListEditor.get_items_from_filter(self)
        items = sorted(items, key=lambda t: six.text_type(t).lower())
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
        comp.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
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
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)
        if show_filter != 0:
            self.fieldnames = Third.get_other_fields()

        self.filter = Q(status=0)
        if contact_filter != "":
            q_legalentity = Q(contact__legalentity__name__icontains=contact_filter)
            q_individual = (Q(contact__individual__firstname__icontains=contact_filter) | Q(contact__individual__lastname__icontains=contact_filter))
            self.filter &= (q_legalentity | q_individual)


@ActionsManage.affect_list(_("Search"), "diacamma.accounting/images/thirds.png")
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
    field_id = ''

    def fillresponse(self, pkname='', new_account=''):
        contact_id = self.getparam(pkname)
        last_thirds = Third.objects.filter(
            contact__pk=contact_id)
        if len(last_thirds) > 0:
            self.item = last_thirds[0]
        else:
            self.item.contact = AbstractContact.objects.get(id=contact_id)
            self.item.status = 0
            self.item.save()
        if new_account != '':
            old_account = self.item.accountthird_set.filter(code=correct_accounting_code(new_account))
            if len(old_account) == 0:
                AccountThird.objects.create(third=self.item, code=correct_accounting_code(new_account))
        self.redirect_action(ThirdShow.get_action(), params={'third': self.item.id})


@ActionsManage.affect_list(_('Disabled'), '')
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
            limite_date.set_needed(True)
            limite_date.set_value((date.today() - timedelta(weeks=25)))
            limite_date.set_location(1, 2, 1)
            dlg.add_component(limite_date)
            dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), params={"SAVE": "YES"})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            third_ids = [val_third['third'] for val_third in EntryLineAccount.objects.filter(
                entry__date_value__gt=limit_date, third__gt=0).values('third')]
            for third in Third.objects.filter(status=0):
                if third.id not in third_ids:
                    third.status = 1
                    third.save()


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", unique=SELECT_NONE)
@MenuManage.describ('accounting.add_third')
class ThirdAdd(ContactSelection):
    icon = "thirds.png"
    caption = _("Add third")
    select_class = ThirdSave
    model = Third


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.change_third')
class ThirdShow(XferShowEditor):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Show third")


@ActionsManage.affect_transition("status")
@MenuManage.describ('accounting.add_third')
class ThirdTransition(XferTransition):
    icon = "thirds.png"
    model = Third
    field_id = 'third'


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('accounting.delete_third')
class ThirdDel(XferDelete):
    icon = "thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Delete third")


@ActionsManage.affect_list(_("Listing"), "images/print.png")
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
                q_legalentity = Q(contact__legalentity__name__icontains=contact_filter)
                q_individual = (Q(contact__individual__firstname__icontains=contact_filter) | Q(
                    contact__individual__lastname__icontains=contact_filter))
                new_filter &= (q_legalentity | q_individual)
        else:
            new_filter = XferPrintListing.get_filter(self)
        return new_filter


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", unique=SELECT_NONE)
@MenuManage.describ('accounting.add_third')
class AccountThirdAddModify(XferAddEditor):
    icon = "account.png"
    model = AccountThird
    field_id = 'accountthird'
    caption_add = _("Add account")
    caption_modify = _("Modify account")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('accounting.add_third')
class AccountThirdDel(XferDelete):
    icon = "account.png"
    model = AccountThird
    field_id = 'accountthird'
    caption = _("Delete account")


@signal_and_lock.Signal.decorate('summary')
def summary_accounting(xfer):
    if WrapAction.is_permission(xfer.request, 'accounting.change_chartsaccount'):
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('accountingtitle')
        lab.set_value_as_infocenter(_("Bookkeeping"))
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
            if len(ChartsAccount.objects.filter(year=year)) == 0:
                add_year_info(xfer, True)
        except LucteriosException as lerr:
            lbl = XferCompLabelForm("accounting_error")
            lbl.set_value_center(six.text_type(lerr))
            lbl.set_location(0, row + 1, 4)
            xfer.add_component(lbl)
            btn = XferCompButton("accounting_conf")
            btn.set_action(xfer.request, Configuration.get_action(_("conf."), ""), close=CLOSE_NO)
            btn.set_location(0, row + 2, 4)
            xfer.add_component(btn)
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('accountingend')
        lab.set_value_center('{[hr/]}')
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
        return True
    else:
        return False


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_accounting(known_codes, accompt_returned):
    third_unknown = AccountThird.objects.filter(
        third__status=0).exclude(code__in=known_codes).values_list('code', flat=True).distinct()
    model_unknown = ModelLineEntry.objects.exclude(
        code__in=known_codes).values_list('code', flat=True).distinct()
    comptenofound = ""
    if (len(third_unknown) > 0):
        comptenofound = _("thirds") + ":" + ",".join(third_unknown) + " "
    if (len(model_unknown) > 0):
        comptenofound += _("models") + ":" + ",".join(model_unknown)
    if comptenofound != "":
        accompt_returned.append(
            "- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Accounting'), comptenofound))
    return True


@signal_and_lock.Signal.decorate('show_contact')
def show_contact_accounting(contact, xfer):
    if WrapAction.is_permission(xfer.request, 'accounting.change_entryaccount'):
        main_third = None
        thirds = Third.objects.filter(contact_id=contact.id)
        if len(thirds) > 1:
            main_third = thirds[0]
            alias_third = []
            for third in thirds:
                if third.id != main_third.id:
                    alias_third.append(third)
            main_third.merge_objects(alias_third)
        elif len(thirds) == 1:
            main_third = thirds[0]
        if main_third is not None:
            xfer.new_tab(_("Financial"))
            xfer.item = main_third
            xfer.filltab_from_model(0, 0, True, ["status", ((_('total'), 'total'),)])
            btn = XferCompButton('show_third')
            btn.set_location(0, 50, 2)
            btn.set_action(xfer.request, ActionsManage.get_action_url('accounting.Third', 'Show', xfer),
                           modal=FORMTYPE_MODAL, close=CLOSE_NO, params={"third": six.text_type(main_third.id)})
            xfer.add_component(btn)
            xfer.item = contact


@signal_and_lock.Signal.decorate('third_addon')
def thirdaddon_accounting(item, xfer):
    if WrapAction.is_permission(xfer.request, 'accounting.change_entryaccount'):
        try:
            entry_lines_filter = Q(entrylineaccount__third=item)
            lines_filter = xfer.getparam('lines_filter', 0)
            if lines_filter == 0:
                entry_lines_filter &= Q(year=FiscalYear.get_current())
            elif lines_filter == 1:
                entry_lines_filter &= Q(year=FiscalYear.get_current()) & Q(close=False)
            xfer.new_tab(_('entry of account'))
            lbl = XferCompLabelForm('lbl_lines_filter')
            lbl.set_value_as_name(_('Accounts filter'))
            lbl.set_location(0, 1)
            xfer.add_component(lbl)
            edt = XferCompSelect("lines_filter")
            edt.set_select([(0, _('All entries of current fiscal year')), (1, _(
                'Only no-closed entries of current fiscal year')), (2, _('All entries for all fiscal year'))])
            edt.set_value(lines_filter)
            edt.set_location(1, 1)
            edt.set_action(xfer.request, xfer.get_action(),
                           modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            xfer.add_component(edt)
            entries = EntryAccount.objects.filter(entry_lines_filter)
            link_grid_lines = XferCompGrid('entryaccount')
            link_grid_lines.set_model(entries, EntryAccount.get_default_fields(), xfer)
            link_grid_lines.set_location(0, 2, 2)
            link_grid_lines.add_action(xfer.request, ActionsManage.get_action_url('accounting.EntryAccount', 'OpenFromLine', xfer),
                                       modal=FORMTYPE_MODAL, unique=SELECT_SINGLE, close=CLOSE_NO)
            link_grid_lines.add_action(xfer.request, ActionsManage.get_action_url('accounting.EntryAccount', 'Close', xfer),
                                       modal=FORMTYPE_MODAL, unique=SELECT_MULTI, close=CLOSE_NO)
            link_grid_lines.add_action(xfer.request, ActionsManage.get_action_url('accounting.EntryAccount', 'Link', xfer),
                                       modal=FORMTYPE_MODAL, unique=SELECT_MULTI, close=CLOSE_NO)
            xfer.add_component(link_grid_lines)
        except LucteriosException:
            pass
