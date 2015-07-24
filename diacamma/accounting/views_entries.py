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

from diacamma.accounting.models import EntryLineAccount, EntryAccount, FiscalYear

from lucterios.framework.xferadvance import XferShowEditor, XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    WrapAction, CLOSE_NO, FORMTYPE_REFRESH, CLOSE_YES, SELECT_SINGLE,\
    FORMTYPE_MODAL, SELECT_MULTI, SELECT_NONE
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompButton, XferCompSelect, \
    XferCompLabelForm, XferCompGrid
from django.utils import six
from lucterios.framework.error import LucteriosException, GRAVE

@ActionsManage.affect('EntryLineAccount', 'list')
@MenuManage.describ('accounting.change_entryaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Edition of accounting entry for current fiscal year'),)
class EntryLineAccountList(XferListEditor):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("accounting entries")
    fieldnames = ['entry.num', 'entry.date_entry', 'entry.date_value', (_('account'), 'entry_account'), \
                    'entry.designation', (_('debit'), 'debit'), (_('credit'), 'credit')]

    def fillresponse_header(self):
        self.item = EntryAccount()

        select_year = self.getparam('year')
        select_filter = self.getparam('filter')

        self.item.year = FiscalYear.get_current(select_year)
        self.fill_from_model(0, 1, False, ['year'])
        self.get_components('year').set_action(self.request, EntryLineAccountList.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})

        if select_filter is None:
            select_filter = 1
        else:
            select_filter = int(select_filter)
        lbl = XferCompLabelForm("filterLbl")
        lbl.set_location(0, 2)
        lbl.set_value_as_name(_("Filter"))
        self.add_component(lbl)
        sel = XferCompSelect("filter")
        sel.set_select({0:_('All'), 1:_('In progress'), 2:_('Valid'), 3:_('Lettered'), 4:_('Not lettered')})
        sel.set_value(select_filter)
        sel.set_location(1, 2)
        sel.set_size(20, 200)
        sel.set_action(self.request, EntryLineAccountList.get_action(modal=FORMTYPE_REFRESH), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
        self.add_component(sel)

        current_filter = Q(entry__year=self.item.year)
        if select_filter == 1:
            current_filter = current_filter & Q(entry__close=False)
        elif select_filter == 2:
            current_filter = current_filter & Q(entry__close=True)
        self.filter = [current_filter]

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid_entries = self.get_components('entrylineaccount')
        grid_entries.actions = []
        grid_entries.add_action(self.request, EntryAccountOpenFromLine.get_action(_("Edit"), "images/edit.png"), {'modal':FORMTYPE_NOMODAL, 'unique':SELECT_SINGLE})
        grid_entries.add_action(self.request, EntryAccountDel.get_action(_("Delete"), "images/delete.png"), {'modal':FORMTYPE_NOMODAL, 'unique':SELECT_MULTI})
        grid_entries.add_action(self.request, EntryAccountAddModify.get_action(_("Add"), "images/add.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_NONE})

        lbl = XferCompLabelForm("result")
        lbl.set_value_center(self.item.year.total_result_text)
        lbl.set_location(0, 10, 2)
        self.add_component(lbl)

@MenuManage.describ('accounting.delete_entryaccount')
class EntryAccountDel(XferDelete):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Delete accounting entry")

    def _search_model(self):
        ids = self.getparam('entrylineaccount')
        if ids is None:
            raise LucteriosException(GRAVE, _("No selection"))
        ids = ids.split(';') # pylint: disable=no-member
        self.items = self.model.objects.filter(entrylineaccount__in=ids) # pylint: disable=no-member

@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountOpenFromLine(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("accounting entries")

    def fillresponse(self):
        if "SAVE" in self.params.keys():
            del self.params["SAVE"]
        entry_account = self.item.entry
        option = {'params':{'entryaccount':entry_account.id}}
        if entry_account.close:
            self.redirect_action(EntryAccountShow.get_action(), option)
        else:
            self.redirect_action(EntryAccountAddModify.get_action(), option)

@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountShow(XferShowEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Show accounting entry")

@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountAddModify(XferAddEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption_add = _("Add entry of account")
    caption_modify = _("Modify accounting entry")

    def fillresponse(self):
        XferAddEditor.fillresponse(self)
        serial_vals = self.getparam('serial_entry')
        if serial_vals is None:
            self.params['serial_entry'] = self.item.get_serial()
            serial_vals = self.getparam('serial_entry')
            six.print_(serial_vals)
        with_change = self.item.is_serial_changed(serial_vals)
        six.print_(with_change)
        btn = XferCompButton('save_modif')
        btn.set_location(3, 0, 1, 2)
        btn.set_action(self.request, self.get_action(_("Modify"), "images/edit.png"), {'params':{"SAVE":"YES"}})
        self.add_component(btn)
        if self.item.id:
            last_row = self.get_max_row() + 5
            lbl = XferCompLabelForm('sep1')
            lbl.set_location(0, last_row, 6)
            lbl.set_value("{[center]}{[hr/]}{[/center]}")
            self.add_component(lbl)
            lbl = XferCompLabelForm('sep2')
            lbl.set_location(1, last_row + 1, 5)
            lbl.set_value_center(_("Add a entry line"))
            self.add_component(lbl)
            entry_line = EntryLineAccount()
            entry_line.edit_line(self)
            btn = XferCompButton('entrybtn')
            btn.set_location(2, last_row + 4, 2)
            btn.set_action(self.request, EntryLineAccountSave.get_action(_("Add"), "images/add.png"), {'close':CLOSE_YES})
            self.add_component(btn)

            self.item.show(self)
            grid_lines = self.get_components('entrylineaccount_set')
            self.remove_component('entrylineaccount_set')
            new_grid_lines = XferCompGrid(self.field_id)
            new_grid_lines.set_model(self.item.get_entrylineaccounts(serial_vals), None, self)
            new_grid_lines.set_location(grid_lines.col, grid_lines.row, grid_lines.colspan + 2, grid_lines.rowspan)
            new_grid_lines.add_action(self.request, EntryLineAccountDel.get_action(_("Delete"), "images/delete.png"), {'close':CLOSE_YES})
            self.add_component(new_grid_lines)
        self.actions = []
        if with_change:
            self.add_action(WrapAction(_('Close'), 'images/close.png'), {})
        else:
            self.add_action(WrapAction(_('Cancel'), 'images/cancel.png'), {})

@ActionsManage.affect('EntryAccount', 'show')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountAfterSave(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Modify accounting entry")

    def fillresponse(self):
        if 'SAVE' in self.params.keys():
            del self.params['SAVE']
        self.redirect_action(EntryAccountAddModify.get_action(), {})

@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountSave(XferContainerAcknowledge):
    icon = "entry.png"
    caption = _("Save entry line of account")

    def fillresponse(self, serial_entry='', num_cpt=0, credit_val=0.0, debit_val=0.0, thirdid=0, reference='None'):
        for old_key in ['num_cpt', 'credit_val', 'debit_val', 'thirdid', 'reference']:
            if old_key in self.params.keys():
                del self.params[old_key]
        if serial_entry != '':
            serial_entry += '\n'
        serial_entry += EntryLineAccount.add_serial(num_cpt, debit_val, credit_val, thirdid, reference)
        self.redirect_action(EntryAccountAddModify.get_action(), {'params':{"serial_entry":serial_entry}})

@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountDel(XferContainerAcknowledge):
    icon = "entry.png"

    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Delete entry line of account")

    def fillresponse(self, entrylineaccount_set=0, serial_entry=''):
        serial_entry = self.item.remove_entrylineaccounts(serial_entry, entrylineaccount_set)
        self.redirect_action(EntryAccountAddModify.get_action(), {'params':{"serial_entry":serial_entry}})
