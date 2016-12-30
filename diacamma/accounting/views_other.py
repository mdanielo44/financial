# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferDelete, XferShowEditor, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE, TITLE_EDIT
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, SELECT_SINGLE, FORMTYPE_REFRESH, SELECT_MULTI, SELECT_NONE, CLOSE_NO, CLOSE_YES
from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.xfercomponents import XferCompCheck, XferCompLabelForm

from diacamma.accounting.models import CostAccounting, ModelLineEntry, ModelEntry


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
        sel.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
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
        self.get_components('costaccounting').colspan += 1
        self.get_components('nb_costaccounting').colspan += 1


@ActionsManage.affect_grid(_("Default"), "", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_fiscalyear')
class CostAccountingDefault(XferContainerAcknowledge):
    icon = ""
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Default")

    def fillresponse(self):
        self.item.change_has_default()


@ActionsManage.affect_grid(_("Close"), "images/ok.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_fiscalyear')
class CostAccountingClose(XferContainerAcknowledge):
    icon = "images/ok.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Close")

    def fillresponse(self):
        if self.item.status == 0:
            if self.item.is_protected:
                raise LucteriosException(IMPORTANT, _("This cost accounting is protected by other modules!"))
            self.item.check_before_close()
            if self.confirme(_("Do you want to close this cost accounting?")):
                self.item.close()


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", unique=SELECT_NONE)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_entryaccount')
class CostAccountingAddModify(XferAddEditor):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption_add = _("Add cost accounting")
    caption_modify = _("Modify cost accounting")

    def fillresponse(self):
        if (self.item.id is not None) and self.item.is_protected:
            raise LucteriosException(IMPORTANT, _("This cost accounting is protected by other modules!"))
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('accounting.delete_entryaccount')
class CostAccountingDel(XferDelete):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Delete cost accounting")


@MenuManage.describ('accounting.change_entryaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Edition of entry model'),)
class ModelEntryList(XferListEditor):
    icon = "entryModel.png"
    model = ModelEntry
    field_id = 'modelentry'
    caption = _("Models of entry")


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", unique=SELECT_NONE)
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES)
@MenuManage.describ('accounting.add_entryaccount')
class ModelEntryAddModify(XferAddEditor):
    icon = "entryModel.png"
    model = ModelEntry
    field_id = 'modelentry'
    caption_add = _("Add model of entry")
    caption_modify = _("Modify model of entry")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.change_entryaccount')
class ModelEntryShow(XferShowEditor):
    icon = "entryModel.png"
    model = ModelEntry
    field_id = 'modelentry'
    caption = _("Show Model of entry")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('accounting.delete_entryaccount')
class ModelEntryDel(XferDelete):
    icon = "entryModel.png"
    model = ModelEntry
    field_id = 'modelentry'
    caption = _("Delete Model of entry")


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", unique=SELECT_NONE)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_entryaccount')
class ModelLineEntryAddModify(XferAddEditor):
    icon = "entryModel.png"
    model = ModelLineEntry
    field_id = 'modellineentry'
    caption_add = _("Add model line  of entry")
    caption_modify = _("Modify model line  of entry")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('accounting.delete_entryaccount')
class ModelLineEntryDel(XferDelete):
    icon = "entryModel.png"
    model = ModelLineEntry
    field_id = 'modellineentry'
    caption = _("Delete Model line  of entry")
