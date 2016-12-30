# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import TITLE_MODIFY, TITLE_ADD, TITLE_DELETE,\
    TITLE_PRINT
from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm
from lucterios.framework.tools import ActionsManage, MenuManage, CLOSE_YES
from lucterios.framework.tools import SELECT_SINGLE, SELECT_MULTI

from diacamma.accounting.tools import current_system_account, format_devise
from diacamma.accounting.models import Budget, CostAccounting, FiscalYear,\
    ChartsAccount
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.xferprint import XferPrintAction
from django.utils import six


@MenuManage.describ('accounting.change_budget')
class BudgetList(XferListEditor):
    icon = "account.png"
    model = Budget
    field_id = 'budget'
    caption = _("Prévisionnal budget")

    def fillresponse_header(self):
        row_id = self.get_max_row() + 1
        if self.getparam('year', 0) != 0:
            year = FiscalYear.get_current(self.getparam('year'))
            lbl = XferCompLabelForm('title_year')
            lbl.set_italic()
            lbl.set_value("{[b]}%s{[/b]} : %s" % (_('fiscal year'), year))
            lbl.set_location(1, row_id, 3)
            self.add_component(lbl)
        row_id += 1
        if self.getparam('cost_accounting') is not None:
            cost = CostAccounting.objects.get(id=self.getparam('cost_accounting', 0))
            lbl = XferCompLabelForm('title_cost')
            lbl.set_italic()
            lbl.set_value("{[b]}%s{[/b]} : %s" % (_('cost accounting'), cost))
            lbl.set_location(1, row_id, 3)
            self.add_component(lbl)
        Signal.call_signal('editbudget', self)
        self.filter = Q()
        if self.getparam('year', 0) != 0:
            self.filter &= Q(year_id=self.getparam('year'))
        if self.getparam('cost_accounting') is not None:
            self.filter &= Q(cost_accounting_id=self.getparam('cost_accounting'))

    def fill_grid(self, row, model, field_id, items):
        XferListEditor.fill_grid(self, row, model, field_id, items)
        if self.getparam('readonly', False):
            grid = self.get_components(field_id)
            grid.record_ids = []
            grid.records = {}
            last_code = ''
            value = 0
            for current_budget in items:
                if last_code != current_budget.code:
                    if last_code != '':
                        chart = ChartsAccount.get_chart_account(last_code)
                        grid.set_value(last_code, 'budget', six.text_type(chart))
                        grid.set_value(last_code, 'montant', format_devise(value, 2))
                        value = 0
                    last_code = current_budget.code
                value += current_budget.credit_debit_way() * current_budget.amount
            if last_code != '':
                chart = ChartsAccount.get_chart_account(last_code)
                grid.set_value(last_code, 'budget', six.text_type(chart))
                grid.set_value(last_code, 'montant', format_devise(value, 2))

    def fillresponse_body(self):
        self.get_components("title").colspan = 2
        row_id = self.get_max_row() + 1
        lbl = XferCompLabelForm('title_exp')
        lbl.set_value_as_headername(_("Expense"))
        lbl.set_location(0, row_id, 2)
        self.add_component(lbl)
        lbl = XferCompLabelForm('title_rev')
        lbl.set_value_as_headername(_("Revenue"))
        lbl.set_location(2, row_id, 2)
        self.add_component(lbl)

        row_id = self.get_max_row()
        self.fill_grid(row_id, self.model, 'budget_revenue', self.model.objects.filter(self.filter & Q(code__regex=current_system_account().get_revenue_mask())))
        self.move_components('budget_revenue', 2, 0)
        self.fill_grid(row_id, self.model, 'budget_expense', self.model.objects.filter(self.filter & Q(code__regex=current_system_account().get_expence_mask())))
        self.remove_component('nb_budget_expense')
        self.remove_component('nb_budget_revenue')

        resultat_budget = Budget.get_total(self.getparam('year'), self.getparam('cost_accounting'))
        if abs(resultat_budget) > 0.0001:
            row_id = self.get_max_row() + 1
            lbl = XferCompLabelForm('title_result')
            if resultat_budget > 0:
                lbl.set_value_as_name(_('result (profit)'))
            else:
                lbl.set_value_as_name(_('result (deficit)'))
            lbl.set_location(0, row_id)
            self.add_component(lbl)
            lbl = XferCompLabelForm('result')
            lbl.set_value(format_devise(resultat_budget, 5))
            lbl.set_location(1, row_id)
            self.add_component(lbl)


@MenuManage.describ('accounting.change_budget')
@ActionsManage.affect_list(TITLE_PRINT, "images/print.png")
class BudgetPrint(XferPrintAction):
    icon = "account.png"
    model = Budget
    field_id = 'budget'
    caption = _("Print previsionnal budget")
    with_text_export = True
    action_class = BudgetList


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.getparam('readonly', False) == False)
@ActionsManage.affect_list(TITLE_ADD, "images/add.png", condition=lambda item: item.getparam('readonly', False) == False)
@MenuManage.describ('accounting.add_budget')
class BudgetAddModify(XferAddEditor):
    icon = "account.png"
    model = Budget
    field_id = 'budget'
    caption_add = _("Add budget line")
    caption_modify = _("Modify budget line")

    def _search_model(self):
        if self.getparam("budget_revenue") != None:
            self.field_id = 'budget_revenue'
        if self.getparam("budget_expense") != None:
            self.field_id = 'budget_expense'
        XferAddEditor._search_model(self)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('readonly', False) == False)
@MenuManage.describ('accounting.change_budget')
class BudgetDel(XferDelete):
    icon = "account.png"
    model = Budget
    field_id = 'budget'
    caption = _("Delete Budget line")

    def _search_model(self):
        if self.getparam("budget_revenue") != None:
            self.field_id = 'budget_revenue'
        if self.getparam("budget_expense") != None:
            self.field_id = 'budget_expense'
        XferAddEditor._search_model(self)


@ActionsManage.affect_grid(_("Budget"), "account.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.change_budget')
class CostAccountingBudget(XferContainerAcknowledge):
    icon = "account.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Budget")

    def fillresponse(self):
        read_only = (self.item.status == 1) or self.item.is_protected
        self.redirect_action(BudgetList.get_action(), close=CLOSE_YES, params={'cost_accounting': self.item.id, 'readonly': read_only})


@ActionsManage.affect_list(_("Budget"), "account.png")
@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearBudget(XferContainerAcknowledge):
    icon = "account.png"
    model = ChartsAccount
    field_id = 'chartsaccount'
    caption = _("Budget")

    def fillresponse(self, year):
        fiscal_year = FiscalYear.get_current(year)
        read_only = (fiscal_year.status == 2)
        self.redirect_action(BudgetList.get_action(), close=CLOSE_YES, params={'year': fiscal_year.id, 'readonly': read_only})
