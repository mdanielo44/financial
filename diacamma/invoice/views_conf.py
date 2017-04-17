# -*- coding: utf-8 -*-
'''
diacamma.invoice views_conf package

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

from lucterios.framework.xferadvance import XferListEditor, TITLE_MODIFY, TITLE_DELETE, TITLE_ADD
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, CLOSE_NO, SELECT_MULTI, SELECT_SINGLE,\
    FORMTYPE_MODAL
from lucterios.framework.xfercomponents import XferCompButton
from lucterios.framework import signal_and_lock
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit, ObjectImport
from lucterios.CORE.models import Parameter

from diacamma.accounting.tools import correct_accounting_code
from diacamma.invoice.models import Vat, Article, Category
from diacamma.accounting.system import accounting_system_ident


def fill_params(xfer, param_lists=None, is_mini=False):
    if param_lists is None:
        param_lists = ['invoice-vat-mode', 'invoice-default-sell-account',
                       'invoice-vatsell-account', 'invoice-reduce-account', 'invoice-account-third']
    Params.fill(xfer, param_lists, 1, xfer.get_max_row() + 1)
    btn = XferCompButton('editparam')
    btn.set_is_mini(is_mini)
    btn.set_location(1, xfer.get_max_row() + 1, 2, 1)
    btn.set_action(xfer.request, ParamEdit.get_action(TITLE_MODIFY, 'images/edit.png'), close=CLOSE_NO, params={'params': param_lists})
    xfer.add_component(btn)


@MenuManage.describ('invoice.change_vat', FORMTYPE_NOMODAL, 'financial.conf', _('Management of parameters and configuration of invoice'))
class InvoiceConf(XferListEditor):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption = _("Invoice configuration")

    def fillresponse_header(self):
        self.new_tab(_('Parameters'))
        fill_params(self)
        self.new_tab(_('Categories'))
        self.fill_grid(self.get_max_row(), Category, 'category', Category.objects.all())
        self.new_tab(_('VAT'))


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class VatAddModify(XferAddEditor):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption_add = _("Add VAT")
    caption_modify = _("Modify VAT")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class VatDel(XferDelete):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption = _("Delete VAT")


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_vat')
class CategoryAddModify(XferAddEditor):
    icon = "invoice_conf.png"
    model = Category
    field_id = 'category'
    caption_add = _("Add category")
    caption_modify = _("Modify category")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_vat')
class CategoryDel(XferDelete):
    icon = "invoice_conf.png"
    model = Category
    field_id = 'category'
    caption = _("Delete Category")


@MenuManage.describ('contacts.add_article', FORMTYPE_MODAL, 'financial.conf', _('Tool to import articles from CSV file.'))
class ArticleImport(ObjectImport):
    caption = _("Article import")
    icon = "invoice_conf.png"

    def get_select_models(self):
        return Article.get_select_contact_type(True)


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_invoice(known_codes, accompt_returned):
    article_unknown = Article.objects.filter(
        isdisabled=False).exclude(sell_account__in=known_codes).values_list('sell_account', flat=True).distinct()
    param_unknown = Parameter.objects.filter(name__in=('invoice-default-sell-account', 'invoice-vatsell-account',
                                                       'invoice-reduce-account')).exclude(value__in=known_codes).values_list('value', flat=True).distinct()
    comptenofound = ""
    if (len(article_unknown) > 0):
        comptenofound = _("articles") + ":" + ",".join(article_unknown) + " "
    if (len(param_unknown) > 0):
        comptenofound += _("parameters") + ":" + ",".join(param_unknown)
    if comptenofound != "":
        accompt_returned.append(
            "- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Invoice'), comptenofound))
    return True


@signal_and_lock.Signal.decorate('param_change')
def paramchange_invoice(params):
    invoice_params = ['invoice-default-sell-account', 'invoice-vatsell-account',
                      'invoice-reduce-account', 'invoice-account-third']
    if 'accounting-sizecode' in params:
        for param_item in invoice_params:
            Parameter.change_value(param_item, correct_accounting_code(Params.getvalue(param_item)))
        Params.clear()
        for art in Article.objects.all():
            if art.sell_account != correct_accounting_code(art.sell_account):
                art.sell_account = correct_accounting_code(art.sell_account)
                art.save()
    for invoice_param in invoice_params:
        if invoice_param in params:
            code_value = Params.getvalue(invoice_param)
            if code_value != "":
                Parameter.change_value(invoice_param, correct_accounting_code(code_value))
    if 'accounting-system' in params:
        system_ident = accounting_system_ident(Params.getvalue("accounting-system"))
        if system_ident == "french":
            Parameter.change_value('invoice-default-sell-account', correct_accounting_code('706'))
            Parameter.change_value('invoice-reduce-account', correct_accounting_code('709'))
            Parameter.change_value('invoice-vatsell-account', correct_accounting_code('4455'))
            Parameter.change_value("invoice-account-third", correct_accounting_code('411'))
        elif system_ident == "belgium":
            Parameter.change_value('invoice-default-sell-account', correct_accounting_code('700'))
            Parameter.change_value('invoice-reduce-account', correct_accounting_code('708'))
            Parameter.change_value('invoice-vatsell-account', correct_accounting_code('451'))
            Parameter.change_value("invoice-account-third", correct_accounting_code('400'))
    Params.clear()


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_invoice(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("invoice_params", 25))
        wizard_ident.append(("invoice_vat", 26))
    elif (xfer is not None) and (wizard_ident == "invoice_params"):
        xfer.add_title(_("Diacamma invoice"), _('Parameters'), _('Configuration of parameters'))
        fill_params(xfer, ['invoice-default-sell-account', 'invoice-reduce-account', 'invoice-account-third'], True)
    elif (xfer is not None) and (wizard_ident == "invoice_vat"):
        xfer.add_title(_("Diacamma invoice"), _('VAT'), _('Configuration of vat'))
        fill_params(xfer, ['invoice-vat-mode', 'invoice-vatsell-account'], True)
        xfer.fill_grid(10, Vat, 'vat', Vat.objects.all())
        xfer.get_components("vat").colspan = 4
