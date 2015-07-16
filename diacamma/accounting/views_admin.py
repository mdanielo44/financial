# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from diacamma.accounting.models import FiscalYear

from lucterios.framework.xferadvance import XferListEditor, XferDelete
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.tools import FORMTYPE_MODAL, ActionsManage, MenuManage, \
    SELECT_SINGLE, CLOSE_NO
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.framework.xfercomponents import XferCompButton

@ActionsManage.affect('FiscalYear', 'list')
@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_MODAL, 'contact.conf', _('Management of fiscal year and financial parameters'))
class Configuration(XferListEditor):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Accounting configuration")

    def fillresponse_header(self):
        self.new_tab(_('Fiscal year list'))

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.add_action(self.request, FiscalYearActive.get_action(), {'unique':SELECT_SINGLE, 'close':CLOSE_NO})
        self.new_tab(_('Parameters'))
        self.params['params'] = ['accounting-devise', 'accounting-devise-iso', 'accounting-devise-prec']
        Params.fill(self, self.params['params'], 1, 1)
        btn = XferCompButton('editparam')
        btn.set_location(1, self.get_max_row() + 1, 2, 1)
        btn.set_action(self.request, ParamEdit.get_action(_('Modify'), 'images/edit.png'), {'close':0})
        self.add_component(btn)

@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearActive(XferContainerAcknowledge):
    icon = "images/ok.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Activate")

    def fillresponse(self):
        all_year = FiscalYear.objects.all() # pylint: disable=no-member
        for year_item in all_year:
            year_item.is_actif = False
            year_item.save()
        self.item.is_actif = True
        self.item.save()

@ActionsManage.affect('FiscalYear', 'edit', 'modify', 'add')
@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearAddModify(XferAddEditor):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption_add = _("Add fiscal year")
    caption_modify = _("Modify fiscal year")

@ActionsManage.affect('FiscalYear', 'delete')
@MenuManage.describ('accounting.delete_fiscalyear')
class FiscalYearDel(XferDelete):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Delete fiscal year")
