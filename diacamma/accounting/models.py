# -*- coding: utf-8 -*-
'''
Describe database model for Django

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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.models import LucteriosModel
from lucterios.contacts.models import AbstractContact # pylint: disable=no-name-in-module,import-error
from lucterios.framework.tools import ActionsManage
from django.utils import six

class Third(LucteriosModel):
    contact = models.ForeignKey('contacts.AbstractContact', verbose_name=_('contact'), null=False)
    status = models.IntegerField(choices=((0, _('Enabled')), (1, _('Disabled'))))

    @classmethod
    def get_default_fields(cls):
        return ["contact", "account_set"]

    @classmethod
    def get_edit_fields(cls):
        return ["status"]

    @classmethod
    def get_show_fields(cls):
        return {'':['contact'], _('001@Account information'):["status", "account_set"]}

    @classmethod
    def get_search_fields(cls):
        result = []
        for field_name in AbstractContact.get_search_fields():
            if not isinstance(field_name, tuple):
                result.append("contact." + field_name)

        result.extend(["status", "account_set.code"])
        return result

    def show(self, xfer):
        from lucterios.framework.xfercomponents import XferCompButton
        from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_NO
        xfer.tab = 0
        old_item = xfer.item
        xfer.item = self.contact.get_final_child() # pylint: disable=no-member
        xfer.filltab_from_model(1, 1, True, ['address', ('postal_code', 'city'), 'country', ('tel1', 'tel2')])
        btn = XferCompButton('show')
        btn.set_location(2, 5, 3, 1)
        modal_name = xfer.item.__class__.__name__
        btn.set_action(xfer.request, ActionsManage.get_act_changed(modal_name, 'show', _('Show'), 'images/edit.png'), \
                {'modal':FORMTYPE_MODAL, 'close':CLOSE_NO, 'params':{modal_name.lower():six.text_type(xfer.item.id)}})
        xfer.add_component(btn)
        xfer.item = old_item

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('third')
        verbose_name_plural = _('thirds')

class Account(LucteriosModel):
    third = models.ForeignKey(Third, verbose_name=_('third'), null=False)
    code = models.CharField(_('code'), max_length=50, unique=True)

    def __str__(self):
        return self.code

    @classmethod
    def get_default_fields(cls):
        return ["code"]

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        default_permissions = []

# class FiscalYear(LucteriosModel):
#    pass
