# -*- coding: utf-8 -*-

'''
Describe database model for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompHeader,\
    XferCompSelect, XferCompCheckList, XferCompCheck, XferCompFloat,\
    XferCompEdit, XferCompMemo
from lucterios.framework.tools import CLOSE_NO, FORMTYPE_REFRESH
from lucterios.framework.models import get_value_if_choices
from lucterios.CORE.parameters import Params

from diacamma.accounting.tools import current_system_account
from diacamma.accounting.models import CostAccounting, FiscalYear, Third
from diacamma.payoff.editors import SupportingEditor
from django.utils import six
from diacamma.invoice.models import Provider, Category, CustomField


class CustomFieldEditor(LucteriosEditor):

    def _edit_add_args(self, xfer, obj_kind):
        args = self.item.get_args()
        arg = XferCompCheck('args_multi')
        arg.set_value(args['multi'])
        arg.set_location(obj_kind.col, obj_kind.row + 1, obj_kind.colspan, 1)
        arg.description = _('multi-line')
        xfer.add_component(arg)
        arg = XferCompFloat('args_min', -10000, 10000, 0)
        arg.set_value(args['min'])
        arg.set_location(obj_kind.col, obj_kind.row + 2, obj_kind.colspan, 1)
        arg.description = _('min')
        xfer.add_component(arg)
        arg = XferCompFloat('args_max', -10000, 10000, 0)
        arg.set_value(args['max'])
        arg.set_location(obj_kind.col, obj_kind.row + 3, obj_kind.colspan, 1)
        arg.description = _('max')
        xfer.add_component(arg)
        arg = XferCompFloat('args_prec', 0, 10, 0)
        arg.set_value(args['prec'])
        arg.set_location(obj_kind.col, obj_kind.row + 4, obj_kind.colspan, 1)
        arg.description = _('precision')
        xfer.add_component(arg)
        arg = XferCompEdit('args_list')
        arg.set_value(','.join(args['list']))
        arg.set_location(obj_kind.col, obj_kind.row + 5, obj_kind.colspan, 1)
        arg.description = _('list')
        xfer.add_component(arg)

    def edit(self, xfer):
        obj_kind = xfer.get_components('kind')
        self._edit_add_args(xfer, obj_kind)
        obj_kind.java_script = """
var type=current.getValue();
parent.get('args_multi').setVisible(type==0);
parent.get('args_min').setVisible(type==1 || type==2);
parent.get('args_max').setVisible(type==1 || type==2);
parent.get('args_prec').setVisible(type==2);
parent.get('args_list').setVisible(type==4);
"""

    def saving(self, xfer):
        args = {}
        for arg_name in ['min', 'max', 'prec', 'list', 'multi']:
            args_val = xfer.getparam('args_' + arg_name)
            if args_val is not None:
                if arg_name == 'list':
                    args[arg_name] = list(args_val.split(','))
                elif arg_name == 'multi':
                    args[arg_name] = (args_val != 'False') and (args_val != '0') and (args_val != '') and (args_val != 'n')
                else:
                    args[arg_name] = float(args_val)
        self.item.args = six.text_type(args)
        LucteriosEditor.saving(self, xfer)
        self.item.save()

    def get_comp(self, value):
        comp = None
        args = self.item.get_args()
        if self.item.kind == 0:
            if args['multi']:
                comp = XferCompMemo(self.item.get_fieldname())
            else:
                comp = XferCompEdit(self.item.get_fieldname())
            comp.set_value(value)
        elif (self.item.kind == 1) or (self.item.kind == 2):
            comp = XferCompFloat(
                self.item.get_fieldname(), args['min'], args['max'], args['prec'])
            comp.set_value(value)
        elif self.item.kind == 3:
            comp = XferCompCheck(self.item.get_fieldname())
            comp.set_value(value)
        elif self.item.kind == 4:
            val_selected = value
            select_id = 0
            select_list = []
            for sel_item in args['list']:
                if sel_item == val_selected:
                    select_id = len(select_list)
                select_list.append((len(select_list), sel_item))
            comp = XferCompSelect(self.item.get_fieldname())
            comp.set_select(select_list)
            comp.set_value(select_id)
        return comp


class ArticleEditor(LucteriosEditor):

    def _edit_custom_field(self, xfer, init_col):
        col = init_col
        col_offset = 0
        colspan = 1
        row = xfer.get_max_row() + 5
        for cf_model in CustomField.objects.all():
            cf_name = cf_model.get_fieldname()
            comp = cf_model.editor.get_comp(getattr(self.item, cf_name))
            comp.set_location(col + col_offset, row, colspan, 1)
            comp.description = cf_model.name
            xfer.add_component(comp)
            col_offset += 1
            if col_offset == 2:
                col_offset = 0
                colspan = 1
                row += 1
            else:
                colspan = 2

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('price').prec = currency_decimal
        old_account = xfer.get_components("sell_account")
        xfer.tab = old_account.tab
        xfer.remove_component("sell_account")
        sel_code = XferCompSelect("sell_account")
        sel_code.description = old_account.description
        sel_code.set_location(old_account.col, old_account.row, old_account.colspan + 1, old_account.rowspan)
        for item in FiscalYear.get_current().chartsaccount_set.all().filter(code__regex=current_system_account().get_revenue_mask()).order_by('code'):
            sel_code.select_list.append((item.code, six.text_type(item)))
        sel_code.set_value(self.item.sell_account)
        xfer.add_component(sel_code)
        self._edit_custom_field(xfer, sel_code.col)

    def saving(self, xfer):
        LucteriosEditor.saving(self, xfer)
        self.item.set_custom_values(xfer.params)


class BillEditor(SupportingEditor):

    def edit(self, xfer):
        xfer.move(0, 0, 2)
        xfer.fill_from_model(1, 0, True, ["third"])
        comp_comment = xfer.get_components('comment')
        comp_comment.with_hypertext = True
        comp_comment.set_size(100, 375)
        com_type = xfer.get_components('bill_type')
        com_type.set_action(xfer.request, xfer.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        if xfer.item.bill_type == 0:
            xfer.remove_component("cost_accounting")
        else:
            comp = xfer.get_components("cost_accounting")
            comp.set_needed(False)
            comp.set_select_query(CostAccounting.objects.filter(Q(status=0) & (Q(year=None) | Q(year=FiscalYear.get_current()))))
            if xfer.item.id is None:
                comp.set_value(xfer.item.cost_accounting_id)
            else:
                cost_acc = CostAccounting.objects.filter(is_default=True)
                if len(cost_acc) > 0:
                    comp.set_value(cost_acc[0].id)
                else:
                    comp.set_value(0)

    def show(self, xfer):
        try:
            if xfer.item.cost_accounting is None:
                xfer.remove_component("cost_accounting")
        except ObjectDoesNotExist:
            xfer.remove_component("cost_accounting")
        xfer.params['new_account'] = Params.getvalue('invoice-account-third')
        xfer.move(0, 0, 1)
        lbl = XferCompLabelForm('title')
        lbl.set_location(1, 0, 4)
        lbl.set_value_as_title(get_value_if_choices(
            self.item.bill_type, self.item.get_field_by_name('bill_type')))
        xfer.add_component(lbl)
        details = xfer.get_components('detail')
        if Params.getvalue("invoice-vat-mode") != 0:
            if Params.getvalue("invoice-vat-mode") == 1:
                details.headers[2] = XferCompHeader(details.headers[2].name, _(
                    'price excl. taxes'), details.headers[2].type, details.headers[2].orderable)
                details.headers[6] = XferCompHeader(details.headers[6].name, _(
                    'total excl. taxes'), details.headers[6].type, details.headers[6].orderable)
            elif Params.getvalue("invoice-vat-mode") == 2:
                details.headers[2] = XferCompHeader(details.headers[2].name, _(
                    'price incl. taxes'), details.headers[2].type, details.headers[2].orderable)
                details.headers[6] = XferCompHeader(details.headers[6].name, _(
                    'total incl. taxes'), details.headers[6].type, details.headers[6].orderable)
            xfer.get_components('total_excltax').description = _('total excl. taxes')
            xfer.filltab_from_model(1, xfer.get_max_row() + 1, True, [((_('VTA sum'), 'vta_sum'), (_('total incl. taxes'), 'total_incltax'))])
        if self.item.status == 0:
            SupportingEditor.show_third(self, xfer, 'invoice.add_bill')
            xfer.get_components('date').colspan += 1
            xfer.get_components('detail').colspan += 1
        else:
            SupportingEditor.show_third_ex(self, xfer)
            details.actions = []
            if self.item.bill_type != 0:
                SupportingEditor.show(self, xfer)
        return


class DetailEditor(LucteriosEditor):

    def before_save(self, xfer):
        self.item.vta_rate = 0
        if (Params.getvalue("invoice-vat-mode") != 0) and (self.item.article is not None) and (self.item.article.vat is not None):
            self.item.vta_rate = float(self.item.article.vat.rate / 100)
        if Params.getvalue("invoice-vat-mode") == 2:
            self.item.vta_rate = -1 * self.item.vta_rate
        return

    def _add_provider_filter(self, xfer, sel_art, init_row):
        old_model = xfer.model
        xfer.model = Provider
        xfer.item = Provider()
        xfer.filltab_from_model(sel_art.col, init_row, False, ['third'])
        xfer.filltab_from_model(sel_art.col + 1, init_row, False, ['reference'])
        xfer.item = self.item
        xfer.model = old_model
        filter_thirdid = xfer.getparam('third', 0)
        filter_ref = xfer.getparam('reference', '')
        sel_third = xfer.get_components("third")
        sel_third.set_needed(False)
        sel_third.set_select_query(Third.objects.filter(provider__isnull=False))
        sel_third.set_value(filter_thirdid)
        sel_third.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
        sel_third.description = _('provider')
        sel_ref = xfer.get_components("reference")
        sel_ref.set_value(filter_ref)
        sel_ref.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
        if (filter_thirdid != 0) or (filter_ref != ''):
            sel_art.set_needed(True)

    def edit(self, xfer):
        sel_art = xfer.get_components("article")
        init_row = sel_art.row
        xfer.move(sel_art.tab, 0, 10)
        sel_art.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components('reduce').prec = currency_decimal

        has_filter = False
        cat_list = Category.objects.all()
        if len(cat_list) > 0:
            filter_cat = xfer.getparam('cat_filter', ())
            edt = XferCompCheckList("cat_filter")
            edt.set_select_query(cat_list)
            edt.set_value(filter_cat)
            edt.set_location(sel_art.col, init_row, 2)
            edt.description = _('categories')
            edt.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
            xfer.add_component(edt)
            if len(filter_cat) > 0:
                sel_art.set_needed(True)
            has_filter = True
        if len(Provider.objects.all()) > 0:
            self._add_provider_filter(xfer, sel_art, init_row + 1)
            has_filter = True
        if has_filter:
            lbl = XferCompLabelForm('sep_filter')
            lbl.set_value("{[hr/]}")
            lbl.set_location(sel_art.col, init_row + 9, 2)
            xfer.add_component(lbl)
