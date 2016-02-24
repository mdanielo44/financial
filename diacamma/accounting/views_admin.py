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

from lucterios.framework.xferadvance import XferListEditor, XferDelete
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.tools import FORMTYPE_MODAL, ActionsManage, MenuManage, \
    SELECT_SINGLE, CLOSE_NO
from lucterios.framework.xfergraphic import XferContainerAcknowledge,\
    XferContainerCustom
from lucterios.framework.xfercomponents import XferCompButton, XferCompGrid, \
    XferCompLabelForm, XferCompSelect, XferCompImage, XferCompDownLoad
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.CORE.models import Parameter

from diacamma.accounting.models import FiscalYear, Journal, AccountThird, ChartsAccount, ModelLineEntry
from diacamma.accounting.system import accounting_system_list, \
    accounting_system_name

from diacamma.accounting.tools import clear_system_account, correct_accounting_code
from lucterios.framework import signal_and_lock

MenuManage.add_sub(
    "financial.conf", "core.extensions", "", _("Financial"), "", 2)


@ActionsManage.affect('FiscalYear', 'list')
@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_MODAL, 'financial.conf', _('Management of fiscal year and financial parameters'))
class Configuration(XferListEditor):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Accounting configuration")

    def fillresponse_header(self):
        self.new_tab(_('Fiscal year list'))
        current_account_system = Params.getvalue("accounting-system")
        lbl = XferCompLabelForm('lbl_account_system')
        lbl.set_value_as_name(_('accounting system'))
        lbl.set_location(0, 1)
        self.add_component(lbl)
        if current_account_system == '':
            edt = XferCompSelect("account_system")
            account_systems = list(accounting_system_list().items())
            account_systems.insert(0, ('', '---'))
            edt.set_select(account_systems)
            edt.set_action(self.request, ConfigurationAccountingSystem.get_action(), {
                           'modal': FORMTYPE_MODAL, 'close': CLOSE_NO})
        else:
            edt = XferCompLabelForm("account_system")
        edt.set_value(accounting_system_name(current_account_system))
        edt.set_location(1, 1)
        self.add_component(edt)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.add_action(self.request, FiscalYearActive.get_action(), {
                        'unique': SELECT_SINGLE, 'close': CLOSE_NO})
        grid.add_action(self.request, FiscalYearExport.get_action(), {
                        'unique': SELECT_SINGLE, 'close': CLOSE_NO})
        self.new_tab(_('Journals'))
        journals = Journal.objects.all()
        grid = XferCompGrid('journal')
        grid.set_model(journals, None, self)
        grid.add_actions(self, Journal)
        grid.set_location(0, self.get_max_row() + 1, 2)
        grid.set_size(200, 500)
        self.add_component(grid)
        self.new_tab(_('Parameters'))
        self.params['params'] = [
            'accounting-devise', 'accounting-devise-iso', 'accounting-devise-prec', 'accounting-sizecode']
        Params.fill(self, self.params['params'], 1, 1)
        btn = XferCompButton('editparam')
        btn.set_location(1, self.get_max_row() + 1, 2, 1)
        btn.set_action(self.request, ParamEdit.get_action(
            _('Modify'), 'images/edit.png'), {'close': 0})
        self.add_component(btn)


@MenuManage.describ('accounting.add_fiscalyear')
class ConfigurationAccountingSystem(XferContainerAcknowledge):

    def fillresponse(self, account_system=''):
        if account_system != '':
            if self.confirme(_('Do you confirm to select "%s" like accounting system?{[br/]}{[br/]}{[i]}{[u]}Warning{[/u]}: This choose is definitive.{[/i]}') %
                             accounting_system_name(account_system)):
                Parameter.change_value('accounting-system', account_system)
                Params.clear()
                clear_system_account()


@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearActive(XferContainerAcknowledge):
    icon = "images/ok.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Activate")

    def fillresponse(self):
        self.item.set_has_actif()


@ActionsManage.affect('FiscalYear', 'edit', 'modify', 'add')
@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearAddModify(XferAddEditor):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption_add = _("Add fiscal year")
    caption_modify = _("Modify fiscal year")

    def fillresponse(self):
        if self.item.id is None:
            if Params.getvalue("accounting-system") == '':
                raise LucteriosException(
                    IMPORTANT, _('Account system not defined!'))
            self.item.init_dates()
        XferAddEditor.fillresponse(self)


@ActionsManage.affect('FiscalYear', 'delete')
@MenuManage.describ('accounting.delete_fiscalyear')
class FiscalYearDel(XferDelete):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Delete fiscal year")


@ActionsManage.affect('Journal', 'edit', 'add')
@MenuManage.describ('accounting.add_fiscalyear')
class JournalAddModify(XferAddEditor):
    icon = "entry.png"
    model = Journal
    field_id = 'journal'
    caption_add = _("Add accounting journal")
    caption_modify = _("Modify accounting journal")


@ActionsManage.affect('Journal', 'delete')
@MenuManage.describ('accounting.delete_fiscalyear')
class JournalDel(XferDelete):
    icon = "entry.png"
    model = Journal
    field_id = 'journal'
    caption = _("Delete accounting journal")


@MenuManage.describ('accounting.change_fiscalyear')
class FiscalYearExport(XferContainerCustom):
    icon = "entry.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Export")

    def fillresponse(self):
        if self.getparam("year") is None:
            self.item = FiscalYear.get_current()
        destination_file = self.item.get_xml_export()
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(_('Export fiscal year'))
        lbl.set_location(1, 0)
        self.add_component(lbl)
        down = XferCompDownLoad('filename')
        down.compress = False
        down.set_value('export_year_%s_%s.xml' %
                       (self.item.begin.isoformat(), self.item.end.isoformat()))
        down.set_download(destination_file)
        down.set_location(1, 1)
        self.add_component(down)


@signal_and_lock.Signal.decorate('param_change')
def paramchange_accounting(params):
    if 'accounting-sizecode' in params:
        for account in AccountThird.objects.all():
            if account.code != correct_accounting_code(account.code):
                account.code = correct_accounting_code(account.code)
                account.save()
        for charts_account in ChartsAccount.objects.filter(year__status__in=(0, 1)):
            if charts_account.code != correct_accounting_code(charts_account.code):
                charts_account.code = correct_accounting_code(
                    charts_account.code)
                charts_account.save()
        for model_line in ModelLineEntry.objects.all():
            if model_line.code != correct_accounting_code(model_line.code):
                model_line.code = correct_accounting_code(model_line.code)
                model_line.save()
