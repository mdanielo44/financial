# -*- coding: utf-8 -*-
'''
diacamma.invoice views package

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

from lucterios.framework.xferadvance import XferAddEditor, XferListEditor,\
    XferSave
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import ActionsManage, MenuManage,\
    FORMTYPE_REFRESH, CLOSE_NO, FORMTYPE_MODAL, CLOSE_YES, SELECT_SINGLE,\
    WrapAction
from lucterios.framework.xfergraphic import XferContainerAcknowledge,\
    XferContainerCustom
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompEdit,\
    XferCompImage
from lucterios.framework.error import LucteriosException, MINOR
from lucterios.framework.models import get_value_if_choices

from diacamma.payoff.models import Payoff, Supporting, PaymentMethod
from diacamma.accounting.models import Third


@ActionsManage.affect('Payoff', 'edit', 'append')
@MenuManage.describ('payoff.add_payoff')
class PayoffAddModify(XferAddEditor):
    icon = "payoff.png"
    model = Payoff
    field_id = 'payoff'
    caption_add = _("Add payoff")
    caption_modify = _("Modify payoff")

    def fillresponse_multisave(self, supportings=(), amount=0.0, mode=0, payer='', reference='', bank_account=0, date=None):
        Payoff.multi_save(
            supportings, amount, mode, payer, reference, bank_account, date)

    def run_save(self, request, *args, **kwargs):
        supportings = self.getparam('supportings', ())
        if len(supportings) > 0:
            multisave = XferContainerAcknowledge()
            multisave.is_view_right = self.is_view_right
            multisave.locked = self.locked
            multisave.model = self.model
            multisave.field_id = self.field_id
            multisave.caption = self.caption
            multisave.closeaction = self.closeaction
            multisave.fillresponse = self.fillresponse_multisave
            return multisave.get(request, *args, **kwargs)
        else:
            return XferAddEditor.run_save(self, request, *args, **kwargs)


@ActionsManage.affect('Payoff', 'delete')
@MenuManage.describ('payoff.delete_payoff')
class PayoffDel(XferDelete):
    icon = "payoff.png"
    model = Payoff
    field_id = 'payoff'
    caption = _("Delete payoff")


@ActionsManage.affect('Supporting', 'third')
@MenuManage.describ('')
class SupportingThird(XferListEditor):
    icon = "diacamma.accounting/images/thirds.png"
    model = Third
    field_id = 'third'
    caption = _("Select third")

    def __init__(self, **kwargs):
        XferListEditor.__init__(self, **kwargs)
        self.action_list = []

    def fillresponse_header(self):
        contact_filter = self.getparam('filter', '')
        lbl = XferCompLabelForm('lbl_filtre')
        lbl.set_value_as_name(_('Filtrer by contact'))
        lbl.set_location(0, 2)
        self.add_component(lbl)
        comp = XferCompEdit('filter')
        comp.set_value(contact_filter)
        comp.set_action(self.request, self.get_action(),
                        {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        comp.set_location(1, 2)
        self.add_component(comp)
        self.filter = Q(status=0)
        if contact_filter != "":
            q_legalentity = Q(
                contact__legalentity__name__contains=contact_filter)
            q_individual = (Q(contact__individual__firstname__contains=contact_filter) | Q(
                contact__individual__lastname__contains=contact_filter))
            self.filter &= (q_legalentity | q_individual)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.add_action(self.request, SupportingThirdValid.get_action(
            _('select'), 'images/ok.png'), {'modal': FORMTYPE_MODAL, 'close': CLOSE_YES, 'unique': SELECT_SINGLE}, 0)


@MenuManage.describ('')
class SupportingThirdValid(XferSave):
    redirect_to_show = False
    icon = "diacamma.accounting/images/thirds.png"
    model = Supporting
    field_id = 'supporting'
    caption = _("Select third")


@ActionsManage.affect('Supporting', 'paymentmethod')
@MenuManage.describ(None)
class SupportingPaymentMethod(XferContainerCustom):
    caption = _("Payment")
    icon = "payments.png"
    model = Supporting
    field_id = 'Supporting'

    def fillresponse(self, item_name=''):
        if item_name != '':
            self.item = Supporting.objects.get(id=self.getparam(item_name, 0))
        self.item = self.item.get_final_child()
        payments = PaymentMethod.objects.all()
        if not self.item.payoff_have_payment() or (len(payments) == 0):
            raise LucteriosException(MINOR, _('No payment for this document.'))
        max_row = self.get_max_row() + 1
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, max_row, True, self.item.get_payment_fields())
        max_row = self.get_max_row() + 1
        lbl = XferCompLabelForm('lb_sep')
        lbl.set_value("{[hr/]}")
        lbl.set_location(1, max_row, 4)
        self.add_component(lbl)
        lbl = XferCompLabelForm('lb_title')
        lbl.set_value_as_infocenter(_("Payement methods"))
        lbl.set_location(1, max_row + 1, 4)
        self.add_component(lbl)
        for paymeth in payments:
            max_row = self.get_max_row() + 1
            lbl = XferCompLabelForm('lb_paymeth_%d' % paymeth.id)
            lbl.set_value_as_name(
                get_value_if_choices(paymeth.paytype, paymeth.get_field_by_name('paytype')))
            lbl.set_location(1, max_row)
            self.add_component(lbl)
            lbl = XferCompLabelForm('paymeth_%d' % paymeth.id)
            lbl.set_value(
                paymeth.show_pay(self.request.build_absolute_uri(), self.language, self.item))
            lbl.set_location(2, max_row, 3)
            self.add_component(lbl)
            lbl = XferCompLabelForm('sep_paymeth_%d' % paymeth.id)
            lbl.set_value("{[br/]}")
            lbl.set_location(2, max_row + 1)
            self.add_component(lbl)
        self.add_action(WrapAction(_('Close'), 'images/close.png'), {})


def get_html_payment(absolute_uri, lang, supporting):
    html_message = "<hr/>"
    html_message += "<center><i><u>%s</u></i></center>" % _(
        "Payement methods")
    html_message += "<table>"
    for paymeth in PaymentMethod.objects.all():
        html_message += "<tr>"
        html_message += "<td><b>%s</b></td>" % get_value_if_choices(
            paymeth.paytype, paymeth.get_field_by_name('paytype'))
        html_message += "<td>%s</td>" % paymeth.show_pay(absolute_uri, lang, supporting)
        html_message += "</tr>"
        html_message += "<tr></tr>"
    html_message += "</table>"
    return html_message


@MenuManage.describ(None)
class ValidationPaymentPaypal(XferContainerAcknowledge):
    pass
