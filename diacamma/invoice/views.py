# -*- coding: utf-8 -*-
'''
diacamma.invoice view package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
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
from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.utils import formats, six
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, XferShowEditor, TITLE_PRINT, TITLE_CLOSE, TITLE_DELETE, TITLE_MODIFY, TITLE_ADD, TITLE_CANCEL, TITLE_OK, TITLE_EDIT,\
    XferTransition
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect, XferCompHeader, XferCompImage, XferCompGrid, XferCompCheck
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, FORMTYPE_MODAL, CLOSE_YES, SELECT_SINGLE, FORMTYPE_REFRESH, CLOSE_NO, SELECT_MULTI, WrapAction
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock

from lucterios.CORE.xferprint import XferPrintAction, XferPrintReporting
from lucterios.CORE.parameters import Params
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor

from lucterios.contacts.models import Individual, LegalEntity

from diacamma.invoice.models import Article, Bill, Detail
from diacamma.accounting.models import FiscalYear, Third
from diacamma.payoff.views import PayoffAddModify
from diacamma.payoff.models import Payoff

MenuManage.add_sub("invoice", "financial", "diacamma.invoice/images/invoice.png", _("invoice"), _("Manage of billing"), 20)


def _add_bill_filter(xfer, row):
    status_filter = xfer.getparam('status_filter', -1)
    lbl = XferCompLabelForm('lbl_filter')
    lbl.set_value_as_name(_('Filter by type'))
    lbl.set_location(0, row)
    xfer.add_component(lbl)
    dep_field = Bill.get_field_by_name('status')
    sel_list = list(dep_field.choices)
    sel_list.insert(0, (-1, _('building+valid')))
    edt = XferCompSelect("status_filter")
    edt.set_select(sel_list)
    edt.set_value(status_filter)
    edt.set_location(1, row)
    edt.set_action(xfer.request, xfer.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
    xfer.add_component(edt)
    current_filter = Q()
    if status_filter >= 0:
        current_filter &= Q(status=status_filter)
    elif status_filter == -1:
        current_filter &= Q(status=0) | Q(status=1)
    return current_filter, status_filter


@MenuManage.describ('invoice.change_bill', FORMTYPE_NOMODAL, 'invoice', _('Management of bill list'))
class BillList(XferListEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Bill")

    def fillresponse_header(self):
        self.filter, status_filter = _add_bill_filter(self, 3)
        self.fieldnames = Bill.get_default_fields(status_filter)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.colspan = 3
        if Params.getvalue("invoice-vat-mode") == 1:
            grid.headers[5] = XferCompHeader(grid.headers[5].name, _('total excl. taxes'),
                                             grid.headers[5].type, grid.headers[5].orderable)
        elif Params.getvalue("invoice-vat-mode") == 2:
            grid.headers[5] = XferCompHeader(grid.headers[5].name, _('total incl. taxes'),
                                             grid.headers[5].type, grid.headers[5].orderable)


@MenuManage.describ('invoice.change_bill', FORMTYPE_NOMODAL, 'invoice', _('To find a bill following a set of criteria.'))
class BillSearch(XferSavedCriteriaSearchEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Search bill")


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) < 1)
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.status == 0)
@MenuManage.describ('invoice.add_bill')
class BillAddModify(XferAddEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption_add = _("Add bill")
    caption_modify = _("Modify bill")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.change_bill')
class BillShow(XferShowEditor):
    caption = _("Show bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        XferShowEditor.fillresponse(self)
        self.add_action(ActionsManage.get_action_url('payoff.Supporting', 'Show', self), close=CLOSE_NO, params={'item_name': self.field_id}, pos_act=0)
        if self.item.status in (1, 3):
            self.add_action(ActionsManage.get_action_url('payoff.Supporting', 'Email', self), close=CLOSE_NO, params={'item_name': self.field_id}, pos_act=0)


@ActionsManage.affect_transition("status")
@MenuManage.describ('invoice.add_bill')
class BillTransition(XferTransition):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fill_dlg_payoff(self, withpayoff):
        dlg = self.create_custom(Payoff)
        dlg.caption = _("Valid bill")
        icon = XferCompImage('img')
        icon.set_location(0, 0, 1, 6)
        icon.set_value(self.icon_path())
        dlg.add_component(icon)
        lbl = XferCompLabelForm('lb_title')
        lbl.set_value_as_infocenter(_("Do you want validate '%s'?") % self.item)
        lbl.set_location(1, 1, 4)
        dlg.add_component(lbl)
        check_payoff = XferCompCheck('withpayoff')
        check_payoff.set_value(withpayoff)
        check_payoff.set_location(1, 2)
        check_payoff.java_script = """
    var type=current.getValue();
    parent.get('date_payoff').setEnabled(type);
    parent.get('amount').setEnabled(type);
    parent.get('payer').setEnabled(type);
    parent.get('mode').setEnabled(type);
    parent.get('reference').setEnabled(type);
    if (parent.get('bank_account')) {
        parent.get('bank_account').setEnabled(type);
    }
    """
        dlg.add_component(check_payoff)
        lbl = XferCompLabelForm('lb_withpayoff')
        lbl.set_value_as_name(_("Payment of deposit or cash"))
        lbl.set_location(2, 2)
        dlg.add_component(lbl)
        dlg.item.supporting = self.item
        dlg.fill_from_model(2, 3, False)
        if dlg.get_components("bank_fee") is not None:
            check_payoff.java_script += "parent.get('bank_fee').setEnabled(type);\n"
        dlg.get_components("date").name = "date_payoff"
        dlg.get_components("mode").set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), params={"CONFIRME": "YES"})
        dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))

    def fill_confirm(self, transition, trans):
        withpayoff = self.getparam('withpayoff', True)
        if (transition != 'valid') or (self.item.bill_type == 0):
            XferTransition.fill_confirm(self, transition, trans)
            if transition == 'cancel':
                if self.trans_result is not None:
                    self.redirect_action(ActionsManage.get_action_url('invoice.Bill', 'Show', self), params={self.field_id: self.trans_result})
        elif self.getparam("CONFIRME") is None:
            self.fill_dlg_payoff(withpayoff)
        else:
            XferTransition.fill_confirm(self, transition, trans)
            if (self.item.bill_type != 0) and withpayoff:
                Payoff.multi_save((self.item.id,), self.getparam('amount', 0.0), self.getparam('mode', 0), self.getparam('payer'),
                                  self.getparam('reference'), self.getparam('bank_account', 0), self.getparam('date_payoff'))


@ActionsManage.affect_grid(_('payoff'), '', close=CLOSE_NO, unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) == 1)
@MenuManage.describ('payoff.add_payoff')
class BillMultiPay(XferContainerAcknowledge):
    caption = _("Multi-pay bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self, bill):
        self.redirect_action(
            PayoffAddModify.get_action("", ""), params={"supportings": bill})


@ActionsManage.affect_show(_("=> Bill"), "images/ok.png", close=CLOSE_YES, condition=lambda xfer: (xfer.item.status == 1) and (xfer.item.bill_type == 0))
@MenuManage.describ('invoice.change_bill')
class BillFromQuotation(XferContainerAcknowledge):
    caption = _("Convert to bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        if (self.item.bill_type == 0) and (self.item.status == 1) and self.confirme(_("Do you want convert '%s' to bill?") % self.item):
            new_bill = self.item.convert_to_bill()
            if new_bill is not None:
                self.redirect_action(ActionsManage.get_action_url('invoice.Bill', 'Show', self), params={self.field_id: new_bill.id})


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) < 1)
@MenuManage.describ('invoice.delete_bill')
class BillDel(XferDelete):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Delete bill")


@ActionsManage.affect_grid(_("Print"), "images/print.png", close=CLOSE_NO, unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) in (1, 3))
@ActionsManage.affect_show(_("Print"), "images/print.png", close=CLOSE_NO, condition=lambda xfer: xfer.item.status in (1, 3))
@MenuManage.describ('invoice.change_bill')
class BillPrint(XferPrintReporting):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Print bill")

    def get_print_name(self):
        if len(self.items) == 1:
            current_bill = self.items[0]
            return current_bill.get_document_filename()
        else:
            return six.text_type(self.caption)

    def items_callback(self):
        has_item = False
        for item in self.items:
            if item.status > 0:
                has_item = True
                yield item
        if not has_item:
            raise LucteriosException(IMPORTANT, _("No invoice to print!"))


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_bill')
class DetailAddModify(XferAddEditor):
    icon = "article.png"
    model = Detail
    field_id = 'detail'
    caption_add = _("Add detail")
    caption_modify = _("Modify detail")

    def fillresponse(self):
        if self.getparam('CHANGE_ART') is not None:
            if self.item.article is not None:
                self.item.designation = self.item.article.designation
                self.item.price = self.item.article.price
                self.item.unit = self.item.article.unit
        XferAddEditor.fillresponse(self)
        self.get_components('article').set_select_query(Article.objects.filter(isdisabled=False))


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.add_bill')
class DetailDel(XferDelete):
    icon = "article.png"
    model = Detail
    field_id = 'detail'
    caption = _("Delete detail")


@MenuManage.describ('invoice.change_article', FORMTYPE_NOMODAL, 'invoice', _('Management of article list'))
class ArticleList(XferListEditor):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Articles")

    def fillresponse_header(self):
        show_filter = self.getparam('show_filter', 0)
        lbl = XferCompLabelForm('lbl_showing')
        lbl.set_value_as_name(_('Show articles'))
        lbl.set_location(0, 3)
        self.add_component(lbl)
        edt = XferCompSelect("show_filter")
        edt.set_select([(0, _('Only activate')), (1, _('All'))])
        edt.set_value(show_filter)
        edt.set_location(1, 3)
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)
        self.filter = Q()
        if show_filter == 0:
            self.filter = Q(isdisabled=False)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_article')
class ArticleAddModify(XferAddEditor):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption_add = _("Add article")
    caption_modify = _("Modify article")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_article')
class ArticleDel(XferDelete):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Delete article")


@MenuManage.describ('invoice.change_bill', FORMTYPE_MODAL, 'invoice', _('Statistic of selling'))
class BillStatistic(XferContainerCustom):
    icon = "report.png"
    model = Bill
    field_id = 'bill'
    caption = _("Statistic")

    def fill_header(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 2)
        self.add_component(img)
        select_year = self.getparam('fiscal_year')
        lbl = XferCompLabelForm('lbl_title')
        lbl.set_value_as_headername(_('Statistics in date of %s') % formats.date_format(date.today(), "DATE_FORMAT"))
        lbl.set_location(1, 0, 2)
        self.add_component(lbl)
        self.item.fiscal_year = FiscalYear.get_current(select_year)
        self.fill_from_model(1, 1, False, ['fiscal_year'])
        fiscal_year = self.get_components('fiscal_year')
        fiscal_year.set_needed(True)
        fiscal_year.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)

    def fill_customers(self):
        costumer_result = self.item.get_statistics_customer()
        grid = XferCompGrid("customers")
        grid.add_header("customer", _("customer"))
        grid.add_header("amount", _("amount"))
        grid.add_header("ratio", _("ratio (%)"))
        index = 0
        for cust_val in costumer_result:
            grid.set_value(index, "customer", cust_val[0])
            grid.set_value(index, "amount", cust_val[1])
            grid.set_value(index, "ratio", cust_val[2])
            index += 1
        grid.set_location(0, 1, 3)
        grid.set_size(400, 800)
        self.add_component(grid)

    def fill_articles(self):
        articles_result = self.item.get_statistics_article()
        grid = XferCompGrid("articles")
        grid.add_header("article", _("article"))
        grid.add_header("amount", _("amount"))
        grid.add_header("number", _("number"))
        grid.add_header("mean", _("mean"))
        grid.add_header("ratio", _("ratio (%)"))
        index = 0
        for art_val in articles_result:
            grid.set_value(index, "article", art_val[0])
            grid.set_value(index, "amount", art_val[1])
            grid.set_value(index, "number", art_val[2])
            grid.set_value(index, "mean", art_val[3])
            grid.set_value(index, "ratio", art_val[4])
            index += 1
        grid.set_location(0, 1, 3)
        grid.set_size(400, 800)
        self.add_component(grid)

    def fillresponse(self):
        self.fill_header()
        self.new_tab(_('Customers'))
        self.fill_customers()
        self.new_tab(_('Articles'))
        self.fill_articles()
        self.add_action(BillStatisticPrint.get_action(TITLE_PRINT, "images/print.png"), close=CLOSE_NO, params={'classname': self.__class__.__name__})
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('invoice.change_bill')
class BillStatisticPrint(XferPrintAction):
    caption = _("Print statistic")
    icon = "report.png"
    model = Bill
    field_id = 'bill'
    action_class = BillStatistic
    with_text_export = True


@signal_and_lock.Signal.decorate('show_contact')
def show_contact_invoice(contact, xfer):
    if WrapAction.is_permission(xfer.request, 'invoice.change_bill'):
        third = Third.objects.filter(contact_id=contact.id)
        if len(third) == 1:
            third = third[0]
            xfer.new_tab(_("Financial"))
            nb_build = len(Bill.objects.filter(third=third, status=0))
            nb_valid = len(Bill.objects.filter(third=third, status=1))
            lab = XferCompLabelForm('invoiceinfo')
            lab.set_value_as_header(_("There are %(build)d bills in building and %(valid)d validated") % {'build': nb_build, 'valid': nb_valid})
            lab.set_location(0, 5, 2)
            xfer.add_component(lab)


@signal_and_lock.Signal.decorate('summary')
def summary_invoice(xfer):
    is_right = WrapAction.is_permission(xfer.request, 'invoice.change_bill')
    contacts = []
    if not xfer.request.user.is_anonymous():
        for contact in Individual.objects.filter(user=xfer.request.user):
            contacts.append(contact.id)
        for contact in LegalEntity.objects.filter(responsability__individual__user=xfer.request.user):
            contacts.append(contact.id)
    if is_right or (len(contacts) > 0):
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('invoicetitle')
        lab.set_value_as_infocenter(_("Invoice"))
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
    if len(contacts) > 0:
        nb_build = len(Bill.objects.filter(third__contact_id__in=contacts))
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('invoicecurrent')
        lab.set_value_as_header(_("You are %d bills") % nb_build)
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
    if is_right:
        row = xfer.get_max_row() + 1
        nb_build = len(Bill.objects.filter(status=0))
        nb_valid = len(Bill.objects.filter(status=1))
        lab = XferCompLabelForm('invoiceinfo')
        lab.set_value_as_header(_("There are %(build)d bills in building and %(valid)d validated") % {'build': nb_build, 'valid': nb_valid})
        lab.set_location(0, row + 1, 4)
        xfer.add_component(lab)
    if is_right or (len(contacts) > 0):
        lab = XferCompLabelForm('invoicesep')
        lab.set_value_as_infocenter("{[hr/]}")
        lab.set_location(0, row + 2, 4)
        xfer.add_component(lab)
        return True
    else:
        return False


@signal_and_lock.Signal.decorate('third_addon')
def thirdaddon_invoice(item, xfer):
    if WrapAction.is_permission(xfer.request, 'invoice.change_bill'):
        try:
            FiscalYear.get_current()
            xfer.new_tab(_('Invoice'))
            current_filter, status_filter = _add_bill_filter(xfer, 1)
            current_filter &= Q(third=item)
            bills = Bill.objects.filter(current_filter)
            bill_grid = XferCompGrid('bill')
            bill_grid.set_model(bills, Bill.get_default_fields(status_filter), xfer)
            bill_grid.set_location(0, 2, 2)
            bill_grid.add_action(xfer.request, ActionsManage.get_action_url('invoice.Bill', 'Show', xfer), modal=FORMTYPE_MODAL, unique=SELECT_SINGLE, close=CLOSE_NO)
            xfer.add_component(bill_grid)
        except LucteriosException:
            pass
