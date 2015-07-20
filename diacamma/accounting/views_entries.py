# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from diacamma.accounting.models import EntryLineAccount, EntryAccount

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage

@ActionsManage.affect('EntryLineAccount', 'list')
@MenuManage.describ('accounting.change_entryaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Edition of accounting entry for current fiscal year'), )
class EntryLineAccountList(XferListEditor):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("accounting entries")

@ActionsManage.affect('EntryLineAccount', 'edit', 'modify', 'add')
@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountAddModify(XferAddEditor):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption_add = _("Add entry line of account")
    caption_modify = _("Modify accounting entry")

@ActionsManage.affect('EntryLineAccount', 'show')
@MenuManage.describ('accounting.change_entryaccount')
class EntryLineAccountShow(XferShowEditor):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("Show accounting entry")

@ActionsManage.affect('EntryLineAccount', 'delete')
@MenuManage.describ('accounting.delete_entryaccount')
class EntryLineAccountDel(XferDelete):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("Delete accounting entry")

@ActionsManage.affect('EntryAccount', 'edit')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountAddModify(XferAddEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption_add = _("Add entry of account")
    caption_modify = _("Modify accounting entry")

@ActionsManage.affect('EntryAccount', 'show')
@MenuManage.describ('accounting.change_entryaccount')
class EntryAccountShow(XferShowEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Show accounting entry")
