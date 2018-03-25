# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import deletion
from django.utils import translation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

from lucterios.CORE.models import PrintModel


def print_values(*args):
    translation.activate(settings.LANGUAGE_CODE)
    PrintModel().load_model('diacamma.invoice', "Article_0001", is_default=True)


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0011_automaticreduce'),
    ]

    operations = [
        migrations.RunPython(print_values),
    ]
