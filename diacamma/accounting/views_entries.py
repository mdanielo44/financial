# -*- coding: utf-8 -*-
'''
Describe entries account viewer for Django

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

from lucterios.framework.xferadvance import XferShowEditor, XferDelete, XferSave
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    CLOSE_NO, FORMTYPE_REFRESH, CLOSE_YES, SELECT_SINGLE, \
    SELECT_MULTI, SELECT_NONE, WrapAction
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor
from lucterios.framework.xfergraphic import XferContainerAcknowledge, \
    XferContainerCustom
from lucterios.framework.xfercomponents import XferCompSelect, \
    XferCompLabelForm, XferCompImage
from lucterios.framework.error import LucteriosException, GRAVE

from diacamma.accounting.models import EntryLineAccount, EntryAccount, FiscalYear, \
    Journal, AccountLink, current_system_account, CostAccounting
from lucterios.CORE.xferprint import XferPrintListing
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor


@ActionsManage.affect('EntryLineAccount', 'list')
@MenuManage.describ('accounting.change_entryaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Edition of accounting entry for current fiscal year'),)
class EntryLineAccountList(XferListEditor):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("accounting entries")

    def __init__(self, **kwargs):
        XferListEditor.__init__(self, **kwargs)
        self.action_list = [('search', _("Search"),
                             "diacamma.accounting/images/entry.png"),
                            ('listing', _("Listing"), "images/print.png")]

    def _filter_by_year(self):
        select_year = self.getparam('year')
        self.item.year = FiscalYear.get_current(select_year)
        self.item.journal = Journal.objects.get(
            id=1)
        self.fill_from_model(0, 1, False, ['year', 'journal'])
        self.get_components('year').set_action(self.request, EntryLineAccountList.get_action(
        ), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        self.filter = Q(entry__year=self.item.year)

    def _filter_by_journal(self):
        select_journal = self.getparam('journal', 4)
        journal = self.get_components('journal')
        journal.select_list.append((-1, '---'))
        journal.set_value(select_journal)
        journal.set_action(self.request, EntryLineAccountList.get_action(), {
                           'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        if select_journal != -1:
            self.filter &= Q(entry__journal__id=select_journal)

    def _filter_by_nature(self):
        select_filter = self.getparam('filter', 1)
        if (self.item.year.status in [0, 1]) and (select_filter != 2):
            self.action_grid.append(
                ('remove', _("Delete"), "images/delete.png", SELECT_MULTI))
            self.action_grid.append(
                ('insertentry', _("Add"), "images/add.png", SELECT_NONE))
            self.action_grid.append(
                ('model', _("Model"), "images/add.png", SELECT_NONE))
            self.action_grid.append(
                ('closeentry', _("Closed"), "images/ok.png", SELECT_MULTI))
        self.action_grid.append(
            ('costaccounting', _("Cost"), "images/edit.png", SELECT_MULTI))
        lbl = XferCompLabelForm("filterLbl")
        lbl.set_location(0, 3)
        lbl.set_value_as_name(_("Filter"))
        self.add_component(lbl)
        sel = XferCompSelect("filter")
        sel.set_select({0: _('All'), 1: _('In progress'), 2: _(
            'Valid'), 3: _('Lettered'), 4: _('Not lettered')})
        sel.set_value(select_filter)
        sel.set_location(1, 3)
        sel.set_size(20, 200)
        sel.set_action(self.request, EntryLineAccountList.get_action(
            modal=FORMTYPE_REFRESH), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        self.add_component(sel)
        if select_filter == 1:
            self.filter &= Q(entry__close=False)
        elif select_filter == 2:
            self.filter &= Q(entry__close=True)
        elif select_filter == 3:
            self.filter &= Q(entry__link__id__gt=0)
        elif select_filter == 4:
            self.filter &= Q(entry__link=None)

    def fillresponse_header(self):
        self.action_grid = []
        self.action_grid.append(
            ('open', _("Edit"), "images/edit.png", SELECT_SINGLE))
        self.fieldnames = EntryLineAccount.get_other_fields()
        self.item = EntryAccount()
        self._filter_by_year()
        self._filter_by_journal()
        self._filter_by_nature()
        if self.item.year.status in [0, 1]:
            self.action_grid.append(
                ('link', _("Link/Unlink"), "images/left.png", SELECT_MULTI))

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        lbl = XferCompLabelForm("result")
        lbl.set_value_center(
            self.item.year.total_result_text)
        lbl.set_location(0, 10, 2)
        self.add_component(lbl)


@ActionsManage.affect('EntryLineAccount', 'search')
@MenuManage.describ('accounting.change_entryaccount')
class EntryLineAccountSearch(XferSavedCriteriaSearchEditor):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("Search accounting entry")

    def fillresponse(self):
        self.action_grid = []
        self.action_grid.append(
            ('open', _("Edit"), "images/edit.png", SELECT_SINGLE))
        self.fieldnames = EntryLineAccount.get_other_fields()
        XferSavedCriteriaSearchEditor.fillresponse(self)


@ActionsManage.affect('EntryLineAccount', 'listing')
@MenuManage.describ('accounting.change_entryaccount')
class EntryLineAccountListing(XferPrintListing):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("Listing accounting entry")

    def get_filter(self):
        if self.getparam('CRITERIA') is None:
            select_year = self.getparam('year')
            select_journal = self.getparam('journal', 4)
            select_filter = self.getparam('filter', 1)
            new_filter = Q(entry__year=FiscalYear.get_current(select_year))
            if select_filter == 1:
                new_filter &= Q(entry__close=False)
            elif select_filter == 2:
                new_filter &= Q(entry__close=True)
            elif select_filter == 3:
                new_filter &= Q(entry__link__id__gt=0)
            elif select_filter == 4:
                new_filter &= Q(entry__link=None)
            if select_journal != -1:
                new_filter &= Q(entry__journal__id=select_journal)
        else:
            new_filter = XferPrintListing.get_filter(self)
        return new_filter


@ActionsManage.affect('EntryLineAccount', 'remove')
@MenuManage.describ('accounting.delete_entryaccount')
class EntryAccountDel(XferDelete):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Delete accounting entry")

    def _search_model(self):
        entrylineaccount = self.getparam('entrylineaccount', [])
        if len(entrylineaccount) == 0:
            raise LucteriosException(GRAVE, _("No selection"))
        self.items = self.model.objects.filter(
            entrylineaccount__in=entrylineaccount)


@ActionsManage.affect('EntryLineAccount', 'closeentry')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountClose(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Close accounting entry")

    def fillresponse(self, entrylineaccount=[]):

        if self.item.id is None:
            if len(entrylineaccount) == 0:
                raise LucteriosException(GRAVE, _("No selection"))
            self.items = []
            for item in self.model.objects.filter(entrylineaccount__in=entrylineaccount):
                if not item.close:
                    self.items.append(item)
        else:
            self.items = [self.item]
        if (len(self.items) > 0) and self.confirme(_("Do you want to close this entry?")):
            for item in self.items:
                item.closed()


@ActionsManage.affect('EntryLineAccount', 'link')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountLink(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Delete accounting entry")

    def fillresponse(self, entrylineaccount=[]):

        if len(entrylineaccount) == 0:
            raise LucteriosException(GRAVE, _("No selection"))
        self.items = self.model.objects.filter(
            entrylineaccount__in=entrylineaccount)
        if len(self.items) == 1:
            if self.confirme(_('Do you want unlink this entry?')):
                self.items[0].unlink()
        else:
            AccountLink.create_link(self.items)


@ActionsManage.affect('EntryLineAccount', 'costaccounting')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountCostAccounting(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("cost accounting for entry")

    def fillresponse(self, entrylineaccount=[], costaccounting=0):

        if len(entrylineaccount) == 0:
            raise LucteriosException(GRAVE, _("No selection"))
        if self.getparam("SAVE") is None:
            dlg = self.create_custom()
            icon = XferCompImage('img')
            icon.set_location(0, 0, 1, 6)
            icon.set_value(self.icon_path())
            dlg.add_component(icon)
            lbl = XferCompLabelForm('lb_costaccounting')
            lbl.set_value_as_name(
                CostAccounting._meta.verbose_name)
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            sel = XferCompSelect('costaccounting')
            sel.set_select_query(
                CostAccounting.objects.filter(status=0))
            sel.set_location(1, 2)
            dlg.add_component(sel)
            dlg.add_action(
                self.get_action(_('Ok'), 'images/ok.png'), {'params': {"SAVE": "YES"}})
            dlg.add_action(WrapAction(_('Cancel'), 'images/cancel.png'), {})
        else:
            if costaccounting == 0:
                new_cost = None
            else:
                new_cost = CostAccounting.objects.get(
                    id=costaccounting)
            for item in self.model.objects.filter(entrylineaccount__in=entrylineaccount):
                if (item.costaccounting is None) or (item.costaccounting.status == 0):
                    item.costaccounting = new_cost
                    item.save()


@ActionsManage.affect('EntryLineAccount', 'open')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountOpenFromLine(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("accounting entries")

    def fillresponse(self, entrylineaccount_link=0):
        for old_key in ["SAVE", 'entrylineaccount', 'entrylineaccount_link', 'third', 'reference', 'serial_entry']:
            if old_key in self.params.keys():
                del self.params[old_key]
        if (self.item.id is None) and (entrylineaccount_link != 0):
            self.item = EntryLineAccount.objects.get(
                id=entrylineaccount_link)
        entry_account = self.item.entry
        option = {'params': {'entryaccount': entry_account.id}}
        if entry_account.close:
            self.redirect_action(EntryAccountShow.get_action(), option)
        else:
            self.redirect_action(EntryAccountEdit.get_action(), option)


@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountShow(XferShowEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Show accounting entry")

    def fillresponse(self):
        self.action_list = []
        if (self.item.link is None) and self.item.has_third and not self.item.has_cash and (self.item.year.status < 2):
            self.action_list = [('payement', _('Payment'), '', CLOSE_YES)]
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('EntryLineAccount', 'insertentry')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountEdit(XferAddEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption_add = _("Add entry of account")
    caption_modify = _("Modify accounting entry")

    def fillresponse(self):
        self.item.check_date()
        XferAddEditor.fillresponse(self)


@ActionsManage.affect('EntryAccount', 'unlock')
@MenuManage.describ('')
class EntryAccountUnlock(XferContainerAcknowledge):
    model = EntryAccount
    field_id = 'entryaccount'

    def fillresponse(self):
        self.item.delete_if_ghost_entry()


@ActionsManage.affect('EntryAccount', 'show')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountAfterSave(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Modify accounting entry")

    def fillresponse(self):
        for old_key in ['date_value', 'designation', 'SAVE']:
            if old_key in self.params.keys():
                del self.params[old_key]
        self.redirect_action(EntryAccountEdit.get_action(), {})


@ActionsManage.affect('EntryAccount', 'addentity')
@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountAddModify(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Save entry line of account")

    def fillresponse(self, entrylineaccount_serial=0, serial_entry='', num_cpt=0, credit_val=0.0, debit_val=0.0, third=0, reference='None'):
        if (credit_val > 0.0001) or (debit_val > 0.0001):
            for old_key in ['num_cpt_txt', 'num_cpt', 'credit_val', 'debit_val', 'third', 'reference', 'entrylineaccount_serial', 'serial_entry']:
                if old_key in self.params.keys():
                    del self.params[old_key]
            serial_entry = self.item.add_new_entryline(
                serial_entry, entrylineaccount_serial, num_cpt, credit_val, debit_val, third, reference)
        self.redirect_action(
            EntryAccountEdit.get_action(), {'params': {"serial_entry": serial_entry}})


@ActionsManage.affect('EntryAccount', 'change')
@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountEdit(XferContainerCustom):
    icon = "entry.png"
    model = EntryLineAccount
    caption = _("Modify entry line of account")

    def fillresponse(self, entryaccount, entrylineaccount_serial=0, serial_entry=''):
        entry = EntryAccount.objects.get(
            id=entryaccount)
        for line in entry.get_entrylineaccounts(serial_entry):
            if line.id == entrylineaccount_serial:
                self.item = line
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, 1, True, ['account'])
        cmp_account = self.get_components('account')
        cmp_account.colspan = 2
        self.item.editor.edit_creditdebit_for_line(self, 1, 2)
        self.item.editor.edit_extra_for_line(self, 1, 4, False)
        self.add_action(EntryLineAccountAddModify.get_action(
            _('Ok'), 'images/ok.png'), {'params': {"num_cpt": self.item.account.id}})
        self.add_action(
            EntryAccountEdit.get_action(_('Cancel'), 'images/cancel.png'), {})


@ActionsManage.affect('EntryAccount', 'remove')
@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountDel(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Delete entry line of account")

    def fillresponse(self, entrylineaccount_serial=0, serial_entry=''):
        for old_key in ['serial_entry', 'entrylineaccount_serial']:
            if old_key in self.params.keys():
                del self.params[old_key]
        serial_entry = self.item.remove_entrylineaccounts(
            serial_entry, entrylineaccount_serial)
        self.redirect_action(
            EntryAccountEdit.get_action(), {'params': {"serial_entry": serial_entry}})


@ActionsManage.affect('EntryAccount', 'validate')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountValidate(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Validate entry line of account")

    def fillresponse(self, serial_entry=''):
        save = XferSave()
        save.model = self.model
        save.field_id = self.field_id
        save.caption = self.caption
        save._initialize(self.request)
        save.params["SAVE"] = "YES"
        save.fillresponse()
        self.item.save_entrylineaccounts(serial_entry)


@ActionsManage.affect('EntryAccount', 'reverse')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountReverse(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Reverse entry lines of account")

    def fillresponse(self):
        for old_key in ['serial_entry']:
            if old_key in self.params.keys():
                del self.params[old_key]
        for line in self.item.entrylineaccount_set.all():
            line.amount = -1 * line.amount
            line.save()
        self.redirect_action(EntryAccountEdit.get_action(), {})


@ActionsManage.affect('EntryAccount', 'payement')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountCreateLinked(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Add payment entry of account")

    def fillresponse(self):
        new_entry, serial_entry = self.item.create_linked()
        self.redirect_action(EntryAccountEdit.get_action(), {'params': {"serial_entry": serial_entry,
                                                                        'journal': '4', 'entryaccount': new_entry.id,
                                                                        'num_cpt_txt': current_system_account().get_cash_begin()}})
