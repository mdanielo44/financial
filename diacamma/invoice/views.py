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

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, XferShowEditor, \
    XferSave
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.xfercomponents import XferCompLabelForm, \
    XferCompSelect, XferCompEdit, XferCompHeader, XferCompImage, XferCompGrid,\
    DEFAULT_ACTION_LIST
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    FORMTYPE_MODAL, CLOSE_YES, SELECT_SINGLE, FORMTYPE_REFRESH, CLOSE_NO,\
    SELECT_MULTI, WrapAction

from diacamma.invoice.models import Article, Bill, Detail
from diacamma.accounting.models import Third, FiscalYear
from django.utils import six, formats
from lucterios.framework.xfergraphic import XferContainerAcknowledge,\
    XferContainerCustom
from lucterios.CORE.parameters import Params
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor
from datetime import date
from lucterios.CORE.xferprint import XferPrintAction, XferPrintReporting
from copy import deepcopy
from lucterios.framework.error import LucteriosException, IMPORTANT
from diacamma.payoff.views import PayoffAddModify

MenuManage.add_sub("invoice", "financial", "diacamma.invoice/images/invoice.png",
                   _("invoice"), _("Manage of billing"), 20)


@ActionsManage.affect('Bill', 'list')
@MenuManage.describ('invoice.change_bill', FORMTYPE_NOMODAL, 'invoice', _('Management of bill list'))
class BillList(XferListEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Bill")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', -1)
        self.fieldnames = Bill.get_default_fields(status_filter)
        lbl = XferCompLabelForm('lbl_filter')
        lbl.set_value_as_name(_('Filter by type'))
        lbl.set_location(0, 3)
        self.add_component(lbl)
        dep_field = self.item.get_field_by_name('status')
        sel_list = list(dep_field.choices)
        sel_list.insert(0, (-1, _('building+valid')))
        edt = XferCompSelect("status_filter")
        edt.set_select(sel_list)
        edt.set_value(status_filter)
        edt.set_location(1, 3)
        edt.set_action(self.request, self.get_action(),
                       {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        self.add_component(edt)
        lbl = XferCompLabelForm('lbl_fiscalyear')
        lbl.set_value_as_header(six.text_type(FiscalYear.get_current()))
        lbl.set_location(2, 3)
        self.add_component(lbl)

        self.filter = Q()
        if status_filter >= 0:
            self.filter = Q(status=status_filter)
        elif status_filter == -1:
            self.filter = Q(status=0) | Q(status=1)
        if status_filter >= 1:
            self.action_grid = [
                ('show', _("Edit"), "images/show.png", SELECT_SINGLE)]
        else:
            self.action_grid = deepcopy(DEFAULT_ACTION_LIST)
        if status_filter == 1:
            self.action_grid.append(
                ('archive', _("Archive"), "images/ok.png", SELECT_MULTI))
            self.action_grid.append(
                ('multipay', _('payoff'), '', SELECT_MULTI))
        if status_filter != 2:
            self.action_grid.append(
                ('printbill', _("Print"), "images/print.png", SELECT_MULTI))

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.colspan = 3
        if Params.getvalue("invoice-vat-mode") == 1:
            grid.headers[5] = XferCompHeader(grid.headers[5].name, _(
                'total excl. taxes'), grid.headers[5].type, grid.headers[5].orderable)
        elif Params.getvalue("invoice-vat-mode") == 2:
            grid.headers[5] = XferCompHeader(grid.headers[5].name, _(
                'total incl. taxes'), grid.headers[5].type, grid.headers[5].orderable)


@ActionsManage.affect('Bill', 'search')
@MenuManage.describ('invoice.change_bill', FORMTYPE_NOMODAL, 'invoice', _('To find a bill following a set of criteria.'))
class BillSearch(XferSavedCriteriaSearchEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Search bill")


@ActionsManage.affect('Bill', 'modify', 'add')
@MenuManage.describ('invoice.add_bill')
class BillAddModify(XferAddEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption_add = _("Add bill")
    caption_modify = _("Modify bill")


@ActionsManage.affect('Bill', 'show')
@MenuManage.describ('contacts.change_bill')
class BillShow(XferShowEditor):
    caption = _("Show bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        if (self.item.status == 0) and (self.item.get_info_state() == ''):
            self.action_list.insert(
                0, ('valid', _("Valid"), "images/ok.png", CLOSE_NO))
        elif self.item.status != 0:
            self.action_list = []
        if self.item.status == 1:
            self.action_list.insert(
                0, ('archive', _("Archive"), "images/ok.png", CLOSE_NO))
            if self.item.bill_type == 0:
                self.action_list.insert(
                    0, ('convertbill', _("=> Bill"), "images/ok.png", CLOSE_YES))
            if self.item.bill_type in (1, 3):
                self.action_list.insert(
                    1, ('cancel', _("Cancel"), "images/cancel.png", CLOSE_NO))
        if self.item.status in (1, 3):
            self.action_list.insert(0,
                                    ('printbill', _("Print"), "images/print.png", CLOSE_NO))
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('Bill', 'valid')
@MenuManage.describ('contacts.change_bill')
class BillValid(XferContainerAcknowledge):
    caption = _("Valid bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        if (self.item.status == 0) and self.confirme(_("Do you want validate '%s'?") % self.item):
            self.item.valid()


@ActionsManage.affect('Bill', 'multipay')
@MenuManage.describ('payoff.add_payoff')
class BillMultiPay(XferContainerAcknowledge):
    caption = _("Multi-pay bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self, bill):
        self.redirect_action(
            PayoffAddModify.get_action("", ""), {'params': {"supportings": bill}})


@ActionsManage.affect('Bill', 'convertbill')
@MenuManage.describ('contacts.change_bill')
class BillFromQuotation(XferContainerAcknowledge):
    caption = _("Convert to bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        if (self.item.bill_type == 0) and (self.item.status == 1) and self.confirme(_("Do you want convert '%s' to bill?") % self.item):
            new_id = self.item.convert_to_bill()
            self.redirect_action(ActionsManage.get_act_changed(
                self.model.__name__, 'show', '', ''), {'params': {self.field_id: new_id}})


@ActionsManage.affect('Bill', 'cancel')
@MenuManage.describ('contacts.change_bill')
class BillCancel(XferContainerAcknowledge):
    caption = _("Valid bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        if (self.item.status == 1) and (self.item.bill_type in (1, 3)) and self.confirme(_("Do you want cancel '%s'?") % self.item):
            asset_id = self.item.cancel()
            if asset_id is not None:
                self.redirect_action(ActionsManage.get_act_changed(
                    'Bill', 'show', '', ''), {'params': {self.field_id: asset_id}})


@ActionsManage.affect('Bill', 'archive')
@MenuManage.describ('contacts.change_bill')
class BillArchive(XferContainerAcknowledge):
    caption = _("Valid bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        if self.confirme(_("Do you want archive this %d items?") % len(self.items)):
            for item in self.items:
                item.archive()


@ActionsManage.affect('Bill', 'delete')
@MenuManage.describ('invoice.delete_bill')
class BillDel(XferDelete):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Delete bill")


@ActionsManage.affect('Bill', 'third')
@MenuManage.describ('invoice.change_bill')
class BillThird(XferListEditor):
    icon = "diacamma.accounting/images/thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Select third to bill")

    def __init__(self, **kwargs):
        XferListEditor.__init__(self, **kwargs)
        self.action_list = []

    def fillresponse_header(self):
        contact_filter = self.getparam('filter', '')
        lbl = XferCompLabelForm('lbl_filtre')
        lbl.set_value_as_name(_('Filtrer by contact'))
        lbl.set_location(0, 2)
        self.add_component(lbl)
        comp = XferCompEdit('filter')
        comp.set_value(contact_filter)
        comp.set_action(self.request, self.get_action(),
                        {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        comp.set_location(1, 2)
        self.add_component(comp)
        self.filter = Q(status=0)
        if contact_filter != "":
            q_legalentity = Q(
                contact__legalentity__name__contains=contact_filter)
            q_individual = (Q(contact__individual__firstname__contains=contact_filter) | Q(
                contact__individual__lastname__contains=contact_filter))
            self.filter &= (q_legalentity | q_individual)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.add_action(self.request, BillThirdValid.get_action(
            _('select'), 'images/ok.png'), {'modal': FORMTYPE_MODAL, 'close': CLOSE_YES, 'unique': SELECT_SINGLE}, 0)


@MenuManage.describ('invoice.change_bill')
class BillThirdValid(XferSave):
    redirect_to_show = False
    icon = "diacamma.accounting/images/thirds.png"
    model = Bill
    field_id = 'bill'
    caption = _("Select third to bill")


@ActionsManage.affect('Bill', 'printbill')
@MenuManage.describ('invoice.add_bill')
class BillPrint(XferPrintReporting):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Print bill")

    def items_callback(self):
        has_item = False
        for item in self.items:
            if item.status > 0:
                has_item = True
                yield item
        if not has_item:
            raise LucteriosException(IMPORTANT, _("No invoice to print!"))


@ActionsManage.affect('Detail', 'edit', 'add')
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
        self.get_components('article').set_select_query(
            Article.objects.filter(isdisabled=False))


@ActionsManage.affect('Detail', 'delete')
@MenuManage.describ('invoice.add_bill')
class DetailDel(XferDelete):
    icon = "article.png"
    model = Detail
    field_id = 'detail'
    caption = _("Delete detail")


@ActionsManage.affect('Article', 'list')
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
        edt.set_action(self.request, self.get_action(),
                       {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        self.add_component(edt)
        self.filter = Q()
        if show_filter == 0:
            self.filter = Q(isdisabled=False)


@ActionsManage.affect('Article', 'edit', 'add')
@MenuManage.describ('invoice.add_article')
class ArticleAddModify(XferAddEditor):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption_add = _("Add article")
    caption_modify = _("Modify article")


@ActionsManage.affect('Article', 'delete')
@MenuManage.describ('invoice.delete_article')
class ArticleDel(XferDelete):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Delete article")


@ActionsManage.affect('Article', 'statistic')
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
        lbl.set_value_as_headername(
            _('Statistics in date of %s') % formats.date_format(date.today(), "DATE_FORMAT"))
        lbl.set_location(1, 0, 2)
        self.add_component(lbl)
        self.item.fiscal_year = FiscalYear.get_current(select_year)
        self.fill_from_model(1, 1, False, ['fiscal_year'])
        self.get_components('fiscal_year').set_action(
            self.request, self.get_action(), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})

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
        self.add_action(BillStatisticPrint.get_action(
            _("Print"), "images/print.png"), {'close': CLOSE_NO, 'params': {'classname': self.__class__.__name__}})
        self.add_action(WrapAction(_('Close'), 'images/close.png'), {})


@MenuManage.describ('invoice.change_bill')
class BillStatisticPrint(XferPrintAction):
    caption = _("Print statistic")
    icon = "report.png"
    model = Bill
    field_id = 'bill'
    action_class = BillStatistic
    with_text_export = True
