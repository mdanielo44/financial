# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, TITLE_DELETE, TITLE_ADD, TITLE_MODIFY, TITLE_EDIT, TITLE_PRINT,\
    TITLE_CANCEL, XferTransition
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.xfergraphic import XferContainerCustom, XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage, XferCompSelect
from lucterios.framework.xfercomponents import XferCompEdit, XferCompGrid
from lucterios.framework.tools import FORMTYPE_NOMODAL, CLOSE_YES, CLOSE_NO, FORMTYPE_REFRESH, SELECT_MULTI, SELECT_SINGLE
from lucterios.framework.tools import ActionsManage, MenuManage, WrapAction
from lucterios.CORE.xferprint import XferPrintAction

from diacamma.payoff.models import DepositSlip, DepositDetail, BankTransaction
from diacamma.accounting.models import FiscalYear


@MenuManage.describ('payoff.change_depositslip', FORMTYPE_NOMODAL, 'financial', _('manage deposit of cheque'))
class DepositSlipList(XferListEditor):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("deposit slips")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', -1)
        year_filter = self.getparam('year_filter', FiscalYear.get_current().id)
        lbl = XferCompLabelForm('lbl_statusfilter')
        lbl.set_value_as_name(_('Filter by status'))
        lbl.set_location(0, 1)
        self.add_component(lbl)
        dep_field = DepositSlip.get_field_by_name('status')
        sel_list = list(dep_field.choices)
        sel_list.insert(0, (-1, '---'))
        edt = XferCompSelect("status_filter")
        edt.set_select(sel_list)
        edt.set_value(status_filter)
        edt.set_needed(False)
        edt.set_location(1, 1)
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        lbl = XferCompLabelForm('lbl_yearfilter')
        lbl.set_value_as_name(_('Filter by year'))
        lbl.set_location(0, 2)
        self.add_component(lbl)
        edt = XferCompSelect("year_filter")
        edt.set_needed(False)
        edt.set_select_query(FiscalYear.objects.all())
        edt.set_value(year_filter)
        edt.set_location(1, 2)
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        self.filter = Q()
        if status_filter >= 0:
            self.filter &= Q(status=status_filter)
        if year_filter > 0:
            year = FiscalYear.objects.get(id=year_filter)
            self.filter &= Q(date__gte=year.begin)
            self.filter &= Q(date__lte=year.end)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", condition=lambda xfer: xfer.item.status == 0, close=CLOSE_YES)
@MenuManage.describ('payoff.add_depositslip')
class DepositSlipAddModify(XferAddEditor):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption_add = _("Add deposit slip")
    caption_modify = _("Modify deposit slip")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('payoff.change_depositslip')
class DepositSlipShow(XferShowEditor):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Show deposit slip")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('payoff.delete_depositslip')
class DepositSlipDel(XferDelete):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Delete deposit slip")


@ActionsManage.affect_transition("status")
@MenuManage.describ('payoff.add_depositslip')
class DepositSlipTransition(XferTransition):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'


@ActionsManage.affect_show(TITLE_PRINT, "images/print.png", condition=lambda xfer: xfer.item.status != 0)
@MenuManage.describ('payoff.change_depositslip')
class DepositSlipPrint(XferPrintAction):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Print deposit slip")
    action_class = DepositSlipShow


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.item.status == 0)
@MenuManage.describ('payoff.add_depositslip')
class DepositDetailAddModify(XferContainerCustom):
    icon = "bank.png"
    model = DepositDetail
    field_id = 'depositdetail'
    caption = _("Add deposit detail")

    def fill_header(self, payer, reference):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(_("select cheque to deposit"))
        lbl.set_location(1, 0, 3)
        self.add_component(lbl)
        lbl = XferCompLabelForm('lbl_payer')
        lbl.set_value_as_name(_("payer contains"))
        lbl.set_location(0, 1)
        self.add_component(lbl)
        edt = XferCompEdit('payer')
        edt.set_value(payer)
        edt.set_location(1, 1)
        edt.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(edt)
        lbl = XferCompLabelForm('lbl_reference')
        lbl.set_value_as_name(_("reference contains"))
        lbl.set_location(2, 1)
        self.add_component(lbl)
        edt = XferCompEdit('reference')
        edt.set_value(reference)
        edt.set_location(3, 1)
        edt.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(edt)

    def fillresponse(self, payer="", reference=""):
        self.fill_header(payer, reference)

        grid = XferCompGrid('entry')
        grid.define_page(self)
        grid.add_header('bill', _('bill'))
        grid.add_header('payer', _('payer'), horderable=1)
        grid.add_header('amount', _('amount'), horderable=1)
        grid.add_header('date', _('date'), horderable=1)
        grid.add_header('reference', _('reference'), horderable=1)
        payoff_nodeposit = DepositDetail.get_payoff_not_deposit(
            payer, reference, grid.order_list)
        for payoff in payoff_nodeposit:
            payoffid = payoff['id']
            grid.set_value(payoffid, 'bill', payoff['bill'])
            grid.set_value(payoffid, 'payer', payoff['payer'])
            grid.set_value(payoffid, 'amount', payoff['amount'])
            grid.set_value(payoffid, 'date', payoff['date'])
            grid.set_value(payoffid, 'reference', payoff['reference'])
        grid.set_location(0, 2, 4)

        grid.add_action(self.request, DepositDetailSave.get_action(_("select"), "images/ok.png"), close=CLOSE_YES, unique=SELECT_MULTI)
        self.add_component(grid)

        self.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))


@MenuManage.describ('payoff.add_depositslip')
class DepositDetailSave(XferContainerAcknowledge):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Save deposit detail")

    def fillresponse(self, entry=()):
        self.item.add_payoff(entry)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.item.status == 0)
@MenuManage.describ('payoff.add_depositslip')
class DepositDetailDel(XferDelete):
    icon = "bank.png"
    model = DepositDetail
    field_id = 'depositdetail'
    caption = _("Delete deposit detail")


@MenuManage.describ('payoff.change_banktransaction', FORMTYPE_NOMODAL, 'financial', _('show bank transactions'))
class BankTransactionList(XferListEditor):
    icon = "transfer.png"
    model = BankTransaction
    field_id = 'banktransaction'
    caption = _("Bank transactions")


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('payoff.change_banktransaction')
class BankTransactionShow(XferShowEditor):
    icon = "transfer.png"
    model = BankTransaction
    field_id = 'banktransaction'
    caption = _("Show bank transaction")
