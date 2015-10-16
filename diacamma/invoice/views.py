# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, XferShowEditor, \
    XferSave
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.xfercomponents import XferCompLabelForm, \
    XferCompSelect, XferCompEdit, XferCompHeader
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, \
    FORMTYPE_MODAL, CLOSE_YES, SELECT_SINGLE, FORMTYPE_REFRESH, CLOSE_NO,\
    SELECT_MULTI

from diacamma.invoice.models import Article, Bill, Detail
from diacamma.accounting.models import Third, FiscalYear
from django.utils import six
from lucterios.framework.xfergraphic import XferContainerAcknowledge,\
    XferContainerCustom
from lucterios.CORE.parameters import Params
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor

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
        if status_filter == 1:
            self.action_grid.append(
                ('archive', _("Archive"), "images/ok.png", SELECT_MULTI))

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
            if self.item.bill_type in (1, 3):
                self.action_list.insert(
                    1, ('cancel', _("Cancel"), "images/cancel.png", CLOSE_NO))
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
@MenuManage.describ('invoice.change_bill', FORMTYPE_NOMODAL, 'invoice', _('Statistic of selling'))
class BillStatistic(XferContainerCustom):
    icon = "report.png"
    model = Bill
    field_id = 'bill'
    caption = _("Statistic")
