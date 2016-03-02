# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import deletion
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from lucterios.CORE.models import Parameter, PrintModel
from diacamma.invoice.models import Bill


def initial_values(*args):
    translation.activate(settings.LANGUAGE_CODE)

    param = Parameter.objects.create(
        name='invoice-default-sell-account', typeparam=0)
    param.title = _("invoice-default-sell-account")
    param.args = "{'Multi':False}"
    param.value = '706'
    param.save()

    param = Parameter.objects.create(
        name='invoice-reduce-account', typeparam=0)
    param.title = _("invoice-reduce-account")
    param.args = "{'Multi':False}"
    param.value = '709'
    param.save()

    param = Parameter.objects.create(
        name='invoice-vatsell-account', typeparam=0)
    param.title = _("invoice-vatsell-account")
    param.args = "{'Multi':False}"
    param.value = '4455'
    param.save()

    param = Parameter.objects.create(
        name='invoice-vat-mode', typeparam=4)
    param.title = _("invoice-vat-mode")
    param.param_titles = (_("invoice-vat-mode.0"),
                          _("invoice-vat-mode.1"), _("invoice-vat-mode.2"))
    param.args = "{'Enum':3}"
    param.value = '0'
    param.save()

    param = Parameter.objects.create(
        name="invoice-account-third", typeparam=0)
    param.title = _("invoice-account-third")
    param.args = "{'Multi':False}"
    param.value = '411'
    param.save()

    prtmdl = PrintModel.objects.create(
        name=_("bill"), kind=2, modelname=Bill.get_long_name())
    prtmdl.value = """
<model hmargin="10.0" vmargin="10.0" page_width="210.0" page_height="297.0">
<header extent="25.0">
<text height="20.0" width="120.0" top="5.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="20" font_family="sans-serif" font_weight="" font_size="20">
{[b]}#OUR_DETAIL.name{[/b]}
</text>
<image height="25.0" width="30.0" top="0.0" left="10.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
#OUR_DETAIL.image
</image>
</header>
<bottom extent="10.0">
<text height="10.0" width="190.0" top="00.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="8" font_family="sans-serif" font_weight="" font_size="8">
{[italic]}
#OUR_DETAIL.address - #OUR_DETAIL.postal_code #OUR_DETAIL.city - #OUR_DETAIL.tel1 #OUR_DETAIL.tel2 #OUR_DETAIL.email{[br/]}#OUR_DETAIL.identify_number
{[/italic]}
</text>
</bottom>
<body>
<text height="8.0" width="190.0" top="0.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="15" font_family="sans-serif" font_weight="" font_size="15">
{[b]}#type_bill #num_txt{[/b]}
</text>
<text height="8.0" width="190.0" top="8.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="13" font_family="sans-serif" font_weight="" font_size="13">
#date
</text>
<text height="20.0" width="100.0" top="25.0" left="80.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}#third.contact.str{[/b]}{[br/]}#third.contact.address{[br/]}#third.contact.postal_code #third.contact.city
</text>
<table height="100.0" width="190.0" top="55.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(article)s{[/b]}
    </columns>
    <columns width="90.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(designation)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(price)s{[/b]}
    </columns>
    <columns width="15.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(Qty)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(reduce)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(total)s{[/b]}
    </columns>
    <rows data="detail_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#article.reference
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#designation
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#price_txt
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#quantity #unit
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#reduce_txt
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#total
        </cell>
    </rows>
</table>
<text height="15.0" width="100.0" top="220.0" left="00.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[i]}#title_vta_details{[/i]}{[br/]}
{[i]}%(total VAT)s{[/i]}{[br/]}
{[i]}%(total excl. taxes)s{[/i]}{[br/]}
</text>
<text height="15.0" width="15.0" top="220.0" left="100.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
#vta_details{[br/]}
#vta_sum{[br/]}
#total_excltax{[br/]}
</text>
<text height="15.0" width="30.0" top="220.0" left="140.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[u]}{[b]}%(total incl. taxes)s{[/b]}{[/u]}{[br/]}
{[u]}{[b]}%(total payed)s{[/b]}{[/u]}{[br/]}
{[u]}{[b]}%(rest to pay)s{[/b]}{[/u]}{[br/]}
</text>
<text height="15.0" width="20.0" top="220.0" left="170.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[u]}#total_incltax{[/u]}{[br/]}
{[u]}#total_payed{[/u]}{[br/]}
{[u]}#total_rest_topay{[/u]}{[br/]}
</text>
<text height="20.0" width="100.0" top="220.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
#comment
</text>
</body>
</model>
""" % {
        'article': _('article'),
        'designation': _('designation'),
        'price': _('price'),
        'Qty': _('Qty'),
        'reduce': ('reduce'),
        'total': ('total'),
        'total VAT': _('total VAT'),
        'total excl. taxes': _('total excl. taxes'),
        'total incl. taxes': _('total incl. taxes'),
        'total payed': _('total payed'),
        'rest to pay': _('rest to pay')
    }
    prtmdl.save()

    prtmdl = PrintModel.objects.create(
        name=_("payoff"), kind=2, modelname=Bill.get_long_name())
    prtmdl.value = """
<model hmargin="10.0" vmargin="10.0" page_width="210.0" page_height="297.0">
<header extent="25.0">
<text height="20.0" width="120.0" top="5.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="20" font_family="sans-serif" font_weight="" font_size="20">
{[b]}#OUR_DETAIL.name{[/b]}
</text>
<image height="25.0" width="30.0" top="0.0" left="10.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
#OUR_DETAIL.image
</image>
</header>
<bottom extent="10.0">
<text height="10.0" width="190.0" top="00.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="8" font_family="sans-serif" font_weight="" font_size="8">
{[italic]}
#OUR_DETAIL.address - #OUR_DETAIL.postal_code #OUR_DETAIL.city - #OUR_DETAIL.tel1 #OUR_DETAIL.tel2 #OUR_DETAIL.email{[br/]}#OUR_DETAIL.identify_number
{[/italic]}
</text>
</bottom>
<body>
<text height="8.0" width="190.0" top="0.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="15" font_family="sans-serif" font_weight="" font_size="15">
{[b]}%(payoff)s #type_bill #num_txt{[/b]}
</text>
<text height="8.0" width="190.0" top="8.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="13" font_family="sans-serif" font_weight="" font_size="13">
#date
</text>
<text height="20.0" width="100.0" top="25.0" left="80.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}#third.contact.str{[/b]}{[br/]}#third.contact.address{[br/]}#third.contact.postal_code #third.contact.city
</text>
<table height="100.0" width="190.0" top="55.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(article)s{[/b]}
    </columns>
    <columns width="90.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(designation)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(price)s{[/b]}
    </columns>
    <columns width="15.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(Qty)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(reduce)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(total)s{[/b]}
    </columns>
    <rows data="detail_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#article.reference
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#designation
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#price_txt
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#quantity #unit
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#reduce_txt
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#total
        </cell>
    </rows>
</table>
<text height="7.0" width="190.0" top="155.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="10">
{[b]}{[u]}%(payoffs)s{[/u]}{[/b]}
</text>
<table height="60.0" width="160.0" top="165.0" left="15.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
    <columns width="35.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(date)s{[/b]}
    </columns>
    <columns width="40.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[bold]}%(mode)s{[/bold]}
    </columns>
    <columns width="60.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[bold]}%(reference)s{[/bold]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[bold]}%(value)s{[/bold]}
    </columns>
    <rows data="payoff_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
        #date
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
        #mode
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
        #reference
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
        #value
        </cell>
    </rows>
</table>
<text height="7.0" width="50.0" top="230.0" left="20.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[b]}%(total)s{[/b]}{[i]}#total_incltax{[/i]}
</text>
<text height="7.0" width="50.0" top="230.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[b]}%(total payed)s{[/b]}{[i]}#total_payed{[/i]}
</text>
<text height="7.0" width="50.0" top="230.0" left="120.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[b]}%(rest to pay)s{[/b]}{[i]}#total_rest_topay{[/i]}
</text>
</body>
</model>
""" % {
        'article': _('article'),
        'designation': _('designation'),
        'price': _('price'),
        'Qty': _('Qty'),
        'reduce': ('reduce'),
        'total': ('total'),
        'total payed': _('total payed'),
        'rest to pay': _('rest to pay'),
        'payoff': _('payoff'),
        'payoffs': _('payoffs'),
        'date': _('date'),
        'mode': _('mode'),
        'reference': _('reference'),
        'value': _('value'),
    }
    prtmdl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
        ('payoff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vat',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(verbose_name='name', max_length=20)),
                ('rate', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    100.0)], decimal_places=2, max_digits=6, verbose_name='rate', default=10.0)),
                ('isactif', models.BooleanField(
                    verbose_name='is actif', default=True)),
            ],
            options={
                'verbose_name_plural': 'VATs',
                'verbose_name': 'VAT'
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(
                    verbose_name='reference', max_length=30)),
                ('designation', models.TextField(verbose_name='designation')),
                ('price', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.999)], decimal_places=3, max_digits=10, verbose_name='price', default=0.0)),
                ('unit', models.CharField(
                    verbose_name='unit', null=True, default='', max_length=10)),
                ('isdisabled', models.BooleanField(
                    verbose_name='is disabled', default=False)),
                ('sell_account', models.CharField(
                    verbose_name='sell account', max_length=50)),
                ('vat', models.ForeignKey(to='invoice.Vat', null=True,
                                          on_delete=deletion.PROTECT, verbose_name='vat', default=None))
            ],
            options={
                'verbose_name_plural': 'articles',
                'verbose_name': 'article'
            },
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('supporting_ptr', models.OneToOneField(auto_created=True, parent_link=True,
                                                        serialize=False, primary_key=True, to='payoff.Supporting', on_delete=models.CASCADE)),
                ('fiscal_year', models.ForeignKey(on_delete=deletion.PROTECT,
                                                  null=True, to='accounting.FiscalYear', default=None, verbose_name='fiscal year')),
                ('bill_type', models.IntegerField(null=False, default=0, db_index=True, verbose_name='bill type', choices=[
                 (0, 'quotation'), (1, 'bill'), (2, 'asset'), (3, 'receipt')])),
                ('num', models.IntegerField(
                    null=True, verbose_name='numeros')),
                ('date', models.DateField(null=False, verbose_name='date')),
                ('comment', models.TextField(
                    verbose_name='comment', null=False, default='')),
                ('status', models.IntegerField(verbose_name='status', db_index=True, default=0, choices=[
                 (0, 'building'), (1, 'valid'), (2, 'cancel'), (3, 'archive')])),
                ('cost_accounting', models.ForeignKey(to='accounting.CostAccounting', null=True,
                                                      on_delete=deletion.PROTECT, verbose_name='cost accounting', default=None)),
                ('entry', models.ForeignKey(to='accounting.EntryAccount', null=True,
                                            on_delete=deletion.PROTECT, verbose_name='entry', default=None)),
            ],
            options={
                'verbose_name_plural': 'bills',
                'verbose_name': 'bill'
            },
        ),
        migrations.CreateModel(
            name='Detail',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.TextField(verbose_name='designation')),
                ('price', models.DecimalField(verbose_name='price', max_digits=10, default=0.0,
                                              decimal_places=3, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])),
                ('vta_rate', models.DecimalField(default=0.0, verbose_name='vta rate', decimal_places=4,
                                                 max_digits=6, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])),
                ('unit', models.CharField(
                    null=True, verbose_name='unit', default='', max_length=10)),
                ('quantity', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.99)], decimal_places=2, verbose_name='quantity', default=1.0, max_digits=10)),
                ('reduce', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.999)], decimal_places=3, verbose_name='reduce', default=0.0, max_digits=10)),
                ('article', models.ForeignKey(null=True, default=None, to='invoice.Article',
                                              on_delete=deletion.PROTECT, verbose_name='article')),
                ('bill', models.ForeignKey(
                    to='invoice.Bill', verbose_name='bill', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'details',
                'default_permissions': [],
                'verbose_name': 'detail'
            },
        ),
        migrations.RunPython(initial_values),
    ]
