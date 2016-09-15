# -*- coding: utf-8 -*-
'''
diacamma.invoice models package

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
from re import match
from datetime import date

from django.db import models
from django.db.models.aggregates import Max
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django_fsm import FSMIntegerField, transition

from lucterios.framework.models import LucteriosModel, get_value_if_choices, \
    get_value_converted
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params

from diacamma.accounting.models import FiscalYear, Third, EntryAccount, \
    CostAccounting, Journal, EntryLineAccount, ChartsAccount, AccountThird
from diacamma.accounting.tools import current_system_account, format_devise, \
    currency_round, correct_accounting_code
from diacamma.payoff.models import Supporting


class Vat(LucteriosModel):
    name = models.CharField(_('name'), max_length=20)
    rate = models.DecimalField(_('rate'), max_digits=6, decimal_places=2,
                               default=10.0,
                               validators=[MinValueValidator(0.0),
                                           MaxValueValidator(100.0)])
    isactif = models.BooleanField(
        verbose_name=_('is actif'), default=True)

    def __str__(self):
        return six.text_type(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "rate", "isactif"]

    class Meta(object):
        verbose_name = _('VAT')
        verbose_name_plural = _('VATs')


class Article(LucteriosModel):
    reference = models.CharField(_('reference'), max_length=30)
    designation = models.TextField(_('designation'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=3,
                                default=0.0, validators=[MinValueValidator(0.0),
                                                         MaxValueValidator(9999999.999)])
    unit = models.CharField(_('unit'), null=True, default='', max_length=10)
    isdisabled = models.BooleanField(
        verbose_name=_('is disabled'), default=False)
    sell_account = models.CharField(_('sell account'), max_length=50)
    vat = models.ForeignKey(Vat, verbose_name=_('vat'), null=True,
                            default=None, on_delete=models.PROTECT)

    def __str__(self):
        return six.text_type(self.reference)

    @classmethod
    def get_default_fields(cls):
        return ["reference", "designation", (_('price'), "price_txt"), 'unit', "isdisabled", 'sell_account']

    @classmethod
    def get_edit_fields(cls):
        return ["reference", "designation", ("price", "unit"), ("sell_account", 'vat'), "isdisabled"]

    @classmethod
    def get_show_fields(cls):
        return ["reference", "designation", ("price", "unit"), ("sell_account", 'vat'), "isdisabled"]

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

    @property
    def ref_price(self):
        return "%s [%s]" % (self.reference, self.price_txt)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.sell_account = correct_accounting_code(self.sell_account)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('article')
        verbose_name_plural = _('articles')


class Bill(Supporting):
    fiscal_year = models.ForeignKey(
        FiscalYear, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    bill_type = models.IntegerField(verbose_name=_('bill type'),
                                    choices=((0, _('quotation')), (1, _('bill')), (2, _('asset')), (3, _('receipt'))), null=False, default=0, db_index=True)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    comment = models.TextField(_('comment'), null=False, default="")
    status = FSMIntegerField(verbose_name=_('status'),
                             choices=((0, _('building')), (1, _('valid')), (2, _('cancel')), (3, _('archive'))), null=False, default=0, db_index=True)
    entry = models.ForeignKey(
        EntryAccount, verbose_name=_('entry'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    cost_accounting = models.ForeignKey(
        CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    def __str__(self):
        billtype = get_value_if_choices(
            self.bill_type, self.get_field_by_name('bill_type'))
        if self.num is None:
            return "%s - %s" % (billtype, get_value_converted(self.date))
        else:
            return "%s %s - %s" % (billtype, self.num_txt, get_value_converted(self.date))

    @classmethod
    def get_default_fields(cls, status=-1):
        fields = ["bill_type", (_('numeros'), "num_txt"),
                  "date", "third", "comment", (_('total'), 'total')]
        if status == -1:
            fields.append("status")
        elif status == 1:
            fields.append(Supporting.get_payoff_fields()[-1][-1])
        return fields

    @classmethod
    def get_payment_fields(cls):
        return ["third", ("bill_type", (_('numeros'), "num_txt"),), ("date", (_('total'), 'total'),)]

    def get_third_mask(self):
        return current_system_account().get_customer_mask()

    @classmethod
    def get_edit_fields(cls):
        return ["bill_type", "cost_accounting", "date", "comment"]

    @classmethod
    def get_search_fields(cls):
        search_fields = [
            "bill_type", "fiscal_year", "num", "date", "comment", "status"]
        for fieldname in Third.get_search_fields():
            search_fields.append("third." + fieldname)
        for det_field in ["article.reference", "article.designation", "article.sell_account", "article.vat", "designation", "price", "unit", "quantity"]:
            search_fields.append("detail_set." + det_field)
        return search_fields

    @classmethod
    def get_show_fields(cls):
        return [((_('numeros'), "num_txt"), "date"), "third", "detail_set", "comment", "cost_accounting", ("status", (_('total'), 'total_excltax'))]

    @classmethod
    def get_print_fields(cls):
        print_fields = [
            (_("bill type"), "type_bill"), (_('numeros'), "num_txt"), "date", "third", "detail_set"]
        print_fields.extend(Supporting.get_print_fields())
        print_fields.extend(
            ["comment", "status", (_('total'), 'total_excltax'), (_('VTA sum'), 'vta_sum'), (_('total incl. taxes'), 'total_incltax')])
        print_fields.append('OUR_DETAIL')
        return print_fields

    @property
    def type_bill(self):
        return get_value_if_choices(self.bill_type, self.get_field_by_name("bill_type")).upper()

    @property
    def total(self):
        if Params.getvalue("invoice-vat-mode") == 2:
            return self.total_incltax
        else:
            return self.total_excltax

    def get_total_excltax(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_total_excltax()
        return val

    @property
    def total_excltax(self):
        return format_devise(self.get_total_excltax(), 5)

    def get_vta_sum(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_vta()
        return val

    def get_tax_sum(self):
        return self.get_vta_sum()

    @property
    def vta_sum(self):
        return format_devise(self.get_vta_sum(), 5)

    def get_total_incltax(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_total_incltax()
        return val

    def get_total(self):
        return self.get_total_incltax()

    @property
    def total_incltax(self):
        return format_devise(self.get_total_incltax(), 5)

    @property
    def num_txt(self):
        if (self.fiscal_year is None) or (self.num is None):
            return None
        else:
            return "%s-%d" % (self.fiscal_year.letter, self.num)

    def get_vta_details(self):
        vtas = {}
        for detail in self.detail_set.all():
            if abs(detail.vta_rate) > 0.001:
                vta_txt = "%.2f" % abs(float(detail.vta_rate) * 100.0)
                if vta_txt not in vtas.keys():
                    vtas[vta_txt] = float(0.0)
                vtas[vta_txt] += detail.get_vta()
        return vtas

    @property
    def title_vta_details(self):
        vtas = []
        for vta in self.get_vta_details().keys():
            vtas.append(_("VAT %s %%") % vta)
        return "{[br/]}".join(vtas)

    @property
    def vta_details(self):
        vtas = []
        for value in self.get_vta_details().values():
            vtas.append(format_devise(value, 5))
        return "{[br/]}".join(vtas)

    def payoff_is_revenu(self):
        return (self.bill_type != 0) and (self.bill_type != 2)

    def default_date(self):
        return self.date

    def entry_links(self):
        return [self.entry]

    def default_costaccounting(self):
        return self.cost_accounting

    def get_info_state(self):
        info = []
        if self.status == 0:
            info = Supporting.get_info_state(
                self, current_system_account().get_customer_mask())
        details = self.detail_set.all()
        if len(details) == 0:
            info.append(six.text_type(_("no detail")))
        else:
            for detail in details:
                if detail.article is not None:
                    detail_code = detail.article.sell_account
                else:
                    detail_code = Params.getvalue(
                        "invoice-default-sell-account")
                detail_account = None
                if match(current_system_account().get_revenue_mask(), detail_code) is not None:
                    try:
                        detail_account = ChartsAccount.get_account(
                            detail_code, FiscalYear.get_current())
                    except LucteriosException:
                        break
                if detail_account is None:
                    info.append(
                        six.text_type(_("article has code account unknown!")))
                    break
        try:
            info.extend(self.check_date(self.date.isoformat()))
        except LucteriosException:
            pass
        return "{[br/]}".join(info)

    def can_delete(self):
        if self.status != 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    def generate_entry(self):
        if self.bill_type == 2:
            is_bill = -1
        else:
            is_bill = 1
        third_account = self.get_third_account(
            current_system_account().get_customer_mask(), self.fiscal_year)
        self.entry = EntryAccount.objects.create(
            year=self.fiscal_year, date_value=self.date, designation=self.__str__(),
            journal=Journal.objects.get(id=3), costaccounting=self.cost_accounting)
        EntryLineAccount.objects.create(
            account=third_account, amount=is_bill * self.get_total_incltax(), third=self.third, entry=self.entry)
        remise_total = 0
        detail_list = {}
        for detail in self.detail_set.all():
            if detail.article is not None:
                detail_code = detail.article.sell_account
            else:
                detail_code = Params.getvalue("invoice-default-sell-account")
            detail_account = ChartsAccount.get_account(
                detail_code, self.fiscal_year)
            if detail_account is None:
                raise LucteriosException(
                    IMPORTANT, _("article has code account unknown!"))
            if detail_account.id not in detail_list.keys():
                detail_list[detail_account.id] = [detail_account, 0]
            detail_list[detail_account.id][
                1] += detail.get_total_excltax() + detail.get_reduce_excltax()
            remise_total += detail.get_reduce_excltax()
        if remise_total > 0.001:
            remise_code = Params.getvalue("invoice-reduce-account")
            remise_account = ChartsAccount.get_account(
                remise_code, self.fiscal_year)
            if remise_account is None:
                raise LucteriosException(
                    IMPORTANT, _("reduce-account is not defined!"))
            EntryLineAccount.objects.create(
                account=remise_account, amount=-1 * is_bill * remise_total, entry=self.entry)
        for detail_item in detail_list.values():
            EntryLineAccount.objects.create(
                account=detail_item[0], amount=is_bill * detail_item[1], entry=self.entry)
        if self.get_vta_sum() > 0.001:
            vta_code = Params.getvalue("invoice-vatsell-account")
            vta_account = ChartsAccount.get_account(
                vta_code, self.fiscal_year)
            if vta_account is None:
                raise LucteriosException(
                    IMPORTANT, _("vta-account is not defined!"))
            EntryLineAccount.objects.create(
                account=vta_account, amount=is_bill * self.get_vta_sum(), entry=self.entry)
        no_change, debit_rest, credit_rest = self.entry.serial_control(
            self.entry.get_serial())
        if not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
            raise LucteriosException(
                GRAVE, _("Error in accounting generator!") + "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest))

    transitionname__valid = _("Validate")

    @transition(field=status, source=0, target=1, conditions=[lambda item:item.get_info_state() == ''])
    def valid(self):
        self.fiscal_year = FiscalYear.get_current()
        bill_list = Bill.objects.filter(Q(bill_type=self.bill_type) & Q(fiscal_year=self.fiscal_year)).exclude(status=0)
        val = bill_list.aggregate(Max('num'))
        if val['num__max'] is None:
            self.num = 1
        else:
            self.num = val['num__max'] + 1
        self.status = 1
        if self.bill_type != 0:
            self.generate_entry()
        self.save()
        Signal.call_signal("change_bill", 'valid', self, None)

    transitionname__archive = _("Archive")

    @transition(field=status, source=1, target=3)
    def archive(self):
        self.status = 3
        self.save()
        Signal.call_signal("change_bill", 'archive', self, None)

    transitionname__cancel = _("Cancel")

    @transition(field=status, source=1, target=2, conditions=[lambda item:item.bill_type != 2])
    def cancel(self):
        new_asset = None
        if (self.bill_type in (1, 3)):
            new_asset = Bill.objects.create(
                bill_type=2, date=date.today(), third=self.third, status=0, cost_accounting=self.cost_accounting)
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_asset
                detail.save()
            self.status = 2
            self.save()
            Signal.call_signal("change_bill", 'cancel', self, new_asset)
        if new_asset is not None:
            return new_asset.id
        else:
            return None

    def convert_to_bill(self):
        if (self.status == 1) and (self.bill_type == 0):
            new_bill = Bill.objects.create(
                bill_type=1, date=date.today(), third=self.third, status=0, comment=self.comment)
            cost_accountings = CostAccounting.objects.filter(
                Q(status=0) & Q(is_default=True))
            if len(cost_accountings) >= 1:
                new_bill.cost_accounting = cost_accountings[0]
                new_bill.save()
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_bill
                detail.save()
            self.status = 3
            self.save()
            Signal.call_signal("change_bill", 'convert', self, new_bill)
            return new_bill
        else:
            return None

    def get_statistics_customer(self):
        cust_list = []
        if self.fiscal_year is not None:
            total_cust = 0
            costumers = {}
            for bill in Bill.objects.filter(Q(fiscal_year=self.fiscal_year) & Q(
                    bill_type__in=(1, 2, 3)) & Q(status__in=(1, 3))):
                if bill.third_id not in costumers.keys():
                    costumers[bill.third_id] = 0
                if bill.bill_type == 2:
                    costumers[bill.third_id] -= bill.get_total_excltax()
                    total_cust -= bill.get_total_excltax()
                else:
                    costumers[bill.third_id] += bill.get_total_excltax()
                    total_cust += bill.get_total_excltax()
            for cust_id in costumers.keys():
                cust_list.append((six.text_type(Third.objects.get(id=cust_id)),
                                  format_devise(costumers[cust_id], 5),
                                  "%.2f %%" % (100 * costumers[cust_id] / total_cust), costumers[cust_id]))
            cust_list.sort(
                key=lambda cust_item: (-1 * cust_item[3], cust_item[0]))
            cust_list.append(("{[b]}%s{[/b]}" % _('total'), "{[b]}%s{[/b]}" % format_devise(total_cust, 5),
                              "{[b]}%.2f %%{[/b]}" % 100, total_cust))
        return cust_list

    def get_statistics_article(self):
        art_list = []
        if self.fiscal_year is not None:
            total_art = 0
            articles = {}
            for det in Detail.objects.filter(Q(bill__fiscal_year=self.fiscal_year) & Q(
                    bill__bill_type__in=(1, 2, 3)) & Q(bill__status__in=(1, 3))):
                if det.article_id not in articles.keys():
                    articles[det.article_id] = [0, 0]
                if det.bill.bill_type == 2:
                    articles[det.article_id][0] -= det.get_total_excltax()
                    articles[det.article_id][1] -= float(det.quantity)
                    total_art -= det.get_total_excltax()
                else:
                    articles[det.article_id][0] += det.get_total_excltax()
                    articles[det.article_id][1] += float(det.quantity)
                    total_art += det.get_total_excltax()
            for art_id in articles.keys():
                if art_id is None:
                    art_text = "---"
                else:
                    art_text = six.text_type(Article.objects.get(id=art_id))
                if abs(articles[art_id][1]) > 0.0001:
                    art_list.append((art_text,
                                     format_devise(articles[art_id][0], 5),
                                     "%.2f" % articles[art_id][1],
                                     format_devise(
                                         articles[art_id][0] / articles[art_id][1], 5),
                                     "%.2f %%" % (100 * articles[art_id][0] / total_art), articles[art_id][0]))
            art_list.sort(key=lambda art_item: art_item[5], reverse=True)
            art_list.append(("{[b]}%s{[/b]}" % _('total'), "{[b]}%s{[/b]}" % format_devise(total_art, 5),
                             "{[b]}---{[/b]}", "{[b]}---{[/b]}",
                             "{[b]}%.2f %%{[/b]}" % 100, total_art))
        return art_list

    def support_validated(self, validate_date):
        if (self.bill_type == 2) or (self.status != 1):
            raise LucteriosException(
                IMPORTANT, _("This item can't be validated!"))
        if (self.bill_type == 0):
            new_bill = self.convert_to_bill()
            new_bill.date = validate_date
            new_bill.save()
            if (new_bill is None) or (new_bill.get_info_state() != ''):
                raise LucteriosException(
                    IMPORTANT, _("This item can't be validated!"))
            new_bill.valid()
        else:
            new_bill = self
        return new_bill

    def get_tax(self):
        return currency_round(self.get_tax_sum() * self.get_total_rest_topay() / self.get_total_incltax())

    def get_payable_without_tax(self):
        return self.get_total_rest_topay() - self.get_tax()

    def payoff_have_payment(self):
        return (self.bill_type != 2) and (self.status == 1) and (self.get_total_rest_topay() > 0.001)

    def get_document_filename(self):
        billtype = get_value_if_choices(
            self.bill_type, self.get_field_by_name('bill_type'))
        return "%s_%s_%s" % (billtype, self.num_txt, six.text_type(self.third))

    class Meta(object):
        verbose_name = _('bill')
        verbose_name_plural = _('bills')
        ordering = ['-date', 'status']


class Detail(LucteriosModel):
    bill = models.ForeignKey(
        Bill, verbose_name=_('bill'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, verbose_name=_('article'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    unit = models.CharField(
        verbose_name=_('unit'), null=True, default='', max_length=10)
    quantity = models.DecimalField(verbose_name=_('quantity'), max_digits=10, decimal_places=2, default=1.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.99)])
    reduce = models.DecimalField(verbose_name=_('reduce'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    vta_rate = models.DecimalField(_('vta rate'), max_digits=6, decimal_places=4, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return "[%s] %s:%f" % (six.text_type(self.reference), six.text_type(self.designation), self.price_txt)

    @classmethod
    def get_default_fields(cls):
        return ["article", "designation", (_('price'), "price_txt"), "unit", "quantity", (_('reduce'), "reduce_txt"), (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ["article", "designation", "price", "unit", "quantity", "reduce"]

    @classmethod
    def get_show_fields(cls):
        return ["article", "designation", (_('price'), "price_txt"), "unit", "quantity", (_('reduce'), "reduce_txt")]

    @classmethod
    def create_for_bill(cls, bill, article, qty=1):
        newdetail = cls(
            bill=bill, article=article, designation=article.designation, price=article.price, unit=article.unit, quantity=qty)
        newdetail.editor.before_save(None)
        newdetail.save()
        return newdetail

    def get_price(self):
        if (Params.getvalue("invoice-vat-mode") == 2) and (self.vta_rate > 0.001):
            return currency_round(self.price * self.vta_rate)
        if (Params.getvalue("invoice-vat-mode") == 1) and (self.vta_rate < -0.001):
            return currency_round(self.price * -1 * self.vta_rate / (1 - self.vta_rate))
        return float(self.price)

    def get_reduce(self):
        if (Params.getvalue("invoice-vat-mode") == 2) and (self.vta_rate > 0.001):
            return currency_round(self.reduce * self.vta_rate)
        if (Params.getvalue("invoice-vat-mode") == 1) and (self.vta_rate < -0.001):
            return currency_round(self.reduce * -1 * self.vta_rate / (1 - self.vta_rate))
        return float(self.reduce)

    @property
    def price_txt(self):
        return format_devise(self.get_price(), 5)

    @property
    def reduce_txt(self):
        if self.reduce > 0.0001:
            return "%s(%.2f%%)" % (format_devise(self.get_reduce(), 5), 100 * self.get_reduce() / (self.get_price() * float(self.quantity)))
        else:
            return None

    @property
    def total(self):
        if Params.getvalue("invoice-vat-mode") == 2:
            return self.total_incltax
        elif Params.getvalue("invoice-vat-mode") == 1:
            return self.total_excltax
        else:
            return format_devise(self.get_total(), 5)

    def get_total(self):
        return currency_round(self.price * self.quantity - self.reduce)

    def get_total_excltax(self):
        if self.vta_rate < -0.001:
            return self.get_total() - self.get_vta()
        else:
            return self.get_total()

    def get_reduce_vat(self):
        if self.vta_rate < -0.001:
            return currency_round(self.reduce * -1 * self.vta_rate / (1 - self.vta_rate))
        elif self.vta_rate > 0.001:
            return currency_round(self.reduce * self.vta_rate)
        else:
            return 0

    def get_reduce_excltax(self):
        if self.vta_rate < -0.001:
            return currency_round(self.reduce) - self.get_reduce_vat()
        else:
            return currency_round(self.reduce)

    @property
    def total_excltax(self):
        return format_devise(self.get_total_excltax(), 5)

    def get_total_incltax(self):
        if self.vta_rate > 0.001:
            return self.get_total() + self.get_vta()
        else:
            return self.get_total()

    @property
    def total_incltax(self):
        return format_devise(self.get_total_incltax(), 5)

    def get_vta(self):
        val = 0
        if self.vta_rate > 0.001:
            val = currency_round(self.price * self.quantity * self.vta_rate)
        elif self.vta_rate < -0.001:
            val = currency_round(
                self.price * self.quantity * -1 * self.vta_rate / (1 - self.vta_rate))
        val -= self.get_reduce_vat()
        return val

    @property
    def price_vta(self):
        return format_devise(self.get_vta(), 5)

    class Meta(object):
        verbose_name = _('detail')
        verbose_name_plural = _('details')
        default_permissions = []


def get_or_create_customer(contact_id):
    try:
        third = Third.objects.get(contact_id=contact_id)
    except ObjectDoesNotExist:
        third = Third.objects.create(
            contact_id=contact_id, status=0)
        AccountThird.objects.create(
            third=third, code=Params.getvalue("invoice-account-third"))
    return third


@Signal.decorate('checkparam')
def invoice_checkparam():
    Parameter.check_and_create(name='invoice-default-sell-account', typeparam=0,
                               title=_("invoice-default-sell-account"), args="{'Multi':False}", value='706')
    Parameter.check_and_create(name='invoice-reduce-account', typeparam=0, title=_("invoice-reduce-account"),
                               args="{'Multi':False}", value='709')
    Parameter.check_and_create(name='invoice-vatsell-account', typeparam=0, title=_("invoice-vatsell-account"),
                               args="{'Multi':False}", value='4455')
    Parameter.check_and_create(name='invoice-vat-mode', typeparam=4, title=_("invoice-vat-mode"),
                               args="{'Enum':3}", value='0', param_titles=(_("invoice-vat-mode.0"), _("invoice-vat-mode.1"), _("invoice-vat-mode.2")))
    Parameter.check_and_create(name="invoice-account-third", typeparam=0, title=_("invoice-account-third"),
                               args="{'Multi':False}", value='411')
