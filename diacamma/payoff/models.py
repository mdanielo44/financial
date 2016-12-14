# -*- coding: utf-8 -*-
'''
diacamma.payoff models package

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
from _io import BytesIO

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_module
from django.utils import six
from django_fsm import FSMIntegerField, transition

from lucterios.framework.models import LucteriosModel, get_value_converted
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.printgenerators import ReportingGenerator
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.models import PrintModel, Parameter
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import LegalEntity, Individual

from diacamma.accounting.models import EntryAccount, FiscalYear, Third, Journal, \
    ChartsAccount, EntryLineAccount, AccountLink
from diacamma.accounting.tools import format_devise, currency_round, correct_accounting_code


def remove_accent(text, replace_space=False):
    if replace_space:
        text = text.replace(' ', '_').replace('-', '')
    try:
        import unicodedata
        return ''.join((letter for letter in unicodedata.normalize('NFD', text) if unicodedata.category(letter) != 'Mn'))
    except:
        return text


class Supporting(LucteriosModel):
    third = models.ForeignKey(
        Third, verbose_name=_('third'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    is_revenu = models.BooleanField(verbose_name=_('is revenu'), default=True)

    @classmethod
    def get_payoff_fields(cls):
        return ['payoff_set', ((_('total payed'), 'total_payed'), (_('rest to pay'), 'total_rest_topay'))]

    @classmethod
    def get_print_fields(cls):
        return ['payoff_set', (_('total payed'), 'total_payed'), (_('rest to pay'), 'total_rest_topay')]

    class Meta(object):
        verbose_name = _('supporting')
        verbose_name_plural = _('supporting')
        default_permissions = []

    def get_total(self):
        raise Exception('no implemented!')

    def get_third_mask(self):
        raise Exception('no implemented!')

    def get_max_payoff(self, ignore_payoff=-1):
        return self.get_total_rest_topay(ignore_payoff)

    def payoff_is_revenu(self):
        raise Exception('no implemented!')

    def default_date(self):
        return date.today()

    def default_costaccounting(self):
        return None

    def entry_links(self):
        return None

    @property
    def payoff_query(self):
        return Q()

    def get_total_payed(self, ignore_payoff=-1):
        val = 0
        for payoff in self.payoff_set.filter(self.payoff_query):
            if payoff.id != ignore_payoff:
                val += currency_round(payoff.amount)
        return val

    def get_info_state(self, third_mask=None):
        info = []
        if third_mask is None:
            third_mask = self.get_third_mask()
        if self.status == 0:
            if self.third is None:
                info.append(six.text_type(_("no third selected")))
            else:
                accounts = self.third.accountthird_set.filter(
                    code__regex=third_mask)
                try:
                    if (len(accounts) == 0) or (ChartsAccount.get_account(accounts[0].code, FiscalYear.get_current()) is None):
                        info.append(
                            six.text_type(_("third has not correct account")))
                except LucteriosException as err:
                    info.append(six.text_type(err))
        return info

    def check_date(self, date):
        info = []
        fiscal_year = FiscalYear.get_current()
        if (fiscal_year.begin.isoformat() > date) or (fiscal_year.end.isoformat() < date):
            info.append(
                six.text_type(_("date not include in current fiscal year")))
        return info

    def get_third_account(self, third_mask, fiscalyear, third=None):
        if third is None:
            third = self.third
        accounts = third.accountthird_set.filter(code__regex=third_mask)
        if len(accounts) == 0:
            raise LucteriosException(
                IMPORTANT, _("third has not correct account"))
        third_account = ChartsAccount.get_account(
            accounts[0].code, fiscalyear)
        if third_account is None:
            raise LucteriosException(
                IMPORTANT, _("third has not correct account"))
        return third_account

    @property
    def total_payed(self):
        return format_devise(self.get_total_payed(), 5)

    def get_total_rest_topay(self, ignore_payoff=-1):
        return self.get_total() - self.get_total_payed(ignore_payoff)

    @property
    def total_rest_topay(self):
        return format_devise(self.get_total_rest_topay(), 5)

    def get_tax_sum(self):
        return 0.0

    def send_email(self, subject, message, model):
        fct_mailing_mod = import_module('lucterios.mailing.functions')
        pdf_name = "%s.pdf" % self.get_document_filename()
        gen = ReportingGenerator()
        gen.items = [self]
        gen.model_text = PrintModel.objects.get(id=model).value
        pdf_file = BytesIO(gen.generate_report(None, False))
        cclist = []
        contact = self.third.contact.get_final_child()
        if isinstance(contact, LegalEntity):
            for indiv in Individual.objects.filter(responsability__legal_entity=self.third.contact):
                if indiv.email != '':
                    cclist.append(indiv.email)
        if len(cclist) == 0:
            cclist = None
        fct_mailing_mod.send_email(self.third.contact.email, subject, message, [(pdf_name, pdf_file)], cclist=cclist, withcopy=True)

    def get_document_filename(self):
        return remove_accent(self.get_payment_name(), True)

    @classmethod
    def get_payment_fields(cls):
        raise Exception('no implemented!')

    def support_validated(self, validate_date):
        raise Exception('no implemented!')

    def get_tax(self):
        raise Exception('no implemented!')

    def get_payable_without_tax(self):
        raise Exception('no implemented!')

    def payoff_have_payment(self):
        raise Exception('no implemented!')

    def get_payment_name(self):
        return six.text_type(self)

    def get_docname(self):
        return six.text_type(self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.is_revenu = self.get_final_child().payoff_is_revenu()
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class BankAccount(LucteriosModel):
    designation = models.TextField(_('designation'), null=False)
    reference = models.CharField(_('reference'), max_length=200, null=False)
    account_code = models.CharField(
        _('account code'), max_length=50, null=False)

    @classmethod
    def get_default_fields(cls):
        return ["designation", "reference", "account_code"]

    def __str__(self):
        return self.designation

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.account_code = correct_accounting_code(self.account_code)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('bank account')
        verbose_name_plural = _('bank accounts')


class Payoff(LucteriosModel):
    supporting = models.ForeignKey(
        Supporting, verbose_name=_('supporting'), null=False, db_index=True, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_('date'), null=False)
    amount = models.DecimalField(verbose_name=_('amount'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    mode = models.IntegerField(verbose_name=_('mode'),
                               choices=((0, _('cash')), (1, _('cheque')), (2, _('transfer')), (3, _('crédit card')), (4, _('other')), (5, _('levy'))), null=False, default=0, db_index=True)
    payer = models.CharField(_('payer'), max_length=150, null=True, default='')
    reference = models.CharField(
        _('reference'), max_length=100, null=True, default='')
    entry = models.ForeignKey(
        EntryAccount, verbose_name=_('entry'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(BankAccount, verbose_name=_(
        'bank account'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    bank_fee = models.DecimalField(verbose_name=_('bank fee'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])

    @classmethod
    def get_default_fields(cls):
        return ["date", (_('value'), "value"), "mode", "reference", "payer", "bank_account"]

    @classmethod
    def get_edit_fields(cls):
        return ["date", "amount", "payer", "mode", "bank_account", "reference", "bank_fee"]

    @property
    def value(self):
        return format_devise(self.amount, 5)

    def delete_accounting(self):
        if self.entry is not None:
            payoff_entry = self.entry
            if payoff_entry.close:
                raise LucteriosException(
                    IMPORTANT, _("an entry associated to this payoff is closed!"))
            self.entry = None
            self.save(do_generate=False)
            payoff_entry.delete()

    def generate_accountlink(self):
        supporting = self.supporting.get_final_child()
        if (self.entry is not None) and (abs(supporting.get_total_rest_topay()) < 0.0001) and (supporting.entry_links() is not None) and (len(supporting.entry_links()) > 0):
            try:
                entryline = []
                for all_payoff in supporting.payoff_set.filter(supporting.payoff_query):
                    entryline.extend(all_payoff.supporting.entry_links())
                    entryline.append(all_payoff.entry)
                entryline = list(set(entryline))
                AccountLink.create_link(entryline)
            except LucteriosException:
                pass

    def generate_accounting(self, third_amounts, designation=None):
        supporting = self.supporting.get_final_child()
        if self.supporting.is_revenu:
            is_revenu = -1
        else:
            is_revenu = 1
        years = FiscalYear.objects.filter(begin__lte=self.date, end__gte=self.date)
        if len(years) == 1:
            fiscal_year = years[0]
        else:
            fiscal_year = FiscalYear.get_current()
        if designation is None:
            designation = _("payoff for %s") % six.text_type(supporting)
        new_entry = EntryAccount.objects.create(
            year=fiscal_year, date_value=self.date, designation=designation,
            journal=Journal.objects.get(id=4), costaccounting=supporting.default_costaccounting())
        amount_to_bank = 0
        for third, amount in third_amounts:
            third_account = third.get_account(fiscal_year, supporting.get_third_mask())
            if third_account.type_of_account == 0:
                is_liability = 1
            else:
                is_liability = -1
            EntryLineAccount.objects.create(account=third_account, amount=is_liability * is_revenu * amount, third=third, entry=new_entry)
            amount_to_bank += float(amount)
        if self.bank_account is None:
            bank_code = Params.getvalue("payoff-cash-account")
        else:
            bank_code = self.bank_account.account_code
        bank_account = ChartsAccount.get_account(bank_code, fiscal_year)
        if bank_account is None:
            raise LucteriosException(
                IMPORTANT, _("account is not defined!"))
        fee_code = Params.getvalue("payoff-bankcharges-account")
        if (fee_code != '') and (float(self.bank_fee) > 0.001):
            fee_account = ChartsAccount.get_account(fee_code, fiscal_year)
            if fee_account is not None:
                EntryLineAccount.objects.create(account=fee_account,
                                                amount=-1 * is_revenu * float(self.bank_fee), entry=new_entry)
                amount_to_bank -= float(self.bank_fee)
        EntryLineAccount.objects.create(account=bank_account,
                                        amount=-1 * is_revenu * amount_to_bank, entry=new_entry)
        return new_entry

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, do_generate=True, do_linking=True):
        if not force_insert and do_generate:
            self.delete_accounting()
            self.entry = self.generate_accounting([(self.supporting.third, float(self.amount))])
        res = LucteriosModel.save(self, force_insert, force_update, using, update_fields)
        if not force_insert and do_linking:
            self.generate_accountlink()
        return res

    @classmethod
    def multi_save(cls, supportings, amount, mode, payer, reference, bank_account, date):
        supporting_list = Supporting.objects.filter(id__in=supportings, is_revenu=True)
        amount_sum = 0
        for supporting in supporting_list:
            amount_sum += supporting.get_final_child().get_total_rest_topay()
        if abs(amount_sum) < 0.0001:
            raise LucteriosException(IMPORTANT, _('No-valid selection!'))
        amount_rest = amount
        paypoff_list = []
        for supporting in supporting_list:
            new_paypoff = Payoff(
                supporting=supporting, date=date, payer=payer, mode=mode, reference=reference)
            if bank_account != 0:
                new_paypoff.bank_account = BankAccount.objects.get(
                    id=bank_account)
            new_paypoff.amount = currency_round(
                supporting.get_final_child().get_total_rest_topay() * amount / amount_sum)
            if new_paypoff.amount > 0.0001:
                amount_rest -= new_paypoff.amount
                new_paypoff.save(do_generate=False)
                paypoff_list.append(new_paypoff)
        if abs(amount_rest) > 0.001:
            new_paypoff.amount += amount_rest
            new_paypoff.save(do_generate=False)
        third_amounts = {}
        designation_items = []
        for paypoff_item in paypoff_list:
            if paypoff_item.supporting.third not in third_amounts.keys():
                third_amounts[paypoff_item.supporting.third] = 0
            third_amounts[paypoff_item.supporting.third] += paypoff_item.amount
            designation_items.append(six.text_type(paypoff_item.supporting.get_final_child()))
        designation = _("payoff for %s") % ",".join(designation_items)
        if len(designation) > 190:
            designation = _("payoff for %d multi-pay") % len(designation_items)
        new_entry = paypoff_list[0].generate_accounting(third_amounts.items(), designation)
        for paypoff_item in paypoff_list:
            paypoff_item.entry = new_entry
            paypoff_item.save(do_generate=False)
        new_entry.unlink()
        try:
            entrylines = []
            for supporting in supporting_list:
                supporting = supporting.get_final_child()
                if (abs(supporting.get_total_rest_topay()) < 0.0001) and (supporting.entry_links() is not None) and (len(supporting.payoff_set.filter(supporting.payoff_query)) == 1):
                    entrylines.extend(supporting.entry_links())
            if len(entrylines) == len(supporting_list):
                entrylines.append(new_entry)
                AccountLink.create_link(entrylines)
        except LucteriosException:
            pass

    def delete(self, using=None):
        self.delete_accounting()
        LucteriosModel.delete(self, using)

    class Meta(object):
        verbose_name = _('payoff')
        verbose_name_plural = _('payoffs')


class DepositSlip(LucteriosModel):

    status = FSMIntegerField(verbose_name=_('status'), choices=(
        (0, _('building')), (1, _('closed')), (2, _('valid'))), null=False, default=0, db_index=True)
    bank_account = models.ForeignKey(BankAccount, verbose_name=_(
        'bank account'), null=False, db_index=True, on_delete=models.PROTECT)
    date = models.DateField(verbose_name=_('date'), null=False)
    reference = models.CharField(
        _('reference'), max_length=100, null=False, default='')

    def __str__(self):
        return "%s %s" % (self.reference, get_value_converted(self.date))

    @classmethod
    def get_default_fields(cls):
        return ['status', 'bank_account', 'date', 'reference', (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ['bank_account', 'reference', 'date']

    @classmethod
    def get_show_fields(cls):
        return ['bank_account', 'bank_account.reference', ("date", "reference"), ((_('number'), "nb"), (_('total'), 'total')), "depositdetail_set"]

    def get_total(self):
        value = 0
        for detail in self.depositdetail_set.all():
            value += detail.get_amount()
        return value

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    @property
    def nb(self):
        return len(self.depositdetail_set.all())

    def can_delete(self):
        if self.status != 0:
            return _('Remove of %s impossible!') % six.text_type(self)
        return ''

    transitionname__close_deposit = _("To Close")

    @transition(field=status, source=0, target=1, conditions=[lambda item:len(item.depositdetail_set.all()) > 0])
    def close_deposit(self):
        pass

    transitionname__validate_deposit = _("Validate")

    @transition(field=status, source=1, target=2)
    def validate_deposit(self):
        for detail in self.depositdetail_set.all():
            detail.payoff.entry.closed()

    def add_payoff(self, entries):
        if self.status == 0:
            for entry in entries:
                payoff_list = Payoff.objects.filter(entry_id=entry)
                if len(payoff_list) > 0:
                    DepositDetail.objects.create(
                        deposit=self, payoff=payoff_list[0])

    class Meta(object):
        verbose_name = _('deposit slip')
        verbose_name_plural = _('deposit slips')


class DepositDetail(LucteriosModel):

    deposit = models.ForeignKey(
        DepositSlip, verbose_name=_('deposit'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    payoff = models.ForeignKey(
        Payoff, verbose_name=_('payoff'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    @classmethod
    def get_default_fields(cls):
        return ['payoff.payer', 'payoff.date', 'payoff.reference', (_('amount'), 'amount')]

    @classmethod
    def get_edit_fields(cls):
        return []

    @property
    def customer(self):
        return self.payoff.payer

    @property
    def date(self):
        return self.payoff.date

    @property
    def reference(self):
        return self.payoff.reference

    def get_amount(self):
        values = Payoff.objects.filter(
            entry=self.payoff.entry, reference=self.payoff.reference).aggregate(Sum('amount'))
        if 'amount__sum' in values.keys():
            return values['amount__sum']
        else:
            return 0

    @property
    def amount(self):
        return format_devise(self.get_amount(), 5)

    @classmethod
    def get_payoff_not_deposit(cls, payer, reference, order_list):
        payoff_nodeposit = []
        entity_known = DepositDetail.objects.values_list(
            'payoff__entry_id', flat=True).distinct()
        entity_unknown = Payoff.objects.filter(supporting__is_revenu=True, mode=1).exclude(entry_id__in=entity_known).values(
            'entry_id', 'date', 'reference', 'payer').annotate(amount=Sum('amount'))
        if payer != '':
            entity_unknown = entity_unknown.filter(payer__icontains=payer)
        if reference != '':
            entity_unknown = entity_unknown.filter(
                reference__icontains=reference)
        if order_list is not None:
            entity_unknown = entity_unknown.order_by(*order_list)
        for values in entity_unknown:
            payoff = {}
            payoff['id'] = values['entry_id']
            bills = []
            for supporting in Supporting.objects.filter(payoff__entry=values['entry_id']):
                bills.append(six.text_type(supporting.get_final_child()))
            payoff['bill'] = '{[br/]}'.join(bills)
            payoff['payer'] = values['payer']
            payoff['amount'] = format_devise(values['amount'], 5)
            payoff['date'] = values['date']
            payoff['reference'] = values['reference']
            payoff_nodeposit.append(payoff)
        return payoff_nodeposit

    class Meta(object):
        verbose_name = _('deposit detail')
        verbose_name_plural = _('deposit details')
        default_permissions = []


class PaymentMethod(LucteriosModel):
    paytype = models.IntegerField(verbose_name=_('type'),
                                  choices=((0, _('transfer')), (1, _('cheque')), (2, _('PayPal'))), null=False, default=0, db_index=True)
    bank_account = models.ForeignKey(BankAccount,
                                     verbose_name=_('bank account'), null=False, default=None, db_index=True, on_delete=models.PROTECT)
    extra_data = models.TextField(_('data'), null=False)

    @classmethod
    def get_default_fields(cls):
        return ['paytype', 'bank_account', (_('parameters'), 'info')]

    @classmethod
    def get_edit_fields(cls):
        return ['paytype', 'bank_account']

    def get_extra_fields(self):
        self.paytype = int(self.paytype)
        if self.paytype == 0:
            return [(1, _('IBAN'), 0), (2, _('BIC'), 0)]
        elif self.paytype == 1:
            return [(1, _('payable to'), 0), (2, _('address'), 1)]
        elif self.paytype == 2:
            return [(1, _('Paypal account'), 0)]
        else:
            return []

    def set_items(self, items):
        size = len(self.get_extra_fields())
        while len(items) < size:
            items.append("")
        self.extra_data = "\n".join(items)

    def get_items(self):
        self.paytype = int(self.paytype)
        if (self.id is None) and (self.paytype == 1) and (self.extra_data == ''):
            current_legal = LegalEntity.objects.get(id=1)
            items = [current_legal.name, "%s{[newline]}%s %s" % (
                current_legal.address, current_legal.postal_code, current_legal.city)]
        else:
            items = self.extra_data.split("\n")
        size = len(self.get_extra_fields())
        while len(items) < size:
            items.append("")
        return items

    @property
    def info(self):
        res = ""
        items = self.get_items()
        for fieldid, fieldtitle, _fieldtype in self.get_extra_fields():
            res += "{[b]}%s{[/b]}{[br/]}" % fieldtitle
            res += items[fieldid - 1]
            res += "{[br/]}"
        return res

    def show_pay(self, absolute_uri, lang, supporting):
        items = self.get_items()
        if self.paytype == 0:
            formTxt = "{[center]}"
            formTxt += "{[table width='100%']}{[tr]}"
            formTxt += "    {[td]}{[u]}{[i]}%s{[/i]}{[/u]}{[/td]}" % _('IBAN')
            formTxt += "    {[td]}%s{[/td]}" % items[0]
            formTxt += "{[/tr]}{[tr]}"
            formTxt += "    {[td]}{[u]}{[i]}%s{[/i]}{[/u]}{[/td]}" % _('BIC')
            formTxt += "    {[td]}%s{[/td]}" % items[1]
            formTxt += "{[/tr]}{[/table]}"
            formTxt += "{[/center]}"
        elif self.paytype == 1:
            formTxt = "{[center]}"
            formTxt += "{[table width='100%%']}"
            formTxt += "    {[tr]}"
            formTxt += "        {[td]}{[u]}{[i]}%s{[/i]}{[/u]}{[/td]}" % _('payable to')
            formTxt += "        {[td]}%s{[/td]}" % items[0]
            formTxt += "    {[/tr]}"
            formTxt += "    {[tr]}"
            formTxt += "        {[td]}{[u]}{[i]}%s{[/i]}{[/u]}{[/td]}" % _('address')
            formTxt += "        {[td]}%s{[/td]}" % items[1]
            formTxt += "    {[/tr]}"
            formTxt += "{[/table]}"
            formTxt += "{[/center]}"
        elif self.paytype == 2:
            try:
                from urllib.parse import quote_plus
            except:
                from urllib import quote_plus
            paypal_url = getattr(settings, 'DIACAMMA_PAYOFF_PAYPAL_URL', 'https://www.paypal.com/cgi-bin/webscr')
            abs_url = absolute_uri.split('/')
            paypal_dict = {}
            paypal_dict['business'] = items[0]
            paypal_dict['currency_code'] = Params.getvalue("accounting-devise-iso")
            paypal_dict['lc'] = lang
            paypal_dict['return'] = '/'.join(abs_url[:-2])
            paypal_dict['cancel_return'] = '/'.join(abs_url[:-2])
            paypal_dict['notify_url'] = paypal_dict['return'] + '/diacamma.payoff/validationPaymentPaypal'
            paypal_dict['item_name'] = remove_accent(supporting.get_payment_name())
            paypal_dict['custom'] = six.text_type(supporting.id)
            paypal_dict['tax'] = six.text_type(supporting.get_tax())
            paypal_dict['amount'] = six.text_type(supporting.get_payable_without_tax())
            paypal_dict['cmd'] = '_xclick'
            paypal_dict['no_note'] = '1'
            paypal_dict['no_shipping'] = '1'
            args = ""
            for key, val in paypal_dict.items():
                args += "&%s=%s" % (key, quote_plus(val))
            formTxt = "{[center]}"
            formTxt += "{[a href='%s?%s' target='_blank']}" % (paypal_url, args[1:])
            formTxt += "{[img src='https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_74x46.jpg' title='PayPal' alt='PayPal' /]}"
            formTxt += "{[/a]}"
            formTxt += "{[/center]}"
        else:
            formTxt = "???"
        return formTxt

    class Meta(object):
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        default_permissions = []
        ordering = ['paytype']


class BankTransaction(LucteriosModel):
    date = models.DateTimeField(verbose_name=_('date'), null=False)
    status = models.IntegerField(verbose_name=_('status'), choices=(
        (0, _('failure')), (1, _('success'))), null=False, default=0, db_index=True)
    payer = models.CharField(_('payer'), max_length=200, null=False)
    amount = models.DecimalField(verbose_name=_('amount'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)], null=True)
    contains = models.TextField(_('contains'), null=True)

    @classmethod
    def get_default_fields(cls):
        return ['date', 'status', 'payer', 'amount']

    @classmethod
    def get_show_fields(cls):
        return [('date', 'status'), ('payer', 'amount'), 'contains']

    class Meta(object):
        verbose_name = _('bank transaction')
        verbose_name_plural = _('bank transactions')
        default_permissions = ['change']
        ordering = ['-date']


def check_payoff_accounting():
    for entry in EntryAccount.objects.filter(close=False, journal_id=4):
        _no_change, debit_rest, credit_rest = entry.serial_control(entry.get_serial())
        payoff_list = entry.payoff_set.all()
        if abs(debit_rest - credit_rest) > 0.0001:
            if len(payoff_list) > 0:
                third_amounts = []
                designation_items = []
                for paypoff_item in payoff_list:
                    third_amounts.append((paypoff_item.supporting.third, float(paypoff_item.amount)))
                    designation_items.append(six.text_type(paypoff_item.supporting.get_final_child()))
                designation = _("payoff for %s") % ",".join(designation_items)
                if len(designation) > 190:
                    designation = _("payoff for %d multi-pay") % len(designation_items)
                entry.unlink()
                new_entry = payoff_list[0].generate_accounting(third_amounts, designation)
                for paypoff_item in payoff_list:
                    paypoff_item.entry = new_entry
                    paypoff_item.save(do_generate=False)
                new_entry.unlink()
                entry.delete()
                try:
                    entrylines = []
                    for paypoff_item in payoff_list:
                        supporting = paypoff_item.supporting.get_final_child()
                        if (abs(supporting.get_total_rest_topay()) < 0.0001) and (supporting.entry_links() is not None) and (len(supporting.payoff_set.filter(supporting.payoff_query)) == 1):
                            entrylines.extend(supporting.entry_links())
                    if len(entrylines) == len(payoff_list):
                        entrylines.append(new_entry)
                        AccountLink.create_link(entrylines)
                except LucteriosException:
                    pass


@Signal.decorate('checkparam')
def payoff_checkparam():
    Parameter.check_and_create(name='payoff-bankcharges-account', typeparam=0,
                               title=_("payoff-bankcharges-account"), args="{'Multi':False}", value='')
    Parameter.check_and_create(name='payoff-cash-account', typeparam=0, title=_("payoff-cash-account"), args="{'Multi':False}", value='531')
    Parameter.check_and_create(name='payoff-email-message', typeparam=0, title=_("payoff-email-message"),
                               args="{'Multi':True}", value=_('%(name)s\n\nJoint in this email %(doc)s.\n\nRegards'))
    check_payoff_accounting()
