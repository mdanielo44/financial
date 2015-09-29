# -*- coding: utf-8 -*-
'''
diacamma.invoice tests package

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
from shutil import rmtree

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir


from diacamma.invoice.views_conf import InvoiceConf, VatAddModify, VatDel
from diacamma.invoice.views import ArticleList, ArticleAddModify, ArticleDel,\
    BillList, BillAddModify, BillShow, BillThirdValid, BillThird,\
    DetailAddModify, DetailDel, BillValid
from diacamma.accounting.test_tools import initial_thirds, default_compta
from diacamma.invoice.test_tools import default_articles
from diacamma.accounting.views_entries import EntryLineAccountList


class ConfigTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        rmtree(get_user_dir(), True)

    def test_vat(self):
        self.factory.xfer = InvoiceConf()
        self.call('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assert_count_equal('COMPONENTS/TAB', 2)
        self.assert_count_equal('COMPONENTS/*', 2 + 2 + 13 + 2)

        self.assert_count_equal(
            'COMPONENTS/GRID[@name="vat"]/HEADER', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="vat"]/HEADER[@name="name"]', "nom")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="vat"]/HEADER[@name="rate"]', "taux")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="vat"]/HEADER[@name="isactif"]', "actif?")
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="vat"]/RECORD', 0)

        self.factory.xfer = VatAddModify()
        self.call('/diacamma.invoice/vatAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'vatAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)

        self.factory.xfer = VatAddModify()
        self.call('/diacamma.invoice/vatAddModify',
                  {'name': 'my vat', 'rate': '11.57', 'isactif': 1, 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'vatAddModify')

        self.factory.xfer = InvoiceConf()
        self.call('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="vat"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="vat"]/RECORD[1]/VALUE[@name="name"]', 'my vat')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="vat"]/RECORD[1]/VALUE[@name="rate"]', '11.57')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="vat"]/RECORD[1]/VALUE[@name="isactif"]', '1')

        self.factory.xfer = VatDel()
        self.call(
            '/diacamma.invoice/vatDel', {'vat': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'vatDel')

        self.factory.xfer = InvoiceConf()
        self.call('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="vat"]/RECORD', 0)

    def test_article(self):
        self.factory.xfer = ArticleList()
        self.call('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('COMPONENTS/*', 6)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="article"]/HEADER', 6)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/HEADER[@name="reference"]', "référence")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/HEADER[@name="designation"]', "désignation")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/HEADER[@name="price_txt"]', "prix")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/HEADER[@name="unit"]', "unité")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/HEADER[@name="isdisabled"]', "désactivé?")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/HEADER[@name="sell_account"]', "compte de vente")
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD', 0)

        self.factory.xfer = ArticleAddModify()
        self.call('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('COMPONENTS/*', 15)

        self.factory.xfer = ArticleAddModify()
        self.call('/diacamma.invoice/articleAddModify',
                  {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'sell_account': '705', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleList()
        self.call('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="reference"]', "ABC001")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="designation"]', "My beautiful article")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="price_txt"]', "43.72€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="unit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="isdisabled"]', "0")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="sell_account"]', "705")

        self.factory.xfer = ArticleDel()
        self.call('/diacamma.invoice/articleDel',
                  {'article': '1', 'CONFIRME': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'articleDel')

        self.factory.xfer = ArticleList()
        self.call('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('COMPONENTS/GRID[@name="article"]/RECORD', 0)


class BillTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_articles()
        rmtree(get_user_dir(), True)

    def test_add_bill(self):
        self.factory.xfer = BillList()
        self.call('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('COMPONENTS/GRID[@name="bill"]/RECORD', 0)

        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_count_equal('COMPONENTS/SELECT[@name="bill_type"]/CASE', 4)

        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': 1, 'date': '2014-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.assert_attrib_equal(
            "ACTION", "id", "diacamma.invoice/billShow")
        self.assert_count_equal("ACTION/PARAM", 1)
        self.assert_xml_equal("ACTION/PARAM[@name='bill']", "1")
        self.assert_count_equal("CONTEXT/*", 2)

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_count_equal('COMPONENTS/*', 18)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="title"]', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="num_txt"]', "---")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="status"]', "en création")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="date"]', "1 avril 2014")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}sans tiers selectionné{[br/]}pas de détail{[br/]}la date n'est pas incluse dans l'exercice{[/font]}")

        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill': 1, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}sans tiers selectionné{[br/]}pas de détail{[/font]}")

        self.factory.xfer = BillThird()
        self.call('/diacamma.invoice/billThird',
                  {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billThird')
        self.assert_count_equal('COMPONENTS/GRID[@name="third"]/RECORD', 7)

        self.factory.xfer = BillThirdValid()
        self.call('/diacamma.invoice/billThirdValid',
                  {'bill': 1, 'third': 6}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billThirdValid')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}pas de détail{[/font]}")

        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('COMPONENTS/*', 13)

        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 1, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('COMPONENTS/*', 19)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="date"]', "1 avril 2015")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="third"]', "Dalton Jack")
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="detail"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total"]', "87.44€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}{[/font]}")
        self.assert_count_equal('ACTIONS/ACTION', 3)

        self.factory.xfer = BillList()
        self.call('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('COMPONENTS/GRID[@name="bill"]/RECORD', 1)

    def test_add_bill_bad(self):
        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': 1, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.factory.xfer = BillThirdValid()
        self.call('/diacamma.invoice/billThirdValid',
                  {'bill': 1, 'third': 6}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billThirdValid')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}pas de détail{[/font]}")

        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 4, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="detail"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}un article a un compte inconnu!{[/font]}")

        self.factory.xfer = DetailDel()
        self.call('/diacamma.invoice/detailDel',
                  {'CONFIRME': 'YES', 'bill': 1, 'detail': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailDel')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 3, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="detail"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}un article a un compte inconnu!{[/font]}")

        self.factory.xfer = DetailDel()
        self.call('/diacamma.invoice/detailDel',
                  {'CONFIRME': 'YES', 'bill': 1, 'detail': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailDel')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 2, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = BillThirdValid()
        self.call('/diacamma.invoice/billThirdValid',
                  {'bill': 1, 'third': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billThirdValid')
        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="detail"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}le tiers n'a pas de compte client{[/font]}")

    def test_compta_bill(self):
        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': 1, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.factory.xfer = BillThirdValid()
        self.call('/diacamma.invoice/billThirdValid',
                  {'bill': 1, 'third': 6}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billThirdValid')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 1, 'designation': 'article 1', 'price': '22.50', 'quantity': 3, 'reduce': '5.0'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 2, 'designation': 'article 2', 'price': '3.25', 'quantity': 7}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 0, 'designation': 'article 3', 'price': '11.10', 'quantity': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total"]', "107.45€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}{[/font]}")
        self.assert_count_equal('ACTIONS/ACTION', 3)

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 0)

        self.factory.xfer = BillValid()
        self.call('/diacamma.invoice/billValid',
                  {'CONFIRME': 'YES', 'bill': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="num_txt"]', "A-1")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="status"]', "validé")

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 5)

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[411 Dalton Jack]')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.designation"]', 'facture A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="debit"]', '107.45€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', '---')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[709] 709')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.designation"]', 'facture A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="debit"]', '5.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="credit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', '---')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry_account"]', '[701] 701')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.designation"]', 'facture A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="debit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="credit"]', '67.50€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[3]/VALUE[@name="entry.link"]', '---')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry_account"]', '[706] 706')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.designation"]', 'facture A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="debit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="credit"]', '22.20€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[4]/VALUE[@name="entry.link"]', '---')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry_account"]', '[707] 707')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.designation"]', 'facture A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="debit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="credit"]', '22.75€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[5]/VALUE[@name="entry.link"]', '---')

    def test_add_quotation(self):
        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': 0, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.factory.xfer = BillThirdValid()
        self.call('/diacamma.invoice/billThirdValid',
                  {'bill': 1, 'third': 6}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billThirdValid')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 1, 'designation': 'article 1', 'price': '22.50', 'quantity': 3, 'reduce': '5.0'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')

        self.factory.xfer = BillValid()
        self.call('/diacamma.invoice/billValid',
                  {'CONFIRME': 'YES', 'bill': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="num_txt"]', "A-1")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="status"]', "validé")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="title"]', "{[br/]}{[center]}{[u]}{[b]}devis{[/b]}{[/u]}{[/center]}")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="date"]', "1 avril 2015")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total"]', "62.50€")

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 0)

    def test_compta_asset(self):
        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': 2, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.factory.xfer = BillThirdValid()
        self.call('/diacamma.invoice/billThirdValid',
                  {'bill': 1, 'third': 6}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billThirdValid')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 0, 'designation': 'article A', 'price': '22.20', 'quantity': 3}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 0, 'designation': 'article B', 'price': '11.10', 'quantity': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 0)

        self.factory.xfer = BillValid()
        self.call('/diacamma.invoice/billValid',
                  {'CONFIRME': 'YES', 'bill': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="title"]', "{[br/]}{[center]}{[u]}{[b]}avoir{[/b]}{[/u]}{[/center]}")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total"]', "88.80€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="num_txt"]', "A-1")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="status"]', "validé")

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 2)

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[411 Dalton Jack]')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.designation"]', 'avoir A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="debit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', "88.80€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', '---')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[706] 706')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.designation"]', 'avoir A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="debit"]', "88.80€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="credit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', '---')

    def test_compta_receive(self):
        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': 3, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.factory.xfer = BillThirdValid()
        self.call('/diacamma.invoice/billThirdValid',
                  {'bill': 1, 'third': 6}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billThirdValid')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 2, 'designation': 'article', 'price': '25.00', 'quantity': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'detailAddModify')

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 0)

        self.factory.xfer = BillValid()
        self.call('/diacamma.invoice/billValid',
                  {'CONFIRME': 'YES', 'bill': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('COMPONENTS/*', 16)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total"]', "25.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="num_txt"]', "A-1")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="status"]', "validé")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="title"]', "{[br/]}{[center]}{[u]}{[b]}reçu{[/b]}{[/u]}{[/center]}")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="date"]', "1 avril 2015")

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 2)

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry_account"]', '[411 Dalton Jack]')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.designation"]', 'reçu A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="debit"]', '25.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="credit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[1]/VALUE[@name="entry.link"]', '---')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.num"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_entry"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.date_value"]', '1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry_account"]', '[707] 707')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.designation"]', 'reçu A-1 - 1 avril 2015')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="debit"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="credit"]', '25.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD[2]/VALUE[@name="entry.link"]', '---')
