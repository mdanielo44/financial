# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from lucterios.CORE.models import Parameter


def initial_values(*args):
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
        name='invoice-cash-account', typeparam=0)
    param.title = _("invoice-cash-account")
    param.args = "{'Multi':False}"
    param.value = '531'
    param.save()

    param = Parameter.objects.create(
        name='invoice-bankcharges-account', typeparam=0)
    param.title = _("invoice-bankcharges-account")
    param.args = "{'Multi':False}"
    param.value = ''
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


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
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
                    verbose_name='reference', max_length=20)),
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
                                          on_delete=django.db.models.deletion.PROTECT, verbose_name='vat', default=None))
            ],
            options={
                'verbose_name_plural': 'articles',
                'verbose_name': 'article'
            },
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_type', models.IntegerField(null=False, default=0, db_index=True, verbose_name='bill type', choices=[
                 (0, 'quotation'), (1, 'bill'), (2, 'asset'), (3, 'receipt')])),
                ('num', models.IntegerField(
                    null=True, verbose_name='numeros')),
                ('date', models.DateField(null=False, verbose_name='date')),
                ('comment', models.TextField(
                    verbose_name='comment', null=True, default='')),
                ('status', models.IntegerField(verbose_name='status', db_index=True, default=0, choices=[
                 (0, 'building'), (1, 'valid'), (2, 'cancel'), (3, 'archive')])),
                ('cost_accounting', models.ForeignKey(to='accounting.CostAccounting', null=True,
                                                      on_delete=django.db.models.deletion.PROTECT, verbose_name='cost accounting', default=None)),
                ('entry', models.ForeignKey(to='accounting.EntryAccount', null=True,
                                            on_delete=django.db.models.deletion.PROTECT, verbose_name='entry', default=None)),
                ('fiscal_year', models.ForeignKey(to='accounting.FiscalYear', null=True,
                                                  on_delete=django.db.models.deletion.PROTECT, verbose_name='fiscal year', default=None)),
                ('third', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                            verbose_name='third', null=True, default=None, to='accounting.Third')),
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
                ('unit', models.CharField(
                    verbose_name='unit', default='', max_length=10)),
                ('quantity', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.99)], decimal_places=2, verbose_name='quantity', default=1.0, max_digits=10)),
                ('reduce', models.DecimalField(validators=[MinValueValidator(0.0), MaxValueValidator(
                    9999999.999)], decimal_places=3, verbose_name='reduce', default=0.0, max_digits=10)),
                ('article', models.ForeignKey(null=True, default=None, to='invoice.Article',
                                              on_delete=django.db.models.deletion.PROTECT, verbose_name='article')),
                ('bill', models.ForeignKey(
                    to='invoice.Bill', verbose_name='bill')),
            ],
            options={
                'verbose_name_plural': 'details',
                'default_permissions': [],
                'verbose_name': 'detail'
            },
        ),
        migrations.RunPython(initial_values),
    ]
