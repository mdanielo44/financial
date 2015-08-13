# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
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

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from lucterios.framework.models import get_value_if_choices
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.parameters import Params
from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect, \
    XferCompButton, XferCompGrid, XferCompEdit, XferCompFloat
from lucterios.framework.tools import FORMTYPE_REFRESH, CLOSE_NO, ActionsManage, \
    FORMTYPE_MODAL, SELECT_SINGLE, SELECT_MULTI, CLOSE_YES, WrapAction

from diacamma.accounting.models import current_system_account, FiscalYear, \
    EntryLineAccount, EntryAccount, get_amount_sum, Third, CostAccounting
from django.db.models.aggregates import Sum

class ThirdEditor(LucteriosEditor):

    def _add_filtering(self, xfer, lines_filter):
        # pylint: disable=no-self-use
        lbl = XferCompLabelForm('lbl_lines_filter')
        lbl.set_value_as_name(_('Accounts filter'))
        lbl.set_location(0, 1)
        xfer.add_component(lbl)
        edt = XferCompSelect("lines_filter")
        edt.set_select([(0, _('All entries of current fiscal year')), (1, _('Only no-closed entries of current fiscal year')), (2, _('All entries for all fiscal year'))])
        edt.set_value(lines_filter)
        edt.set_location(1, 1)
        edt.set_action(xfer.request, xfer.get_action(), {'modal':FORMTYPE_REFRESH, 'close':CLOSE_NO})
        xfer.add_component(edt)

    def show(self, xfer):
        xfer.tab = 0
        old_item = xfer.item
        xfer.item = self.item.contact.get_final_child()  # pylint: disable=no-member
        xfer.filltab_from_model(1, 1, True, ['address', ('postal_code', 'city'), 'country', ('tel1', 'tel2')])
        btn = XferCompButton('show')
        btn.set_location(2, 5, 3, 1)
        modal_name = xfer.item.__class__.__name__
        btn.set_action(xfer.request, ActionsManage.get_act_changed(modal_name, 'show', _('Show'), 'images/edit.png'), \
                {'modal':FORMTYPE_MODAL, 'close':CLOSE_NO, 'params':{modal_name.lower():six.text_type(xfer.item.id)}})
        xfer.add_component(btn)
        xfer.item = old_item
        try:
            lines_filter = xfer.getparam('lines_filter', 0)
            if lines_filter == 0:
                entry_lines_filter = Q(entry__year=FiscalYear.get_current())
            elif lines_filter == 1:
                entry_lines_filter = Q(entry__year=FiscalYear.get_current()) & Q(entry__close=False)
            else:
                entry_lines_filter = Q()
            entry_lines = self.item.entrylineaccount_set.filter(entry_lines_filter)  # pylint: disable=no-member
            xfer.new_tab(_('entry of account'))
            self._add_filtering(xfer, lines_filter)
            link_grid_lines = XferCompGrid('entrylineaccount')
            link_grid_lines.set_model(entry_lines, EntryLineAccount.get_other_fields(), xfer)
            link_grid_lines.set_location(0, 2, 2)
            link_grid_lines.add_action(xfer.request, ActionsManage.get_act_changed('EntryLineAccount', 'open', _('Edit'), 'images/edit.png'), \
                                    {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE, 'close':CLOSE_NO})
            xfer.add_component(link_grid_lines)
        except LucteriosException:
            pass

class AccountThirdEditor(LucteriosEditor):

    def edit(self, xfer):
        code_ed = xfer.get_components('code')
        code_ed.mask = current_system_account().get_third_mask()
        return

class FiscalYearEditor(LucteriosEditor):

    def edit(self, xfer):
        fiscal_years = FiscalYear.objects.order_by('end')  # pylint: disable=no-member
        xfer.change_to_readonly('status')
        # modification case
        if self.item.id is not None:  # pylint: disable=no-member
            if (len(fiscal_years) != 0) and (fiscal_years[len(fiscal_years) - 1].id != self.item.id):  # pylint: disable=no-member
                raise LucteriosException(IMPORTANT, _('This fiscal year is not the last!'))
            # modifcation and not the first in building
            if (len(fiscal_years) != 1) or (self.item.status != 0):
                xfer.change_to_readonly('begin')
        # creation and not the first
        elif len(fiscal_years) > 0:
            xfer.params['last_fiscalyear'] = fiscal_years[len(fiscal_years) - 1].id
            xfer.params['begin'] = self.item.begin.isoformat()
            xfer.change_to_readonly('begin')
        if self.item.status == 2:
            xfer.change_to_readonly('end')

    def before_save(self, xfer):
        if self.item.end < self.item.begin:
            raise LucteriosException(IMPORTANT, _("end of fiscal year must be after begin!"))
        if self.item.id is None and (len(FiscalYear.objects.all()) == 0):  # pylint: disable=no-member
            self.item.is_actif = True
        return

    def run_begin(self, xfer):
        if self.item.status == 0:
            nb_entry_noclose = EntryLineAccount.objects.filter(entry__journal__id=1, entry__close=False, account__year=self.item).count()  # pylint: disable=no-member
            if nb_entry_noclose > 0:
                raise LucteriosException(IMPORTANT, _("Some enties for last year report are not closed!"))
            if current_system_account().check_begin(self.item, xfer):
                self.item.status = 1
                self.item.save()

    def run_close(self, xfer):
        if self.item.status == 0:
            raise LucteriosException(IMPORTANT, _("This fiscal year is not 'in running'!"))
        nb_entry_noclose = EntryAccount.objects.filter(close=False, entrylineaccount__account__year=self.item).distinct().count()  # pylint: disable=no-member
        if (nb_entry_noclose > 0) and (FiscalYear.objects.filter(last_fiscalyear=self.item).count() == 0):  # pylint: disable=no-member
            raise LucteriosException(IMPORTANT, _("This fiscal year has entries not closed and not next fiscal year!"))
        if current_system_account().check_end(self.item, xfer, nb_entry_noclose):
            self.item.status = 2
            self.item.save()

class CostAccountingEditor(LucteriosEditor):

    def edit(self, xfer):
        if self.item.status == 1:
            xfer.change_to_readonly('name')
            xfer.change_to_readonly('description')
            xfer.change_to_readonly('last_costaccounting')
        elif self.item.id is not None:
            sel = xfer.get_components('last_costaccounting')
            sel.set_select_query(CostAccounting.objects.all().exclude(id=self.item.id))  # pylint: disable=no-member

    def before_save(self, xfer):
        if self.item.id is None and (len(CostAccounting.objects.all()) == 0):  # pylint: disable=no-member
            self.item.is_default = True
        return

class ChartsAccountEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('type_of_account')
        code_ed = xfer.get_components('code')
        code_ed.mask = current_system_account().get_general_mask()
        code_ed.set_action(xfer.request, xfer.get_action(), {'modal':FORMTYPE_REFRESH, 'close':CLOSE_NO})
        descript, typeaccount = current_system_account().new_charts_account(self.item.code)
        error_msg = ''
        if typeaccount < 0:
            if typeaccount == -2:
                error_msg = _("Invalid code")
            if self.item.code != '':
                code_ed.set_value(self.item.code + '!')
            if self.item.id is None:  # pylint: disable=no-member
                xfer.get_components('type_of_account').set_value('---')
        elif self.item.id is None:  # pylint: disable=no-member
            field_type = self.item.get_field_by_name('type_of_account')
            xfer.get_components('type_of_account').set_value(get_value_if_choices(typeaccount, field_type))
            xfer.get_components('name').set_value(descript)
            xfer.params['type_of_account'] = typeaccount
        elif typeaccount != self.item.type_of_account:
            error_msg = _("Changment not allowed!")
            code_ed.set_value(self.item.code + '!')
        lbl = XferCompLabelForm('error_code')
        lbl.set_location(1, xfer.get_max_row() + 1, 2)
        lbl.set_value_center("{[font color='red']}%s{[/font]}" % error_msg)
        xfer.add_component(lbl)
        return

    def show(self, xfer):
        if self.item.is_third:
            fieldnames = ['entry.num', 'entry.date_entry', 'entry.date_value', 'third', 'entry.designation', (_('debit'), 'debit'), (_('credit'), 'credit'), 'entry.link']
        elif self.item.is_cash:
            fieldnames = ['entry.num', 'entry.date_entry', 'entry.date_value', 'reference', 'entry.designation', (_('debit'), 'debit'), (_('credit'), 'credit'), 'entry.link']
        else:
            fieldnames = ['entry.num', 'entry.date_entry', 'entry.date_value', 'entry.designation', (_('debit'), 'debit'), (_('credit'), 'credit'), 'entry.link']
        row = xfer.get_max_row() + 1
        lbl = XferCompLabelForm('lbl_entrylineaccount')
        lbl.set_location(1, row)
        lbl.set_value_as_name(EntryLineAccount._meta.verbose_name)  # pylint: disable=protected-access,no-member
        xfer.add_component(lbl)
        comp = XferCompGrid('entrylineaccount')
        comp.set_model(self.item.entrylineaccount_set.all(), fieldnames, xfer)  # pylint: disable=no-member
        comp.add_action(xfer.request, ActionsManage.get_act_changed('EntryLineAccount', 'open', _('Edit'), 'images/edit.png'), \
                                    {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE, 'close':CLOSE_NO})
        if self.item.is_third:
            comp.add_action(xfer.request, ActionsManage.get_act_changed('EntryLineAccount', 'link', _('Link/Unlink'), ''), \
                                        {'modal':FORMTYPE_MODAL, 'unique':SELECT_MULTI, 'close':CLOSE_NO})
        comp.set_location(2, row)
        xfer.add_component(comp)

class EntryAccountEditor(LucteriosEditor):

    def before_save(self, xfer):
        # pylint: disable=no-member
        if self.item.date_value > self.item.year.end.isoformat():
            self.item.date_value = self.item.year.end.isoformat()
        if self.item.date_value < self.item.year.begin.isoformat():
            self.item.date_value = self.item.year.begin.isoformat()
        return

    def _add_cost_savebtn(self, xfer):
        name_comp = xfer.get_components('designation')
        if (self.item.costaccounting is None) or (self.item.costaccounting.status == 0):
            xfer.fill_from_model(1, name_comp.row + 1, False, ['costaccounting'])
            sel = xfer.get_components('costaccounting')
            sel.set_select_query(CostAccounting.objects.filter(status=0))  # pylint: disable=no-member
            added = True
        else:
            xfer.fill_from_model(1, name_comp.row + 1, True, ['costaccounting'])
            added = isinstance(name_comp, XferCompEdit)
        if added:
            btn = XferCompButton('save_modif')
            btn.set_location(3, 0, 1, 2)
            btn.set_action(xfer.request, xfer.get_action(_("Modify"), "images/edit.png"), {'params':{"SAVE":"YES"}})
            xfer.add_component(btn)

    def show(self, xfer):
        self._add_cost_savebtn(xfer)
        last_row = xfer.get_max_row() + 10
        lbl = XferCompLabelForm('sep3')
        lbl.set_location(0, last_row + 1, 6)
        lbl.set_value_center("{[hr/]}")
        xfer.add_component(lbl)
        xfer.filltab_from_model(1, last_row + 2, True, ['entrylineaccount_set'])
        grid_lines = xfer.get_components('entrylineaccount')
        grid_lines.actions = []
        if self.item.has_third:
            sum_customer = get_amount_sum(self.item.entrylineaccount_set.filter(account__code__regex=current_system_account().get_third_mask()).aggregate(Sum('amount')))  # pylint: disable=no-member
            if ((sum_customer < 0) and not self.item.has_cash) or ((sum_customer > 0) and self.item.has_cash):
                lbl = XferCompLabelForm('asset_warning')
                lbl.set_location(0, last_row + 3, 6)
                lbl.set_value_as_header(_("entry of accounting for an asset"))
                xfer.add_component(lbl)
        if self.item.link is not None:
            entrylines = EntryLineAccount.objects.filter(entry__link=self.item.link).exclude(entry__id=self.item.id)  # pylint: disable=no-member
            lbl = XferCompLabelForm('sep4')
            lbl.set_location(0, last_row + 4, 6)
            lbl.set_value_center("{[hr/]}")
            xfer.add_component(lbl)
            lbl = XferCompLabelForm('entrylinklab')
            lbl.set_location(1, last_row + 5, 5)
            lbl.set_value_center(_("Linked entries"))
            xfer.add_component(lbl)
            link_grid_lines = XferCompGrid('entrylineaccount_link')
            link_grid_lines.set_model(entrylines, EntryLineAccount.get_other_fields(), xfer)
            link_grid_lines.set_location(1, last_row + 6, 5)
            link_grid_lines.add_action(xfer.request, ActionsManage.get_act_changed('EntryLineAccount', 'open', _('Edit'), 'images/edit.png'), \
                            {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE, 'close':CLOSE_YES})
            xfer.add_component(link_grid_lines)

    def _entryline_editor(self, xfer, serial_vals, debit_rest, credit_rest):
        last_row = xfer.get_max_row() + 5
        lbl = XferCompLabelForm('sep1')
        lbl.set_location(0, last_row, 6)
        lbl.set_value("{[center]}{[hr/]}{[/center]}")
        xfer.add_component(lbl)
        lbl = XferCompLabelForm('sep2')
        lbl.set_location(1, last_row + 1, 5)
        lbl.set_value_center(_("Add a entry line"))
        xfer.add_component(lbl)
        entry_line = EntryLineAccount()
        entry_line.editor.edit_line(xfer, 0, last_row + 2, debit_rest, credit_rest)  # pylint: disable=no-member
        if entry_line.has_account:
            btn = XferCompButton('entrybtn')
            btn.set_location(3, last_row + 5)
            btn.set_action(xfer.request, ActionsManage.get_act_changed('EntryAccount', 'addentity', _("Add"), "images/add.png"), {'close':CLOSE_YES})
            xfer.add_component(btn)
        self.item.editor.show(xfer)
        grid_lines = xfer.get_components('entrylineaccount')
        xfer.remove_component('entrylineaccount')
        new_grid_lines = XferCompGrid('entrylineaccount_serial')
        new_grid_lines.set_model(self.item.get_entrylineaccounts(serial_vals), None, xfer)
        new_grid_lines.set_location(grid_lines.col, grid_lines.row, grid_lines.colspan + 2, grid_lines.rowspan)
        new_grid_lines.add_action(xfer.request, ActionsManage.get_act_changed('EntryAccount', 'change', _("Edit"), "images/edit.png"), \
                                  {'close':CLOSE_YES, 'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        new_grid_lines.add_action(xfer.request, ActionsManage.get_act_changed('EntryAccount', 'remove', _("Delete"), "images/delete.png"), \
                                  {'close':CLOSE_YES, 'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        xfer.add_component(new_grid_lines)
        nb_lines = len(new_grid_lines.record_ids)
        return nb_lines

    def _remove_lastyear_notbuilding(self, xfer):
        if self.item.year.status != 0:
            cmp_journal = xfer.get_components('journal')
            select_list = cmp_journal.select_list
            for item_idx in range(len(select_list)):
                if select_list[item_idx][0] == 1:
                    del select_list[item_idx]
                    break
            cmp_journal.select_list = select_list

    def _change_buttons(self, xfer, no_change, debit_rest, credit_rest, nb_lines):
        xfer.actions = []
        if no_change:
            if (self.item.link is None) and self.item.has_third and not self.item.has_cash:
                xfer.add_action(ActionsManage.get_act_changed('EntryAccount', 'payement', _('Payment'), ''), {'close':CLOSE_YES})
            xfer.add_action(ActionsManage.get_act_changed('EntryAccount', 'reverse', _('Reverse'), 'images/edit.png'), {'close':CLOSE_YES})
            xfer.add_action(WrapAction(_('Close'), 'images/close.png'), {})
        else:
            if (debit_rest < 0.0001) and (credit_rest < 0.0001) and (nb_lines > 0):
                xfer.add_action(ActionsManage.get_act_changed('EntryAccount', 'validate', _('Ok'), 'images/ok.png'), {})
            if self.item.id is None:
                xfer.add_action(WrapAction(_('Cancel'), 'images/cancel.png'), {})
            else:
                xfer.add_action(ActionsManage.get_act_changed('EntryAccount', 'unlock', _('Cancel'), 'images/cancel.png'), {})

    def edit(self, xfer):
        self._remove_lastyear_notbuilding(xfer)
        serial_vals = xfer.getparam('serial_entry')
        if serial_vals is None:
            xfer.params['serial_entry'] = self.item.get_serial()
            serial_vals = xfer.getparam('serial_entry')
        no_change, debit_rest, credit_rest = self.item.serial_control(serial_vals)
        if self.item.id:
            nb_lines = self._entryline_editor(xfer, serial_vals, debit_rest, credit_rest)
        else:
            self._add_cost_savebtn(xfer)
            nb_lines = 0
        self._change_buttons(xfer, no_change, debit_rest, credit_rest, nb_lines)

class EntryLineAccountEditor(LucteriosEditor):

    def edit_account_for_line(self, xfer, column, row, debit_rest, credit_rest):
        # pylint: disable=too-many-locals
        num_cpt_txt = xfer.getparam('num_cpt_txt', '')
        num_cpt = xfer.getparam('num_cpt', 0)

        lbl = XferCompLabelForm('numCptlbl')
        lbl.set_location(column, row, 3)
        lbl.set_value_as_headername(_('account'))
        xfer.add_component(lbl)
        edt = XferCompEdit('num_cpt_txt')
        edt.set_location(column, row + 1, 2)
        edt.set_value(num_cpt_txt)
        edt.set_size(20, 25)
        edt.set_action(xfer.request, xfer.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
        xfer.add_component(edt)
        sel_val = []
        current_account = None
        if num_cpt_txt != '':
            year = FiscalYear.get_current(xfer.getparam('year'))
            sel_val, current_account = year.get_account_list(num_cpt_txt, num_cpt)
        sel = XferCompSelect('num_cpt')
        sel.set_location(column + 2, row + 1, 1)
        sel.set_select(sel_val)
        sel.set_size(20, 150)
        sel.set_action(xfer.request, xfer.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
        if current_account is not None:
            sel.set_value(current_account.id)
            self.item.account = current_account
            self.item.set_montant(float(xfer.getparam('debit_val', 0.0)), float(xfer.getparam('credit_val', 0.0)))
            if abs(self.item.amount) < 0.0001:
                self.item.set_montant(debit_rest, credit_rest)
        xfer.add_component(sel)
        return lbl, edt

    def edit_extra_for_line(self, xfer, column, row, vertical=True):
        try:
            if self.item.has_account and self.item.account.is_third:
                lbl = XferCompLabelForm('thirdlbl')
                lbl.set_value_as_name(_('third'))
                sel_thirds = [(0, '---')]
                for third in Third.objects.filter(accountthird__code=self.item.account.code):  # pylint: disable=no-member
                    sel_thirds.append((third.id, six.text_type(third)))
                cb_third = XferCompSelect('third')
                cb_third.set_select(sel_thirds)
                if self.item.third is None:
                    cb_third.set_value(xfer.getparam('third', 0))
                else:
                    cb_third.set_value(xfer.getparam('third', self.item.third.id))
                if vertical:
                    cb_third.set_location(column, row + 1)
                    lbl.set_location(column, row)
                else:
                    cb_third.set_location(column + 2, row)
                    lbl.set_location(column, row, 2)
                xfer.add_component(lbl)
                xfer.add_component(cb_third)
            elif self.item.account.is_cash:
                lbl = XferCompLabelForm('referencelbl')
                lbl.set_value_as_name(_('reference'))
                edt = XferCompEdit('reference')
                reference = xfer.getparam('reference', self.item.reference)
                if reference is not None:
                    edt.set_value(reference)
                if vertical:
                    edt.set_location(column, row + 1)
                    lbl.set_location(column, row)
                else:
                    edt.set_location(column + 2, row)
                    lbl.set_location(column, row, 2)
                xfer.add_component(lbl)
                xfer.add_component(edt)
        except ObjectDoesNotExist:
            pass

    def edit_creditdebit_for_line(self, xfer, column, row):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        lbl = XferCompLabelForm('debitlbl')
        lbl.set_location(column, row, 2)
        lbl.set_value_as_name(_('debit'))
        xfer.add_component(lbl)
        edt = XferCompFloat('debit_val', -10000000, 10000000, currency_decimal)
        edt.set_location(column + 2, row)
        edt.set_value(self.item.get_debit())
        edt.set_size(20, 75)
        xfer.add_component(edt)
        lbl = XferCompLabelForm('creditlbl')
        lbl.set_location(column, row + 1, 2)
        lbl.set_value_as_name(_('credit'))
        xfer.add_component(lbl)
        edt = XferCompFloat('credit_val', -10000000, 10000000, currency_decimal)
        edt.set_location(column + 2, row + 1)
        edt.set_value(self.item.get_credit())
        edt.set_size(20, 75)
        xfer.add_component(edt)

    def edit_line(self, xfer, init_col, init_row, debit_rest, credit_rest):
        self.edit_account_for_line(xfer, init_col, init_row, debit_rest, credit_rest)
        self.edit_creditdebit_for_line(xfer, init_col, init_row + 2)
        self.edit_extra_for_line(xfer, init_col + 3, init_row)
