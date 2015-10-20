# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


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
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                            null=True, to='accounting.EntryAccount', default=None, verbose_name='entry')),
            ],
            options={
                'verbose_name_plural': 'payoffs',
                'verbose_name': 'payoff',
            },
        ),
    ]
