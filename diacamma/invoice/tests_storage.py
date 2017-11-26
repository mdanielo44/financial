# -*- coding: utf-8 -*-
'''
diacamma.invoice tests package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2017 sd-libre.fr
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

from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir
from lucterios.framework.test import LucteriosTest

from diacamma.invoice.test_tools import InvoiceTest, default_area,\
    default_articles, insert_storage
from diacamma.accounting.test_tools import initial_thirds, default_compta
from diacamma.payoff.test_tools import default_bankaccount
from diacamma.invoice.views import ArticleShow, BillAddModify, DetailAddModify,\
    BillShow, BillTransition, ArticleList
from diacamma.invoice.views_storage import StorageSheetList,\
    StorageSheetAddModify, StorageSheetShow, StorageDetailAddModify,\
    StorageSheetTransition, StorageDetailImport, StorageDetailDel
from diacamma.payoff.views import SupportingThirdValid
from django.utils import six
from _io import StringIO


class StorageTest(InvoiceTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_bankaccount()
        rmtree(get_user_dir(), True)
        default_area()
        default_articles(with_storage=True)

    def test_receipt(self):
        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 10)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC3")

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "{[b]}0.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "{[b]}0.00€{[/b]}")
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 0)

        self.factory.xfer = StorageSheetList()
        self.call('/diacamma.invoice/storageSheetList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetList')
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/RECORD', 0)

        self.factory.xfer = StorageSheetAddModify()
        self.call('/diacamma.invoice/storageSheetAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)

        self.factory.xfer = StorageSheetAddModify()
        self.call('/diacamma.invoice/storageSheetAddModify',
                  {'sheet_type': 0, 'date': '2014-04-01', 'SAVE': 'YES', 'storagearea': 1, 'comment': "arrivage massif!"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageSheetAddModify')
        self.assert_attrib_equal("ACTION", "id", "diacamma.invoice/storageSheetShow")
        self.assert_count_equal("ACTION/PARAM", 1)
        self.assert_xml_equal("ACTION/PARAM[@name='storagesheet']", "1")

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="sheet_type"]', "réception de stock")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "en création")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="storagearea"]', "Lieu 1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/ACTIONS/ACTION', 4)

        self.factory.xfer = StorageDetailAddModify()
        self.call('/diacamma.invoice/storageDetailAddModify', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageDetailAddModify')
        self.assert_count_equal('COMPONENTS/*', 5)

        self.factory.xfer = StorageDetailAddModify()
        self.call('/diacamma.invoice/storageDetailAddModify', {'storagesheet': "1", 'SAVE': 'YES', "article": 1, "price": 7.25, "quantity": 10}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageDetailAddModify')

        self.factory.xfer = StorageDetailAddModify()
        self.call('/diacamma.invoice/storageDetailAddModify', {'storagesheet': "1", 'SAVE': 'YES', "article": 4, "price": 1.00, "quantity": 25}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageDetailAddModify')

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "en création")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="article"]', "ABC1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="price_txt"]', "7.25€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="quantity_txt"]', "10.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="article"]', "ABC4")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="price_txt"]', "1.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="quantity_txt"]', "25.00")

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 0)

        self.factory.xfer = StorageSheetTransition()
        self.call('/diacamma.invoice/storageSheetTransition',
                  {'CONFIRME': 'YES', 'storagesheet': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageSheetTransition')

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 10)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "validé")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 2)

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "Lieu 1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "10.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "72.50€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="qty"]', "{[b]}10.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="amount"]', "{[b]}72.50€{[/b]}")

        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.date"]', "1 avril 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.comment"]', "arrivage massif!")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="quantity"]', "10.00")

        self.factory.xfer = StorageSheetList()
        self.call('/diacamma.invoice/storageSheetList', {'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetList')
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/RECORD', 1)

    def test_exit(self):
        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 10)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC3")

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "{[b]}0.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "{[b]}0.00€{[/b]}")
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 0)

        self.factory.xfer = StorageSheetList()
        self.call('/diacamma.invoice/storageSheetList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetList')
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/RECORD', 0)

        self.factory.xfer = StorageSheetAddModify()
        self.call('/diacamma.invoice/storageSheetAddModify', {'sheet_type': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetAddModify')
        self.assert_count_equal('COMPONENTS/*', 5)

        self.factory.xfer = StorageSheetAddModify()
        self.call('/diacamma.invoice/storageSheetAddModify',
                  {'sheet_type': 1, 'date': '2014-04-01', 'SAVE': 'YES', 'storagearea': 1, 'comment': "casses!"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageSheetAddModify')
        self.assert_attrib_equal("ACTION", "id", "diacamma.invoice/storageSheetShow")
        self.assert_count_equal("ACTION/PARAM", 1)
        self.assert_xml_equal("ACTION/PARAM[@name='storagesheet']", "1")

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="sheet_type"]', "sortie de stock")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "en création")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="storagearea"]', "Lieu 1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/ACTIONS/ACTION', 3)

        self.factory.xfer = StorageDetailAddModify()
        self.call('/diacamma.invoice/storageDetailAddModify', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageDetailAddModify')
        self.assert_count_equal('COMPONENTS/*', 4)

        self.factory.xfer = StorageDetailAddModify()
        self.call('/diacamma.invoice/storageDetailAddModify', {'storagesheet': "1", 'SAVE': 'YES', "article": 1, "quantity": 7}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageDetailAddModify')

        self.factory.xfer = StorageDetailAddModify()
        self.call('/diacamma.invoice/storageDetailAddModify', {'storagesheet': "1", 'SAVE': 'YES', "article": 4, "quantity": 6}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageDetailAddModify')

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "en création")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="article"]', "ABC1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="quantity_txt"]', "7.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="article"]', "ABC4")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="quantity_txt"]', "6.00")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]',
                              "{[font color=\"red\"]}L'article ABC1 est en quantité insuffisante{[br/]}L'article ABC4 est en quantité insuffisante{[/font]}")

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 0)

        self.factory.xfer = StorageSheetTransition()
        self.call('/diacamma.invoice/storageSheetTransition',
                  {'CONFIRME': 'YES', 'storagesheet': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.exception', 'diacamma.invoice', 'storageSheetTransition')

        insert_storage()

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "Lieu 1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "10.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "50.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="area"]', "Lieu 2")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="qty"]', "5.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="amount"]', "20.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="qty"]', "{[b]}15.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="amount"]', "{[b]}70.00€{[/b]}")
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.date"]', "2 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.comment"]', "B")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="quantity"]', "5.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.date"]', "1 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.comment"]', "A")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="quantity"]', "10.00")

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "en création")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="article"]', "ABC1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="quantity_txt"]', "7.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="article"]', "ABC4")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="quantity_txt"]', "6.00")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}{[/font]}")

        self.factory.xfer = StorageSheetTransition()
        self.call('/diacamma.invoice/storageSheetTransition',
                  {'CONFIRME': 'YES', 'storagesheet': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageSheetTransition')

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "validé")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 2)

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "Lieu 1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "3.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "15.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="area"]', "Lieu 2")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="qty"]', "5.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="amount"]', "20.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="qty"]', "{[b]}8.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="amount"]', "{[b]}35.00€{[/b]}")
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.date"]', "1 avril 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.comment"]', "casses!")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="quantity"]', "-7.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.date"]', "2 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.comment"]', "B")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="quantity"]', "5.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[3]/VALUE[@name="storagesheet.date"]', "1 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[3]/VALUE[@name="storagesheet.comment"]', "A")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[3]/VALUE[@name="quantity"]', "10.00")

        self.factory.xfer = StorageSheetList()
        self.call('/diacamma.invoice/storageSheetList', {'status': -1, 'sheet_type': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetList')
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/RECORD', 1)

    def test_bill(self):
        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 10)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC3")

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "{[b]}0.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "{[b]}0.00€{[/b]}")
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 0)

        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': 1, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.call('/diacamma.payoff/supportingThirdValid',
                  {'supporting': 1, 'third': 6}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_count_equal('COMPONENTS/SELECT[@name="article"]/CASE', 4)

        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify', {'bill': 1, 'article': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/SELECT[@name="storagearea"]/CASE', 0)

        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 1, 'designation': 'article A', 'price': '1.11', 'quantity': 5, 'storagearea': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 2, 'designation': 'article B', 'price': '2.22', 'quantity': 5, 'storagearea': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify',
                  {'SAVE': 'YES', 'bill': 1, 'article': 3, 'designation': 'article C', 'price': '3.33', 'quantity': 5}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailAddModify')

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('COMPONENTS/GRID[@name="detail"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]',
                              "{[font color=\"red\"]}L'article ABC1 est en quantité insuffisante{[br/]}L'article ABC2 est en quantité insuffisante{[/font]}")

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 0)

        self.factory.xfer = BillTransition()
        self.call('/diacamma.invoice/billTransition',
                  {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.exception', 'diacamma.invoice', 'billTransition')

        insert_storage()

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "Lieu 1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "10.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "50.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="area"]', "Lieu 2")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="qty"]', "5.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="amount"]', "20.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="qty"]', "{[b]}15.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="amount"]', "{[b]}70.00€{[/b]}")
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.date"]', "2 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.comment"]', "B")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="quantity"]', "5.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.date"]', "1 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.comment"]', "A")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="quantity"]', "10.00")

        self.factory.xfer = DetailAddModify()
        self.call('/diacamma.invoice/detailAddModify', {'bill': 1, 'article': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/SELECT[@name="storagearea"]/CASE', 2)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="storagearea"]/CASE[@id="1"]', "Lieu 1 [10.0]")
        self.assert_xml_equal('COMPONENTS/SELECT[@name="storagearea"]/CASE[@id="2"]', "Lieu 2 [5.0]")

        self.factory.xfer = BillShow()
        self.call('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('COMPONENTS/GRID[@name="detail"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}{[/font]}")

        self.factory.xfer = BillTransition()
        self.call('/diacamma.invoice/billTransition',
                  {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billTransition')

        self.factory.xfer = ArticleShow()
        self.call('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="reference"]', "ABC1")
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storage"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="area"]', "Lieu 1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="qty"]', "5.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[1]/VALUE[@name="amount"]', "25.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="area"]', "Lieu 2")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="qty"]', "5.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[2]/VALUE[@name="amount"]', "20.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="area"]', "{[b]}Total{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="qty"]', "{[b]}10.0{[/b]}")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storage"]/RECORD[3]/VALUE[@name="amount"]', "{[b]}45.00€{[/b]}")
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="moving"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.date"]', "1 avril 2015")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="storagesheet.comment"]', "facture A-1 - 1 avril 2015")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[1]/VALUE[@name="quantity"]', "-5.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.date"]', "2 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="storagesheet.comment"]', "B")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[2]/VALUE[@name="quantity"]', "5.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[3]/VALUE[@name="storagesheet.date"]', "1 janvier 2014")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[3]/VALUE[@name="storagesheet.comment"]', "A")
        self.assert_xml_equal('COMPONENTS/GRID[@name="moving"]/RECORD[3]/VALUE[@name="quantity"]', "10.00")

        self.factory.xfer = StorageSheetList()
        self.call('/diacamma.invoice/storageSheetList', {'status': -1, 'sheet_type': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetList')
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/HEADER', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagesheet"]/RECORD', 2)

    def test_import(self):
        self.factory.xfer = ArticleList()
        self.call('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="article"]/HEADER', 8)
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/HEADER[@name="reference"]', "référence")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/HEADER[@name="stockage_total"]', "quantités")
        self.assert_count_equal('COMPONENTS/GRID[@name="article"]/RECORD', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="reference"]', "ABC1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="stockage_total"]', "0.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[2]/VALUE[@name="reference"]', "ABC2")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[2]/VALUE[@name="stockage_total"]', "0.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[3]/VALUE[@name="reference"]', "ABC3")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[3]/VALUE[@name="stockage_total"]', "---")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[4]/VALUE[@name="reference"]', "ABC4")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[4]/VALUE[@name="stockage_total"]', "0.0")

        csv_content = """'num','prix','qty'
'ABC1','1.11','10.00'
'ABC2','2.22','5.00'
'ABC3','3.33','25.00'
'ABC4','4.44','20.00'
'ABC5','5.55','15.00'
"""
        self.factory.xfer = StorageSheetAddModify()
        self.call('/diacamma.invoice/storageSheetAddModify',
                  {'sheet_type': 0, 'date': '2014-04-01', 'SAVE': 'YES', 'storagearea': 1, 'comment': "arrivage massif!"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageSheetAddModify')

        self.factory.xfer = StorageDetailImport()
        self.call('/diacamma.invoice/storageDetailImport', {'storagesheet': "1", 'step': 1, 'modelname': 'invoice.StorageDetail', 'quotechar': "'",
                                                            'delimiter': ',', 'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent': StringIO(csv_content)}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageDetailImport')
        self.assert_count_equal('COMPONENTS/*', 10)
        self.assert_count_equal('COMPONENTS/SELECT[@name="fld_article"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/SELECT[@name="fld_price"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/SELECT[@name="fld_quantity"]/CASE', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="CSV"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="CSV"]/RECORD', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="CSV"]/ACTIONS', 0)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_action_equal('ACTIONS/ACTION[1]', (six.text_type(
            'Retour'), 'images/left.png', 'diacamma.invoice', 'storageDetailImport', 0, 2, 1, {'step': '0'}))
        self.assert_action_equal('ACTIONS/ACTION[2]', (six.text_type(
            'Ok'), 'images/ok.png', 'diacamma.invoice', 'storageDetailImport', 0, 2, 1, {'step': '2'}))

        self.factory.xfer = StorageDetailImport()
        self.call('/diacamma.invoice/storageDetailImport', {'storagesheet': "1", 'step': 2, 'modelname': 'invoice.StorageDetail', 'quotechar': "'", 'delimiter': ',',
                                                            'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                            "fld_article": "num", "fld_price": "prix", "fld_quantity": "qty", }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageDetailImport')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="CSV"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="CSV"]/RECORD', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="CSV"]/ACTIONS', 0)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_action_equal('ACTIONS/ACTION[2]', (six.text_type(
            'Ok'), 'images/ok.png', 'diacamma.invoice', 'storageDetailImport', 0, 2, 1, {'step': '3'}))

        self.factory.xfer = StorageDetailImport()
        self.call('/diacamma.invoice/storageDetailImport', {'storagesheet': "1", 'step': 3, 'modelname': 'invoice.StorageDetail', 'quotechar': "'", 'delimiter': ',',
                                                            'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                            "fld_article": "num", "fld_price": "prix", "fld_quantity": "qty", }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageDetailImport')
        self.assert_count_equal('COMPONENTS/*', 2)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="result"]', "{[center]}{[i]}5 éléments ont été importés{[/i]}{[/center]}")
        self.assert_count_equal('ACTIONS/ACTION', 1)

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_count_equal('COMPONENTS/*', 11)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', "en création")
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/HEADER', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[1]/VALUE[@name="article"]', "ABC1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[2]/VALUE[@name="article"]', "ABC2")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[3]/VALUE[@name="article"]', "ABC3")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[4]/VALUE[@name="article"]', "ABC4")
        self.assert_xml_equal('COMPONENTS/GRID[@name="storagedetail"]/RECORD[5]/VALUE[@name="article"]', "ABC5")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]',
                              "{[font color=\"red\"]}L'article ABC3 est en non stockable{[br/]}L'article ABC5 est en non stockable{[/font]}")

        self.factory.xfer = StorageDetailDel()
        self.call('/diacamma.invoice/storageDetailDel', {'storagedetail': "3", 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageDetailDel')
        self.factory.xfer = StorageDetailDel()
        self.call('/diacamma.invoice/storageDetailDel', {'storagedetail': "5", 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageDetailDel')

        self.factory.xfer = StorageSheetShow()
        self.call('/diacamma.invoice/storageSheetShow', {'storagesheet': "1"}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageSheetShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}{[/font]}")

        self.factory.xfer = StorageSheetTransition()
        self.call('/diacamma.invoice/storageSheetTransition',
                  {'CONFIRME': 'YES', 'storagesheet': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageSheetTransition')

        self.factory.xfer = ArticleList()
        self.call('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="article"]/RECORD', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="reference"]', "ABC1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[1]/VALUE[@name="stockage_total"]', "10.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[2]/VALUE[@name="reference"]', "ABC2")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[2]/VALUE[@name="stockage_total"]', "5.0")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[3]/VALUE[@name="reference"]', "ABC3")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[3]/VALUE[@name="stockage_total"]', "---")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[4]/VALUE[@name="reference"]', "ABC4")
        self.assert_xml_equal('COMPONENTS/GRID[@name="article"]/RECORD[4]/VALUE[@name="stockage_total"]', "20.0")
