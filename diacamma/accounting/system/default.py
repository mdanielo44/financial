# -*- coding: utf-8 -*-
'''
lucterios.contacts package

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
import re

from django.utils import six
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import get_icon_path
from lucterios.framework.xferadvance import TITLE_OK, TITLE_CANCEL


class DefaultSystemAccounting(object):

    NEGATIF_ACCOUNT = ""
    POSITIF_ACCOUNT = ""

    def has_minium_code_size(self):
        return True

    def get_general_mask(self):
        return ''

    def get_cash_mask(self):
        return ''

    def get_cash_begin(self):
        return ''

    def get_provider_mask(self):
        return ''

    def get_customer_mask(self):
        return ''

    def get_employed_mask(self):
        return ''

    def get_societary_mask(self):
        return ''

    def get_revenue_mask(self):
        return ''

    def get_expence_mask(self):
        return ''

    def get_third_mask(self):
        return ''

    def get_annexe_mask(self):
        return ''

    def new_charts_account(self, code):
        return ''

    def _create_custom_for_profit(self, year, custom, val_profit):
        from django.db.models import Q
        from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm, XferCompSelect
        from diacamma.accounting.models import format_devise
        if val_profit > 0.0001:
            type_profit = _('profit')
        else:
            type_profit = _('deficit')
        img = XferCompImage("img")
        img.set_location(0, 0)
        img.set_value(get_icon_path("diacamma.accounting/images/account.png"))
        custom.add_component(img)
        lbl = XferCompLabelForm("title")
        lbl.set_value_as_headername(_("Profit and deficit"))
        lbl.set_location(1, 0)
        custom.add_component(lbl)
        # text = "{[i]}Vous avez un %s de %s.{[br/]}Vous devez definir sur quel compte l'affecter.{[br/]}{[/i]}" % (type_profit, format_devise(val_profit, 4))
        # text += "{[br/]}En validant, vous commencerez '%s'{[br/]}{[br/]}{[i]}{[u]}Attention:{[/u]} Votre report à nouveau doit être totalement fait.{[/i]}" % six.text_type(year)
        text = _("{[i]}You have a %(type)s of %(value)s.{[br/]}You must to define the account to affect.{[br/]}{[/i]}") % {'type': type_profit, 'value': format_devise(val_profit, 4)}
        text += _("{[br/]}After validation, you begin '%s'.{[br/]}{[br/]}{[i]}{[u]}Warning:{[/u]} Your retained earnings must be completed.{[/i]}") % six.text_type(year)
        lbl = XferCompLabelForm("info")
        lbl.set_value(text)
        lbl.set_location(0, 1, 2)
        custom.add_component(lbl)
        sel_cmpt = []
        query = Q(code__startswith=self.NEGATIF_ACCOUNT) | Q(code__startswith=self.POSITIF_ACCOUNT)
        for account in year.chartsaccount_set.filter(type_of_account=2).exclude(query).order_by('code'):
            sel_cmpt.append((account.id, six.text_type(account)))
        sel = XferCompSelect("profit_account")
        sel.set_select(sel_cmpt)
        sel.set_location(1, 2)
        custom.add_component(sel)
        return custom

    def _get_profit(self, year):
        from diacamma.accounting.models import EntryLineAccount, get_amount_sum
        from django.db.models.aggregates import Sum
        from django.db.models import Q
        query = Q(account__code__startswith=self.NEGATIF_ACCOUNT) | Q(account__code__startswith=self.POSITIF_ACCOUNT)
        query &= Q(account__year=year)
        val_profit = get_amount_sum(EntryLineAccount.objects.filter(query).aggregate(Sum('amount')))
        return val_profit

    def _create_profit_entry(self, year, profit_account):
        from diacamma.accounting.models import Journal, EntryAccount, EntryLineAccount, ChartsAccount
        from django.db.models import Q
        paym_journ = Journal.objects.get(id=5)
        paym_desig = _('Affect of profit/deficit')
        new_entry = EntryAccount.objects.create(year=year, journal=paym_journ, designation=paym_desig, date_value=year.begin)
        query = Q(account__code__startswith=self.NEGATIF_ACCOUNT) | Q(account__code__startswith=self.POSITIF_ACCOUNT)
        query &= Q(account__year=year)
        sum_profit = 0
        for new_line in EntryLineAccount.objects.filter(query):
            sum_profit += new_line.amount
            new_line.id = None
            new_line.entry = new_entry
            new_line.amount = -1 * new_line.amount
            new_line.save()
        new_line = EntryLineAccount()
        new_line.entry = new_entry
        new_line.amount = sum_profit
        new_line.account = ChartsAccount.objects.get(id=profit_account)
        new_line.save()
        new_entry.closed()
        return True

    def check_begin(self, year, xfer):
        profit_account = xfer.getparam('profit_account', 0)
        if profit_account > 0:
            return self._create_profit_entry(year, profit_account)
        val_profit = 0
        if xfer.getparam('with_profit', True):
            val_profit = self._get_profit(year)
        if abs(val_profit) > 0.0001:
            from lucterios.framework.tools import WrapAction, CLOSE_YES, FORMTYPE_MODAL
            custom = xfer.create_custom()
            self._create_custom_for_profit(year, custom, val_profit)
            custom.add_action(xfer.get_action(TITLE_OK, "images/ok.png"), modal=FORMTYPE_MODAL, close=CLOSE_YES)
            custom.add_action(WrapAction(TITLE_CANCEL, "images/cancel.png"))
            return False
        else:
            text = _("Do you want to begin '%s'? {[br/]}{[br/]}{[i]}{[u]}Warning:{[/u]} Your retained earnings must be completed.{[/i]}") % six.text_type(year)
            return xfer.confirme(text)

    def _create_result_entry(self, year):
        revenue = year.total_revenue
        expense = year.total_expense
        if abs(expense - revenue) > 0.0001:
            from diacamma.accounting.models import EntryAccount
            end_desig = _("Fiscal year closing - Result")
            new_entry = EntryAccount.objects.create(year=year, journal_id=5, designation=end_desig, date_value=year.end)
            if expense > revenue:
                new_entry.add_entry_line(revenue - expense, self.NEGATIF_ACCOUNT)
            else:
                new_entry.add_entry_line(revenue - expense, self.POSITIF_ACCOUNT)
            new_entry.closed(check_balance=False)

    def _create_thirds_ending_entry(self, year):
        from diacamma.accounting.models import EntryAccount, EntryLineAccount
        from django.db.models.aggregates import Sum
        sum_third = {}
        entry_lines = []
        end_desig = _("Fiscal year closing - Third")
        for data_line in EntryLineAccount.objects.filter(account__code__regex=self.get_third_mask(), account__year=year).values('account', 'third').annotate(data_sum=Sum('amount')):
            if abs(data_line['data_sum']) > 0.0001:
                entry_lines.append((data_line['data_sum'], data_line['account'], data_line['third']))
                if data_line['account'] not in sum_third.keys():
                    sum_third[data_line['account']] = 0
                sum_third[data_line['account']] += data_line['data_sum']
        if len(sum_third) > 0:
            new_entry = EntryAccount.objects.create(year=year, journal_id=5, designation=end_desig, date_value=year.end)
            for entry_line in entry_lines:
                new_line = EntryLineAccount()
                new_line.entry = new_entry
                new_line.amount = -1 * entry_line[0]
                new_line.account_id = entry_line[1]
                if entry_line[2] is not None:
                    new_line.third_id = entry_line[2]
                new_line.save()
            for account_id, value in sum_third.items():
                new_line = EntryLineAccount()
                new_line.entry = new_entry
                new_line.account_id = account_id
                new_line.amount = value
                new_line.third = None
                new_line.save()
            new_entry.closed()

    def finalize_year(self, year):
        self._create_result_entry(year)
        self._create_thirds_ending_entry(year)
        return

    def _create_report_lastyearresult(self, year, import_result):
        from diacamma.accounting.models import EntryAccount
        end_desig = _("Retained earnings - Balance sheet")
        new_entry = EntryAccount.objects.create(year=year, journal_id=1, designation=end_desig, date_value=year.begin)
        for charts_account in year.last_fiscalyear.chartsaccount_set.filter(type_of_account__in=(0, 1, 2)):
            code = charts_account.code
            name = charts_account.name
            new_entry.add_entry_line(charts_account.get_current_validated(), code, name)
        new_entry.closed()

    def _create_report_third(self, year):
        from diacamma.accounting.models import EntryAccount
        last_entry_account = list(year.last_fiscalyear.entryaccount_set.filter(journal__id=5).order_by('num'))[-1]
        _no_change, debit_rest, credit_rest = last_entry_account.serial_control(last_entry_account.get_serial())
        if abs(debit_rest - credit_rest) < 0.0001:
            end_desig = _("Retained earnings - Third party debt")
            new_entry = EntryAccount.objects.create(year=year, journal_id=1, designation=end_desig, date_value=year.begin)
            for entry_line in last_entry_account.entrylineaccount_set.all():
                if re.match(self.get_general_mask(), entry_line.account.code):
                    new_entry.add_entry_line(-1 * entry_line.amount, entry_line.account.code, entry_line.account.name, entry_line.third)
            new_entry.closed()

    def import_lastyear(self, year, import_result):
        self._create_report_lastyearresult(year, import_result)
        self._create_report_third(year)
        return

    def get_export_xmlfiles(self):
        return None
