# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferDelete, XferShowEditor, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE, TITLE_EDIT
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, SELECT_SINGLE, FORMTYPE_REFRESH, WrapAction, SELECT_MULTI, SELECT_NONE
from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.xfercomponents import XferCompCheck, XferCompLabelForm, XferCompImage, XferCompSelect, XferCompFloat

from diacamma.accounting.models import CostAccounting, ModelLineEntry, ModelEntry, EntryAccount, FiscalYear
from diacamma.accounting.views_entries import EntryAccountEdit


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
        sel.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH)
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
            EntryAccount.clear_ghost()
            if self.item.entryaccount_set.filter(close=False).count() > 0:
                raise LucteriosException(IMPORTANT, _('This costa accounting has some not validated entry!'))
            if self.confirme(_("Do you want to close this cost accounting?")):
                self.item.is_default = False
                self.item.status = 1
                self.item.save()


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", unique=SELECT_NONE)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/modify.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_entryaccount')
class CostAccountingAddModify(XferAddEditor):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption_add = _("Add cost accounting")
    caption_modify = _("Modify cost accounting")


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
@ActionsManage.affect_grid(TITLE_MODIFY, "images/modify.png", unique=SELECT_SINGLE)
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
@ActionsManage.affect_grid(TITLE_MODIFY, "images/modify.png", unique=SELECT_SINGLE)
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


@MenuManage.describ('accounting.add_entryaccount')
class ModelEntrySelector(XferContainerAcknowledge):
    icon = "entryModel.png"
    model = ModelEntry
    field_id = 'model'
    caption = _("Select model of entry")

    def fillresponse(self, journal=0):
        if self.getparam('SAVE') is None:
            dlg = self.create_custom()
            image = XferCompImage('image')
            image.set_value(self.icon_path())
            image.set_location(0, 0, 1, 6)
            dlg.add_component(image)
            lbl = XferCompLabelForm('lblmodel')
            lbl.set_value(_('model name'))
            lbl.set_location(1, 0)
            dlg.add_component(lbl)
            if journal > 0:
                mod_query = ModelEntry.objects.filter(
                    journal=journal)
            else:
                mod_query = ModelEntry.objects.all(
                )
            sel = XferCompSelect('model')
            sel.set_location(2, 0)
            sel.set_needed(True)
            sel.set_select_query(mod_query)
            dlg.add_component(sel)
            lbl = XferCompLabelForm('lblfactor')
            lbl.set_value(_('factor'))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            fact = XferCompFloat('factor', 0.00, 1000000.0, 2)
            fact.set_value(1.0)
            fact.set_location(2, 1)
            dlg.add_component(fact)
            dlg.add_action(
                self.get_action(_('Ok'), 'images/ok.png'), {'params': {"SAVE": "YES"}})
            dlg.add_action(WrapAction(_('Cancel'), 'images/cancel.png'), {})
        else:
            factor = self.getparam('factor', 1.0)
            for old_key in ['SAVE', 'model', 'factor']:
                if old_key in self.params.keys():
                    del self.params[old_key]
            year = FiscalYear.get_current(self.getparam('year'))
            serial_entry = self.item.get_serial_entry(factor, year)
            date_value = date.today().isoformat()
            entry = EntryAccount.objects.create(
                year=year, date_value=date_value, designation=self.item.designation, journal=self.item.journal)
            entry.editor.before_save(self)
            self.params["entryaccount"] = entry.id
            self.redirect_action(
                EntryAccountEdit.get_action(), {'params': {"serial_entry": serial_entry}})
