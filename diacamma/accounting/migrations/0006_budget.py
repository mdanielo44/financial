# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-20 17:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_costaccounting_is_protected'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, verbose_name='account')),
                ('amount', models.FloatField(default=0, verbose_name='amount')),
            ],
            options={
                'ordering': ['code'],
                'verbose_name_plural': 'Budget lines',
                'verbose_name': 'Budget line',
            },
        ),
        migrations.AlterModelOptions(
            name='costaccounting',
            options={'default_permissions': [], 'ordering': ['name'], 'verbose_name': 'cost accounting', 'verbose_name_plural': 'costs accounting'},
        ),
        migrations.AlterModelOptions(
            name='entryaccount',
            options={'ordering': ['date_value'], 'verbose_name': 'entry of account', 'verbose_name_plural': 'entries of account'},
        ),
        migrations.AddField(
            model_name='budget',
            name='cost_accounting',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.CostAccounting', verbose_name='cost accounting'),
        ),
        migrations.AddField(
            model_name='budget',
            name='year',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.FiscalYear', verbose_name='fiscal year'),
        ),
    ]
