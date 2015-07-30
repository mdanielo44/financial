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
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.framework.xfercomponents import XferCompButton, XferCompGrid

from diacamma.accounting.models import FiscalYear, Journal

@ActionsManage.affect('FiscalYear', 'list')
@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_MODAL, 'contact.conf', _('Management of fiscal year and financial parameters'))
class Configuration(XferListEditor):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Accounting configuration")

    def fillresponse_header(self):
        self.new_tab(_('Fiscal year list'))

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.add_action(self.request, FiscalYearActive.get_action(), {'unique':SELECT_SINGLE, 'close':CLOSE_NO})
        self.new_tab(_('Journals'))
        journals = Journal.objects.all() # pylint: disable=no-member
        grid = XferCompGrid('journal')
        grid.set_model(journals, None, self)
        grid.add_actions(self, Journal)
        grid.set_location(0, self.get_max_row() + 1, 2)
        grid.set_size(200, 500)
        self.add_component(grid)
        self.new_tab(_('Parameters'))
        self.params['params'] = ['accounting-devise', 'accounting-devise-iso', 'accounting-devise-prec']
        Params.fill(self, self.params['params'], 1, 1)
        btn = XferCompButton('editparam')
        btn.set_location(1, self.get_max_row() + 1, 2, 1)
        btn.set_action(self.request, ParamEdit.get_action(_('Modify'), 'images/edit.png'), {'close':0})
        self.add_component(btn)

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
