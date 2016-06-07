# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _


from lucterios.framework.xferadvance import XferListEditor, XferDelete
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage
from lucterios.CORE.parameters import Params
from lucterios.framework.xfercomponents import XferCompButton
from lucterios.CORE.views import ParamEdit
from lucterios.framework import signal_and_lock
from lucterios.CORE.models import Parameter

from diacamma.accounting.tools import correct_accounting_code
from diacamma.payoff.models import BankAccount, PaymentMethod


@ActionsManage.affect('BankAccount', 'list')
@MenuManage.describ('payoff.change_bankaccount', FORMTYPE_NOMODAL, 'financial.conf', _('Management of parameters and configuration of payoff'))
class PayoffConf(XferListEditor):
    icon = "bank.png"
    model = BankAccount
    field_id = 'bankaccount'
    caption = _("Payoff configuration")

    def fillresponse_header(self):
        self.new_tab(_('Bank account'))

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.new_tab(_('Payment method'))
        self.fill_grid(
            0, PaymentMethod, "paymentmethod", PaymentMethod.objects.all())
        self.new_tab(_('Parameters'))
        param_lists = ['payoff-cash-account', 'payoff-bankcharges-account', 'payoff-email-message']
        Params.fill(self, param_lists, 1, 1)
        btn = XferCompButton('editparam')
        btn.set_location(1, self.get_max_row() + 1, 2, 1)
        btn.set_action(self.request, ParamEdit.get_action(
            _('Modify'), 'images/edit.png'), {'close': 0, 'params': {'params': param_lists}})
        self.add_component(btn)


@ActionsManage.affect('BankAccount', 'edit', 'add')
@MenuManage.describ('payoff.add_bankaccount')
class BankAccountAddModify(XferAddEditor):
    icon = "bank.png"
    model = BankAccount
    field_id = 'bankaccount'
    caption_add = _("Add bank account")
    caption_modify = _("Modify bank account")


@ActionsManage.affect('BankAccount', 'delete')
@MenuManage.describ('payoff.delete_bankaccount')
class BankAccountDelete(XferDelete):
    icon = "bank.png"
    model = BankAccount
    field_id = 'bankaccount'
    caption = _("Delete bank account")


@ActionsManage.affect('PaymentMethod', 'edit', 'add')
@MenuManage.describ('payoff.add_bankaccount')
class PaymentMethodAddModify(XferAddEditor):
    icon = "bank.png"
    model = PaymentMethod
    field_id = 'paymentmethod'
    caption_add = _("Add payment method")
    caption_modify = _("Modify payment method")


@ActionsManage.affect('PaymentMethod', 'delete')
@MenuManage.describ('payoff.delete_bankaccount')
class PaymentMethodDelete(XferDelete):
    icon = "bank.png"
    model = PaymentMethod
    field_id = 'paymentmethod'
    caption = _("Delete payment method")


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_payoff(known_codes, accompt_returned):
    bank_unknown = BankAccount.objects.exclude(
        account_code__in=known_codes).values_list('account_code', flat=True).distinct()
    param_unknown = Parameter.objects.filter(name__in=(
        'payoff-cash-account', 'payoff-bankcharges-account')).exclude(value__in=known_codes).values_list('value', flat=True).distinct()
    comptenofound = ""
    if (len(bank_unknown) > 0):
        comptenofound = _("bank account") + ":" + ",".join(bank_unknown) + " "
    if (len(param_unknown) > 0):
        comptenofound += _("parameters") + ":" + ",".join(param_unknown)
    if comptenofound != "":
        accompt_returned.append(
            "- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Payoff'), comptenofound))
    return True


@signal_and_lock.Signal.decorate('param_change')
def paramchange_payoff(params):
    if 'accounting-sizecode' in params:
        for bank in BankAccount.objects.all():
            if bank.account_code != correct_accounting_code(bank.account_code):
                bank.account_code = correct_accounting_code(bank.account_code)
                bank.save()
    if ('payoff-cash-account' in params) or ('accounting-sizecode' in params):
        Parameter.change_value(
            'payoff-cash-account', correct_accounting_code(Params.getvalue('payoff-cash-account')))
    if ('payoff-bankcharges-account' in params) or ('accounting-sizecode' in params):
        pvalue = Params.getvalue('payoff-bankcharges-account')
        if pvalue != '':
            Parameter.change_value(
                'payoff-bankcharges-account', correct_accounting_code(pvalue))
    Params.clear()
