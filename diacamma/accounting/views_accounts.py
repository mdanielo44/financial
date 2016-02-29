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

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE, FORMTYPE_MODAL, WrapAction,\
    SELECT_MULTI
from lucterios.framework.xfercomponents import XferCompLabelForm
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.xferprint import XferPrintListing
from lucterios.CORE.views import ObjectMerge

from diacamma.accounting.models import ChartsAccount, FiscalYear
from lucterios.framework import signal_and_lock

MenuManage.add_sub("bookkeeping", "financial", "diacamma.accounting/images/accounting.png",
                   _("Bookkeeping"), _("Manage of Bookkeeping"), 30)


@ActionsManage.affect('ChartsAccount', 'list')
@MenuManage.describ('accounting.change_chartsaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Editing and modifying of Charts of accounts for current fiscal year'))
class ChartsAccountList(XferListEditor):
    icon = "account.png"
    model = ChartsAccount
    field_id = 'chartsaccount'
    caption = _("charts of account")
    multi_page = False

    def fillresponse_header(self):
        select_year = self.getparam('year')
        select_type = self.getparam('type_of_account', 0)
        self.item.year = FiscalYear.get_current(select_year)
        self.fill_from_model(0, 1, False, ['year', 'type_of_account'])
        self.get_components('year').set_action(self.request, self.get_action(),
                                               {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        type_of_account = self.get_components('type_of_account')
        type_of_account.select_list.append((-1, '---'))
        type_of_account.set_value(select_type)
        type_of_account.set_action(self.request, ChartsAccountList.get_action(
            modal=FORMTYPE_REFRESH), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        self.filter = Q(year=self.item.year)
        if select_type != -1:
            self.filter &= Q(type_of_account=select_type)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        if self.item.year.status == 2:
            grid_charts = self.get_components('chartsaccount')
            grid_charts.actions = []
            grid_charts.add_action(self.request, ActionsManage.get_act_changed('ChartsAccount', 'show', _(
                "Edit"), "images/edit.png"), {'modal': FORMTYPE_MODAL, 'unique': SELECT_SINGLE})
        else:
            grid_charts = self.get_components('chartsaccount')
            if self.item.year.last_fiscalyear is not None:
                grid_charts.add_action(self.request, FiscalYearImport.get_action(
                    _("import"), ''), {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO})
            if WrapAction.is_permission(self.request, 'accounting.add_chartsaccount'):
                self.get_components(self.field_id).add_action(self.request, ObjectMerge.get_action(
                    _("Merge"), "images/clone.png"), {'close': CLOSE_NO, 'unique': SELECT_MULTI, 'params': {'modelname': self.model.get_long_name(), 'field_id': self.field_id}})
            if signal_and_lock.Signal.call_signal("initial_account", None) > 0:
                grid_charts.add_action(self.request, ChartsAccountInitial.get_action(
                    _("initial"), 'images/add.png'), {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO})
        lbl = XferCompLabelForm("result")
        lbl.set_value_center(self.item.year.total_result_text)
        lbl.set_location(0, 10, 2)
        self.add_component(lbl)

        accompt_returned = []
        all_codes = list(
            self.item.year.chartsaccount_set.all().values_list('code', flat=True))
        all_codes.append('')
        Signal.call_signal("compte_no_found", all_codes, accompt_returned)
        lbl = XferCompLabelForm("CompteNoFound")
        if len(accompt_returned) > 0:
            lbl.set_value("{[u]}{[b]}%s{[/b]}{[/u]}{[br]}%s" % (
                _("Using codes unknows in this account chart:"), "{[br/]}".join(accompt_returned)))
        lbl.set_location(0, 11, 2)
        self.add_component(lbl)

        if self.item.year.status == 0:
            self.add_action(FiscalYearBegin.get_action(
                _('Begin'), 'images/ok.png'), {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO}, 0)
            if (self.item.year.last_fiscalyear is not None) and self.item.year.has_no_lastyear_entry and (self.item.year.last_fiscalyear.status == 2):
                self.add_action(FiscalYearReportLastYear.get_action(
                    _('Last fiscal year'), 'images/edit.png'), {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO}, 0)
        if self.item.year.status == 1:
            self.add_action(FiscalYearClose.get_action(
                _('Closing'), 'images/ok.png'), {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO}, 0)


@MenuManage.describ('accounting.add_chartsaccount')
class ChartsAccountInitial(XferContainerAcknowledge):
    icon = "account.png"
    model = ChartsAccount
    field_id = 'chartsaccount'
    caption = _("Add initial charts of account")

    def fillresponse(self, confirme):
        account_list = []
        signal_and_lock.Signal.call_signal("initial_account", account_list)
        if self.confirme(_('Do you want to import initial accounts?')):
            ChartsAccount.import_initial(
                FiscalYear.get_current(self.getparam('year')), account_list)


@ActionsManage.affect('ChartsAccount', 'listing')
@MenuManage.describ('accounting.change_chartsaccount')
class ChartsAccountListing(XferPrintListing):
    icon = "account.png"
    model = ChartsAccount
    field_id = 'chartsaccount'
    caption = _("Listing charts of account")

    def get_filter(self):
        if self.getparam('CRITERIA') is None:
            select_year = self.getparam('year')
            select_type = self.getparam('type_of_account', 0)
            new_filter = Q(year=FiscalYear.get_current(select_year))
            if select_type != -1:
                new_filter &= Q(type_of_account=select_type)
        else:
            new_filter = XferPrintListing.get_filter(self)
        return new_filter


@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearImport(XferContainerAcknowledge):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'year'
    caption = _("Import charts accounts from last fiscal year")

    def fillresponse(self):
        if self.confirme(_("Do you want to import last year charts accounts?")):
            self.item.import_charts_accounts()


@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearReportLastYear(XferContainerAcknowledge):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'year'
    caption = _("Last fiscal year import")

    def fillresponse(self):
        if self.confirme(_('Do you want to import last year result?')):

            self.item.run_report_lastyear()


@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearBegin(XferContainerAcknowledge):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'year'
    caption_add = _("Begin fiscal year")

    def fillresponse(self):
        self.item.editor.run_begin(self)


@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearClose(XferContainerAcknowledge):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'year'
    caption_add = _("Close fiscal year")

    def fillresponse(self):
        self.item.editor.run_close(self)


@ActionsManage.affect('ChartsAccount', 'modify', 'add')
@MenuManage.describ('accounting.add_chartsaccount')
class ChartsAccountAddModify(XferAddEditor):
    icon = "account.png"
    model = ChartsAccount
    field_id = 'chartsaccount'
    caption_add = _("Add an account")
    caption_modify = _("Modify an account")
    redirect_to_show = None

    def fill_simple_fields(self):
        for old_key in ['type_of_account']:
            if old_key in self.params.keys():
                del self.params[old_key]
        return XferAddEditor.fill_simple_fields(self)


@ActionsManage.affect('ChartsAccount', 'show')
@MenuManage.describ('accounting.change_chartsaccount')
class ChartsAccountShow(XferShowEditor):
    icon = "account.png"
    model = ChartsAccount
    field_id = 'chartsaccount'
    caption = _("Show an account")

    def fillresponse(self):
        if self.item.year.status > 1:
            self.action_list = []
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('ChartsAccount', 'delete')
@MenuManage.describ('accounting.delete_chartsaccount')
class ChartsAccountDel(XferDelete):
    icon = "account.png"
    model = ChartsAccount
    field_id = 'chartsaccount'
    caption = _("Delete an account")
