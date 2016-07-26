# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-26 15:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_third_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelentry',
            name='costaccounting',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounting.CostAccounting', verbose_name='cost accounting'),
        ),
    ]
