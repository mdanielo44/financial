# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.translation import ugettext_lazy as _
import django.core.validators
import django.db.models.deletion

from lucterios.CORE.models import Parameter


def initial_values(*args):
    param = Parameter.objects.create(
        name='payoff-bankcharges-account', typeparam=0)
    param.title = _("payoff-bankcharges-account")
    param.args = "{'Multi':False}"
    param.value = ''
    param.save()

    param = Parameter.objects.create(
        name='payoff-cash-account', typeparam=0)
    param.title = _("payoff-cash-account")
    param.args = "{'Multi':False}"
    param.value = '531'
    param.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supporting',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('fiscal_year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                                  null=True, to='accounting.FiscalYear', default=None, verbose_name='fiscal year')),
                ('third', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                            null=True, to='accounting.Third', default=None, verbose_name='third')),
            ],
            options={
                'verbose_name_plural': 'supporting',
                'verbose_name': 'supporting',
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('designation', models.TextField(verbose_name='designation')),
                ('reference', models.CharField(
                    max_length=200, verbose_name='reference')),
                ('account_code', models.CharField(
                    max_length=50, verbose_name='account code')),
            ],
            options={
                'verbose_name_plural': 'bank accounts',
                'verbose_name': 'bank account',
            },
        ),
        migrations.CreateModel(
            name='Payoff',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('supporting', models.ForeignKey(
                    to='payoff.Supporting', verbose_name='supporting')),
                ('date', models.DateField(verbose_name='date')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10, validators=[django.core.validators.MinValueValidator(
                    0.0), django.core.validators.MaxValueValidator(9999999.999)], verbose_name='amount', default=0.0)),
                ('mode', models.IntegerField(choices=[(0, 'cash'), (1, 'cheque'), (2, 'transfer'), (
                    3, 'crédit card'), (4, 'other')], default=0, verbose_name='mode', db_index=True)),
                ('payer', models.CharField(
                    verbose_name='payer', max_length=150, null=True, default='')),
                ('reference', models.CharField(
                    verbose_name='reference', max_length=100, null=True, default='')),
                ('entry', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                            to='accounting.EntryAccount', default=None, verbose_name='entry')),
                ('bank_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT,
                                                   to='payoff.BankAccount', default=None, verbose_name='bank account')),
            ],
            options={
                'verbose_name_plural': 'payoffs',
                'verbose_name': 'payoff',
            },
        ),
        migrations.RunPython(initial_values),
    ]
