# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
'''
Initial django functions

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

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=50, verbose_name='code', unique=True)),
            ],
            options={
                'verbose_name': 'account',
                'default_permissions': [],
                'verbose_name_plural': 'accounts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Third',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('status', models.IntegerField(choices=[(0, 'Enabled'), (1, 'Disabled')])),
                ('contact', models.ForeignKey(verbose_name='contact', to='contacts.AbstractContact')),
            ],
            options={
                'verbose_name': 'third',
                'verbose_name_plural': 'thirds',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='account',
            name='third',
            field=models.ForeignKey(verbose_name='third', to='accounting.Third'),
            preserve_default=True,
        ),
    ]
