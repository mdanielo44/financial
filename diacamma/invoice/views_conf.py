# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from diacamma.invoice.models import Vat

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage


@ActionsManage.affect('Vat', 'list')
@MenuManage.describ('invoice.change_vat', FORMTYPE_NOMODAL, 'contact.conf', _('Management of parameters and configuration of invoice'))
class InvoiceConf(XferListEditor):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption = _("Invoice configuration")

    def fillresponse_header(self):
        self.new_tab(_('Parameters'))
        self.new_tab(_('VAT'))


@ActionsManage.affect('Vat', 'edit', 'add')
@MenuManage.describ('invoice.add_vat')
class VatAddModify(XferAddEditor):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption_add = _("Add VAT")
    caption_modify = _("Modify VAT")


@ActionsManage.affect('Vat', 'delete')
@MenuManage.describ('invoice.delete_vat')
class VatDel(XferDelete):
    icon = "invoice_conf.png"
    model = Vat
    field_id = 'vat'
    caption = _("Delete VAT")
