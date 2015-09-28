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
from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir
from shutil import rmtree
from diacamma.invoice.views_conf import InvoiceConf, VatAddModify, VatDel
from diacamma.invoice.views import ArticleList, ArticleAddModify, ArticleDel


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
