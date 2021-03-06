# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-06-03 13:14
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payoff', '0003_paymentmethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='date')),
                ('status', models.IntegerField(choices=[(0, 'failure'), (1, 'success')], db_index=True, default=0, verbose_name='status')),
                ('payer', models.CharField(max_length=200, verbose_name='payer')),
                ('amount', models.DecimalField(decimal_places=3, default=0.0, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(9999999.999)], verbose_name='amount')),
                ('contains', models.TextField(null=True, verbose_name='contains')),
            ],
            options={
                'verbose_name_plural': 'bank transactions',
                'default_permissions': ['change'],
                'ordering': ['-date'],
                'verbose_name': 'bank transaction',
            },
        ),
    ]
