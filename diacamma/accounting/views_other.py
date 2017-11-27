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

from diacamma.accounting.models import CostAccounting, ModelLineEntry, ModelEntry


@MenuManage.describ('accounting.change_entryaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Edition of costs accounting'))
class CostAccountingList(XferListEditor):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("costs accounting")

    def fillresponse_header(self):
        self.filter = Q()

        status_filter = self.getparam('status', -1)
        if status_filter != -1:
            self.filter &= Q(status=status_filter)
        self.status = status_filter

        select_year = self.getparam('year', 0)
        if select_year > 0:
            self.filter &= Q(year_id=select_year)
        if select_year == -1:
            self.filter &= Q(year__isnull=True)
        self.fill_from_model(1, 4, False, ['status', 'year'])
        comp_year = self.get_components('year')
        comp_year.select_list.append((-1, _('- without fiscal year -')))
        comp_year.set_value(select_year)
        comp_year.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        comp_status = self.get_components('status')
        comp_status.select_list.insert(0, (-1, None))
        comp_status.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.get_components('title').colspan += 1
        self.get_components('costaccounting').colspan += 1


@ActionsManage.affect_grid(_("Default"), "", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.getparam('status', 0) != 1)
@MenuManage.describ('accounting.add_fiscalyear')
class CostAccountingDefault(XferContainerAcknowledge):
    icon = ""
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Default")

    def fillresponse(self):
        self.item.change_has_default()


@ActionsManage.affect_grid(_("Close"), "images/ok.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.getparam('status', 0) != 1)
@MenuManage.describ('accounting.add_fiscalyear')
class CostAccountingClose(XferContainerAcknowledge):
    icon = "images/ok.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Close")
    readonly = True

    def fillresponse(self):
        if self.item.status == 0:
            if self.item.is_protected:
                raise LucteriosException(IMPORTANT, _("This cost accounting is protected by other modules!"))
            self.item.check_before_close()
            if self.confirme(_("Do you want to close this cost accounting?")):
                self.item.close()


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", unique=SELECT_NONE, condition=lambda xfer, gridname='': xfer.getparam('status', 0) != 1)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.getparam('status', 0) != 1)
@MenuManage.describ('accounting.add_entryaccount')
class CostAccountingAddModify(XferAddEditor):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption_add = _("Add cost accounting")
    caption_modify = _("Modify cost accounting")

    def fillresponse(self):
        if 'status' in self.params.keys():
            del self.params['status']
        if (self.item.id is not None) and self.item.is_protected:
            raise LucteriosException(IMPORTANT, _("This cost accounting is protected by other modules!"))
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status', 0) != 1)
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
