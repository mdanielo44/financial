# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.CORE.xferprint import XferPrintAction
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    CLOSE_YES, CLOSE_NO, FORMTYPE_REFRESH, SELECT_MULTI, WrapAction
from lucterios.framework.xfergraphic import XferContainerCustom, \
    XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage
from lucterios.framework.xfercomponents import XferCompEdit, XferCompGrid

from diacamma.payoff.models import DepositSlip, DepositDetail, BankTransaction


@ActionsManage.affect('DepositSlip', 'list')
@MenuManage.describ('payoff.change_depositslip', FORMTYPE_NOMODAL, 'financial', _('manage deposit of cheque'))
class DepositSlipList(XferListEditor):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("deposit slips")


@ActionsManage.affect('DepositSlip', 'modify', 'add')
@MenuManage.describ('payoff.add_depositslip')
class DepositSlipAddModify(XferAddEditor):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption_add = _("Add deposit slip")
    caption_modify = _("Modify deposit slip")


@ActionsManage.affect('DepositSlip', 'show')
@MenuManage.describ('payoff.change_depositslip')
class DepositSlipShow(XferShowEditor):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Show deposit slip")

    def fillresponse(self):
        self.action_list = []
        if self.item.status == 0:
            self.action_list.append(
                ('modify', _("Modify"), "images/edit.png", CLOSE_YES))
            self.action_list.append(
                ('close', _("Closed"), "images/ok.png", CLOSE_YES))
        else:
            self.action_list.append(
                ('print', _("Print"), "images/print.png", CLOSE_NO))
        if self.item.status == 1:
            self.action_list.append(
                ('validate', _("Validate"), "images/ok.png", CLOSE_YES))
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('DepositSlip', 'delete')
@MenuManage.describ('payoff.delete_depositslip')
class DepositSlipDel(XferDelete):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Delete deposit slip")


@ActionsManage.affect('DepositSlip', 'close')
@MenuManage.describ('payoff.add_depositslip')
class DepositSlipClose(XferContainerAcknowledge):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Close deposit slip")

    def fillresponse(self):
        if (self.item.status == 0) and self.confirme(_("Do you want to close this deposit?")):
            self.item.close_deposit()


@ActionsManage.affect('DepositSlip', 'validate')
@MenuManage.describ('payoff.add_depositslip')
class DepositSlipValidate(XferContainerAcknowledge):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Close deposit slip")

    def fillresponse(self):
        if (self.item.status == 1) and self.confirme(_("Do you want to validate this deposit?")):
            self.item.validate_deposit()


@ActionsManage.affect('DepositSlip', 'print')
@MenuManage.describ('payoff.change_depositslip')
class DepositSlipPrint(XferPrintAction):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Print deposit slip")
    action_class = DepositSlipShow


@ActionsManage.affect('DepositDetail', 'add')
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
        edt.set_action(self.request, self.get_action(),
                       {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        self.add_component(edt)
        lbl = XferCompLabelForm('lbl_reference')
        lbl.set_value_as_name(_("reference contains"))
        lbl.set_location(2, 1)
        self.add_component(lbl)
        edt = XferCompEdit('reference')
        edt.set_value(reference)
        edt.set_location(3, 1)
        edt.set_action(self.request, self.get_action(),
                       {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
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

        grid.add_action(self.request, DepositDetailSave.get_action(
            _("select"), "images/ok.png"), {'close': CLOSE_YES, 'unique': SELECT_MULTI})
        self.add_component(grid)

        self.add_action(WrapAction(_('Cancel'), 'images/cancel.png'), {})


@ActionsManage.affect('DepositDetail', 'save')
@MenuManage.describ('payoff.add_depositslip')
class DepositDetailSave(XferContainerAcknowledge):
    icon = "bank.png"
    model = DepositSlip
    field_id = 'depositslip'
    caption = _("Save deposit detail")

    def fillresponse(self, entry=()):
        self.item.add_payoff(entry)


@ActionsManage.affect('DepositDetail', 'delete')
@MenuManage.describ('payoff.add_depositslip')
class DepositDetailDel(XferDelete):
    icon = "bank.png"
    model = DepositDetail
    field_id = 'depositdetail'
    caption = _("Delete deposit detail")


@ActionsManage.affect('BankTransaction', 'list')
@MenuManage.describ('payoff.change_banktransaction', FORMTYPE_NOMODAL, 'financial', _('show bank transactions'))
class BankTransactionList(XferListEditor):
    icon = "transfer.png"
    model = BankTransaction
    field_id = 'banktransaction'
    caption = _("Bank transactions")


@ActionsManage.affect('BankTransaction', 'show')
@MenuManage.describ('payoff.change_banktransaction')
class BankTransactionShow(XferShowEditor):
    icon = "transfer.png"
    model = BankTransaction
    field_id = 'banktransaction'
    caption = _("Show bank transaction")
