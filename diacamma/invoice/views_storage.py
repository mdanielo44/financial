# -*- coding: utf-8 -*-
'''
Describe view for Django

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

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL,\
    ActionsManage, SELECT_SINGLE, SELECT_MULTI, CLOSE_YES, FORMTYPE_REFRESH, CLOSE_NO
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferDelete, XferShowEditor, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE, TITLE_EDIT,\
    XferTransition

from diacamma.invoice.models import StorageSheet, StorageDetail


MenuManage.add_sub("storage", "invoice", "diacamma.invoice/images/storage.png", _("Storage"), _("Manage of storage"), 10)


@MenuManage.describ('invoice.change_storagesheet', FORMTYPE_NOMODAL, 'storage', _('Management of storage sheet list'))
class StorageSheetList(XferListEditor):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'
    caption = _("Storage sheet")

    def fillresponse_header(self):
        status_filter = self.getparam('status', 0)
        type_filter = self.getparam('sheet_type', -1)
        self.fill_from_model(0, 1, False, ['status', 'sheet_type'])
        sel_status = self.get_components('status')
        sel_status.select_list.insert(0, (-1, '---'))
        sel_status.set_value(status_filter)
        sel_status.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        sel_type = self.get_components('sheet_type')
        sel_type.select_list.insert(0, (-1, '---'))
        sel_type.set_value(type_filter)
        sel_type.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.filter = Q()
        if status_filter != -1:
            self.filter &= Q(status=status_filter)
        if type_filter != -1:
            self.filter &= Q(sheet_type=type_filter)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES)
@MenuManage.describ('invoice.add_storagesheet')
class StorageSheetAddModify(XferAddEditor):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'
    caption_add = _("Add storage sheet")
    caption_modify = _("Modify storage sheet")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.change_storagesheet')
class StorageSheetShow(XferShowEditor):
    caption = _("Show storage sheet")
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_storagesheet')
class StorageSheetDel(XferDelete):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'
    caption = _("Delete storage sheet")


@ActionsManage.affect_transition("status")
@MenuManage.describ('invoice.add_bill')
class StorageSheetTransition(XferTransition):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.item.status == 0)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': int(xfer.item.status) == 0)
@MenuManage.describ('invoice.add_storagesheet')
class StorageDetailAddModify(XferAddEditor):
    icon = "storagesheet.png"
    model = StorageDetail
    field_id = 'storagedetail'
    caption_add = _("Add storage detail")
    caption_modify = _("Modify storage detail")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': int(xfer.item.status) == 0)
@MenuManage.describ('invoice.delete_storagesheet')
class StorageDetailDel(XferDelete):
    icon = "storagesheet.png"
    model = StorageDetail
    field_id = 'storagedetail'
    caption = _("Delete storage detail")
