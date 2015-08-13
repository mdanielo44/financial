# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    SELECT_SINGLE, CLOSE_NO, FORMTYPE_REFRESH
from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.xfercomponents import XferCompCheck, XferCompLabelForm

from diacamma.accounting.models import CostAccounting
from diacamma.accounting.views_reports import CostAccountingIncomeStatement

@ActionsManage.affect('CostAccounting', 'list')
@MenuManage.describ('accounting.change_entryaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Edition of costs accounting'))
class CostAccountingList(XferListEditor):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("costs accounting")

    def fillresponse_header(self):
        all_cost = self.getparam('all_cost', False)
        sel = XferCompCheck("all_cost")
        sel.set_value(all_cost)
        sel.set_location(1, 3)
        sel.set_action(self.request, self.get_action(), {'close':CLOSE_NO, 'modal':FORMTYPE_REFRESH})
        self.add_component(sel)
        lbl = XferCompLabelForm("all_costLbl")
        lbl.set_location(2, 3)
        lbl.set_value_as_name(_("Show all cost accounting"))
        self.add_component(lbl)
        if not all_cost:
            self.filter = Q(status=0)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.get_components('title').colspan += 1
        self.get_components('nb').colspan += 1
        grid = self.get_components(self.field_id)
        grid.colspan += 1
        grid.add_action(self.request, CostAccountingDefault.get_action(), {'unique':SELECT_SINGLE, 'close':CLOSE_NO})
        grid.add_action(self.request, CostAccountingClose.get_action(), {'unique':SELECT_SINGLE, 'close':CLOSE_NO})
        grid.add_action(self.request, CostAccountingIncomeStatement.get_action(_('Report'), 'images/print.png'), {'unique':SELECT_SINGLE, 'close':CLOSE_NO, 'modal':FORMTYPE_NOMODAL})

@MenuManage.describ('accounting.add_fiscalyear')
class CostAccountingDefault(XferContainerAcknowledge):
    icon = ""
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Default")

    def fillresponse(self):
        self.item.change_has_default()

@MenuManage.describ('accounting.add_fiscalyear')
class CostAccountingClose(XferContainerAcknowledge):
    icon = "images/ok.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Close")

    def fillresponse(self):
        if self.item.status == 0:
            if self.item.entryaccount_set.filter(close=False).count() > 0:
                raise LucteriosException(IMPORTANT, _('This costa accounting has some not validated entry!'))
            if self.confirme(_("Do you want to close this cost accounting?")):
                self.item.is_default = False
                self.item.status = 1
                self.item.save()

@ActionsManage.affect('CostAccounting', 'edit', 'add')
@MenuManage.describ('accounting.add_entryaccount')
class CostAccountingAddModify(XferAddEditor):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption_add = _("Add cost accounting")
    caption_modify = _("Modify cost accounting")

@ActionsManage.affect('CostAccounting', 'delete')
@MenuManage.describ('accounting.delete_entryaccount')
class CostAccountingDel(XferDelete):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Delete cost accounting")
