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
from datetime import date
from base64 import b64decode
from _io import StringIO

from django.utils import formats, six

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ObjectMerge
from lucterios.mailing.tests import configSMTP, TestReceiver, decode_b64
from lucterios.contacts.models import CustomField

from diacamma.accounting.test_tools import initial_thirds, default_compta, default_costaccounting
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.payoff.views import PayoffAddModify, PayoffDel, SupportingThird, SupportingThirdValid, PayableEmail
from diacamma.payoff.test_tools import default_bankaccount
from diacamma.invoice.models import Article, Bill, AccountPosting
from diacamma.invoice.test_tools import default_articles, InvoiceTest, default_categories, default_customize, default_accountPosting
from diacamma.invoice.views_conf import InvoiceConf, VatAddModify, VatDel, CategoryAddModify, CategoryDel, ArticleImport, StorageAreaDel,\
    StorageAreaAddModify, AccountPostingAddModify, AccountPostingDel
from diacamma.invoice.views import ArticleList, ArticleAddModify, ArticleDel, \
    BillList, BillAddModify, BillShow, DetailAddModify, DetailDel, BillTransition, BillDel, BillFromQuotation, \
    BillStatistic, BillStatisticPrint, BillPrint, BillMultiPay, BillSearch, ArticleShow, ArticleSearch
from diacamma.accounting.models import CostAccounting


class ConfigTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        default_compta()
        rmtree(get_user_dir(), True)

    def test_vat(self):
        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assertTrue('__tab_6' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_7' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 5 + 5 + 2 + 2 + 2)

        self.assert_grid_equal('vat', {'name': "nom", 'rate': "taux", 'account': "compte de TVA", 'isactif': "actif ?"}, 0)

        self.factory.xfer = VatAddModify()
        self.calljson('/diacamma.invoice/vatAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'vatAddModify')
        self.assert_count_equal('', 5)

        self.factory.xfer = VatAddModify()
        self.calljson('/diacamma.invoice/vatAddModify',
                      {'name': 'my vat', 'rate': '11.57', 'account': '4455', 'isactif': 1, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'vatAddModify')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal('vat', 1)
        self.assert_json_equal('', 'vat/@0/name', 'my vat')
        self.assert_json_equal('', 'vat/@0/rate', '11.57')
        self.assert_json_equal('', 'vat/@0/account', '4455')
        self.assert_json_equal('', 'vat/@0/isactif', '1')

        self.factory.xfer = VatDel()
        self.calljson('/diacamma.invoice/vatDel', {'vat': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'vatDel')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal('vat', 0)

    def test_category(self):
        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assertTrue('__tab_6' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_7' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 5 + 5 + 2 + 2 + 2)

        self.assert_grid_equal('category', {'name': "nom", 'designation': "désignation"}, 0)

        self.factory.xfer = CategoryAddModify()
        self.calljson('/diacamma.invoice/categoryAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'categoryAddModify')
        self.assert_count_equal('', 3)

        self.factory.xfer = CategoryAddModify()
        self.calljson('/diacamma.invoice/categoryAddModify',
                      {'name': 'my category', 'designation': "bla bla bla", 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryAddModify')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal('category', 1)
        self.assert_json_equal('', 'category/@0/name', 'my category')
        self.assert_json_equal('', 'category/@0/designation', 'bla bla bla')

        self.factory.xfer = CategoryDel()
        self.calljson('/diacamma.invoice/categoryDel', {'category': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'categoryDel')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal('category', 0)

    def test_accountposting(self):
        default_costaccounting()
        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assert_grid_equal('accountposting', {'name': "nom", 'sell_account': "compte de vente", 'cost_accounting': 'comptabilité analytique'}, 0)

        self.factory.xfer = AccountPostingAddModify()
        self.calljson('/diacamma.invoice/accountPostingAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'accountPostingAddModify')
        self.assert_count_equal('', 4)
        self.assert_select_equal('sell_account', 3)
        self.assert_select_equal('cost_accounting', {0: None, 2: 'open'})

        self.factory.xfer = AccountPostingAddModify()
        self.calljson('/diacamma.invoice/accountPostingAddModify', {'name': 'aaa', 'sell_account': '601', 'cost_accounting': 2, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'accountPostingAddModify')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assert_count_equal('accountposting', 1)

        self.factory.xfer = AccountPostingDel()
        self.calljson('/diacamma.invoice/accountPostingDel', {'accountposting': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'accountPostingDel')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assert_count_equal('accountposting', 0)

    def test_customize(self):
        default_customize()
        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assertTrue('__tab_5' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 5 + 5 + 2 + 2 + 2)

        self.assert_grid_equal('custom_field', {'name': "nom", 'kind_txt': "type"}, 2)
        self.assert_json_equal('', 'custom_field/@0/name', 'couleur')
        self.assert_json_equal('', 'custom_field/@0/kind_txt', 'Sélection (---,noir,blanc,rouge,bleu,jaune)')
        self.assert_json_equal('', 'custom_field/@1/name', 'taille')
        self.assert_json_equal('', 'custom_field/@1/kind_txt', 'Entier [0;100]')

    def test_storagearea(self):
        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'invoiceConf')
        self.assertTrue('__tab_6' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_7' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('', 2 + 5 + 5 + 2 + 2 + 2)

        self.assert_grid_equal('storagearea', {'name': "nom", 'designation': "désignation"}, 0)

        self.factory.xfer = StorageAreaAddModify()
        self.calljson('/diacamma.invoice/storageAreaAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'storageAreaAddModify')
        self.assert_count_equal('', 3)

        self.factory.xfer = StorageAreaAddModify()
        self.calljson('/diacamma.invoice/storageAreaAddModify',
                      {'name': 'my category', 'designation': "bla bla bla", 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageAreaAddModify')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal('storagearea', 1)
        self.assert_json_equal('', 'storagearea/@0/name', 'my category')
        self.assert_json_equal('', 'storagearea/@0/designation', 'bla bla bla')

        self.factory.xfer = StorageAreaDel()
        self.calljson('/diacamma.invoice/storageAreaDel', {'storagearea': 1, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'storageAreaDel')

        self.factory.xfer = InvoiceConf()
        self.calljson('/diacamma.invoice/invoiceConf', {}, False)
        self.assert_count_equal('storagearea', 0)

    def test_article(self):
        default_accountPosting()
        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 6)
        self.assert_select_equal('stockable', 4)  # nb=4
        self.assert_grid_equal('article', {'reference': "référence", 'designation': "désignation", 'price_txt': "prix", 'unit': "unité", 'isdisabled': "désactivé ?", 'accountposting': "code d'imputation comptable", 'stockable': "stockable"}, 0)
        self.assert_count_equal('#article/actions', 3)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 11)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'accountposting': 4, 'stockable': '1', 'qtyDecimal': '1', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 1)
        self.assert_json_equal('', 'article/@0/reference', "ABC001")
        self.assert_json_equal('', 'article/@0/designation', "My beautiful article")
        self.assert_json_equal('', 'article/@0/price_txt', "43.72€")
        self.assert_json_equal('', 'article/@0/unit', '')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code4")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 14)
        self.assert_json_equal('', 'qtyDecimal', '1')

        self.factory.xfer = ArticleDel()
        self.calljson('/diacamma.invoice/articleDel',
                      {'article': '1', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleDel')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 0)

    def test_article_with_cat(self):
        default_categories()
        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_select_equal("cat_filter", 3, True)
        self.assert_grid_equal('article', {"reference": "référence", "designation": "désignation", "price_txt": "prix", "unit": "unité",
                                           "isdisabled": "désactivé ?", "accountposting": "code d'imputation comptable", "stockable": "stockable", "categories": "catégories"}, 0)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleAddModify')
        self.assert_count_equal('', 13)

        self.factory.xfer = ArticleAddModify()
        self.calljson('/diacamma.invoice/articleAddModify',
                      {'reference': 'ABC001', 'designation': 'My beautiful article', 'price': '43.72', 'sell_account': '705', 'stockable': '1', 'categories': '2;3', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'articleAddModify')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 15)
        self.assert_json_equal('', 'qtyDecimal', '0')

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 1)
        self.assert_json_equal('', 'article/@0/categories', "cat 2{[br/]}cat 3")

    def test_article_merge(self):
        default_categories()
        default_articles(with_storage=True)
        default_customize()
        initial_thirds()

        search_field_list = Article.get_search_fields()
        self.assertEqual(9 + 2 + 2 + 2, len(search_field_list), search_field_list)  # article + art custom + category + provider

        self.factory.xfer = ArticleSearch()
        self.calljson('/diacamma.invoice/articleSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleSearch')
        self.assert_count_equal('article', 5)
        self.assert_json_equal('', 'article/@0/reference', "ABC1")
        self.assert_json_equal('', 'article/@1/reference', "ABC2")
        self.assert_json_equal('', 'article/@2/reference', "ABC3")
        self.assert_json_equal('', 'article/@3/reference', "ABC4")
        self.assert_json_equal('', 'article/@4/reference', "ABC5")
        self.assert_json_equal('', 'article/@0/categories', "cat 1")
        self.assert_json_equal('', 'article/@1/categories', "cat 2")
        self.assert_json_equal('', 'article/@2/categories', "cat 2{[br/]}cat 3")
        self.assert_json_equal('', 'article/@3/categories', "cat 3")
        self.assert_json_equal('', 'article/@4/categories', "cat 1{[br/]}cat 2{[br/]}cat 3")
        self.assert_count_equal('#article/actions', 4)
        self.assert_action_equal('#article/actions/@3', ('Fusion', 'images/clone.png', 'CORE', 'objectMerge', 0, 1, 2,
                                                         {'modelname': 'invoice.Article', 'field_id': 'article'}))

        self.factory.xfer = ObjectMerge()
        self.calljson('/CORE/objectMerge', {'modelname': 'invoice.Article', 'field_id': 'article', 'article': '1;3;5'}, False)
        self.assert_observer('core.custom', 'CORE', 'objectMerge')
        self.assert_count_equal('mrg_object', 3)
        self.assert_json_equal('', 'mrg_object/@0/value', "ABC1")
        self.assert_json_equal('', 'mrg_object/@1/value', "ABC3")
        self.assert_json_equal('', 'mrg_object/@2/value', "ABC5")

        self.factory.xfer = ObjectMerge()
        self.calljson('/CORE/objectMerge', {'modelname': 'invoice.Article', 'field_id': 'article', 'article': '1;3;5', 'CONFIRME': 'YES', 'mrg_object': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'objectMerge')
        self.assert_action_equal(self.response_json['action'], ('Editer', 'images/show.png', 'diacamma.invoice', 'articleShow', 1, 1, 1, {'article': '3'}))

        self.factory.xfer = ArticleSearch()
        self.calljson('/diacamma.invoice/articleSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleSearch')
        self.assert_count_equal('article', 3)
        self.assert_json_equal('', 'article/@0/reference', "ABC2")
        self.assert_json_equal('', 'article/@1/reference', "ABC3")
        self.assert_json_equal('', 'article/@2/reference', "ABC4")
        self.assert_json_equal('', 'article/@0/categories', "cat 2")
        self.assert_json_equal('', 'article/@1/categories', "cat 1{[br/]}cat 2{[br/]}cat 3")
        self.assert_json_equal('', 'article/@2/categories', "cat 3")

    def test_article_filter(self):
        default_categories()
        default_articles(with_storage=True)
        default_customize()
        initial_thirds()

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 4)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 5)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 0}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'stockable': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 3)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '2;3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 2)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1, 'cat_filter': '1;2;3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('article', 1)

    def test_article_import1(self):
        initial_thirds()
        default_categories()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref'
'A123','article N°1','','Kg','code1','stockable','cat 2','Dalton Avrel','POIYT'
'B234','article N°2','23,56','L','code1','stockable','cat 3','',''
'C345','article N°3','45.74','','code2','non stockable','cat 1','Dalton Avrel','MLKJH'
'D456','article N°4','56,89','m','code1','stockable & non vendable','','Maximum','987654'
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','',''
'A123','article N°1','16,95','Kg','code1','stockable','','Maximum','654321'
"""

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 0)

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 1, 'modelname': 'invoice.Article', 'quotechar': "'",
                                                          'delimiter': ',', 'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent': StringIO(csv_content)}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 6 + 12)
        self.assert_select_equal('fld_reference', 9)  # nb=9
        self.assert_select_equal('fld_categories', 10)  # nb=10
        self.assert_count_equal('CSV', 6)
        self.assert_count_equal('#CSV/actions', 0)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Retour'), 'images/left.png', 'diacamma.invoice', 'articleImport', 0, 2, 1, {'step': '0'}))
        self.assert_action_equal(self.json_actions[1], (six.text_type('Ok'), 'images/ok.png', 'diacamma.invoice', 'articleImport', 0, 2, 1, {'step': '2'}))
        self.assertEqual(len(self.json_context), 8)

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 2, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 4)
        self.assert_count_equal('CSV', 6)
        self.assert_count_equal('#CSV/actions', 0)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_action_equal(self.json_actions[1], (six.text_type('Ok'), 'images/ok.png', 'diacamma.invoice', 'articleImport', 0, 2, 1, {'step': '3'}))

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price_txt', "16.95€")
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code1")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")
        self.assert_json_equal('', 'article/@0/categories', "cat 2{[br/]}cat 3")

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price_txt', "23.56€")
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/isdisabled', "0")
        self.assert_json_equal('', 'article/@1/accountposting', "code1")
        self.assert_json_equal('', 'article/@1/stockable', "stockable")
        self.assert_json_equal('', 'article/@1/categories', "cat 3")

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price_txt', "45.74€")
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/isdisabled', "0")
        self.assert_json_equal('', 'article/@2/accountposting', "code2")
        self.assert_json_equal('', 'article/@2/stockable', "non stockable")
        self.assert_json_equal('', 'article/@2/categories', "cat 1")

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price_txt', "56.89€")
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/isdisabled', "0")
        self.assert_json_equal('', 'article/@3/accountposting', "code1")
        self.assert_json_equal('', 'article/@3/stockable', "stockable & non vendable")
        self.assert_json_equal('', 'article/@3/categories', '')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 17)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', "cat 2{[br/]}cat 3")
        self.assert_count_equal('provider', 2)
        self.assert_json_equal('', 'provider/@0/third', "Dalton Avrel")
        self.assert_json_equal('', 'provider/@0/reference', "POIYT")
        self.assert_json_equal('', 'provider/@1/third', "Maximum")
        self.assert_json_equal('', 'provider/@1/reference', "654321")

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': 'categorie',
                                                          'fld_provider.third.contact': 'fournisseur', 'fld_provider.reference': 'ref', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 17)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', "cat 2{[br/]}cat 3")
        self.assert_count_equal('provider', 2)
        self.assert_json_equal('', 'provider/@0/third', "Dalton Avrel")
        self.assert_json_equal('', 'provider/@0/reference', "POIYT")
        self.assert_json_equal('', 'provider/@1/third', "Maximum")
        self.assert_json_equal('', 'provider/@1/reference', "654321")

    def test_article_import2(self):
        initial_thirds()
        default_categories()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref'
'A123','article N°1','ssdqs','Kg','code1','stockable','cat 2','Avrel','POIYT'
'B234','article N°2','23.56','L','code1','stockable','cat 3','',''
'C345','article N°3','45.74','','code2','non stockable','cat 1','Avrel','MLKJH'
'D456','article N°4','56.89','m','code1','stockable & non vendable','','Maximum','987654'
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','',''
'A123','article N°1','16.95','Kg','code1','stockable','','Maximum','654321'
"""

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?", 'fld_categories': '',
                                                          'fld_provider.third.contact': '', 'fld_provider.reference': '', }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price_txt', "16.95€")
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code1")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")
        self.assert_json_equal('', 'article/@0/categories', '')

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price_txt', "23.56€")
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/isdisabled', "0")
        self.assert_json_equal('', 'article/@1/accountposting', "code1")
        self.assert_json_equal('', 'article/@1/stockable', "stockable")
        self.assert_json_equal('', 'article/@1/categories', '')

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price_txt', "45.74€")
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/isdisabled', "0")
        self.assert_json_equal('', 'article/@2/accountposting', "code2")
        self.assert_json_equal('', 'article/@2/stockable', "non stockable")
        self.assert_json_equal('', 'article/@2/categories', '')

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price_txt', "56.89€")
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/isdisabled', "0")
        self.assert_json_equal('', 'article/@3/accountposting', "code1")
        self.assert_json_equal('', 'article/@3/stockable', "stockable & non vendable")
        self.assert_json_equal('', 'article/@3/categories', '')

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 17)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'categories', '')
        self.assert_count_equal('provider', 0)

    def test_article_import3(self):
        default_customize()
        default_accountPosting()
        csv_content = """'num','comment','prix','unité','compte','stock?','categorie','fournisseur','ref','color','size'
'A123','article N°1','12.45','Kg','code1','stockable','cat 2','Avrel','POIYT','---','10'
'B234','article N°2','23.56','L','code1','stockable','cat 3','','','noir','25'
'C345','article N°3','45.74','','code2','non stockable','cat 1','Avrel','MLKJH','rouge','75'
'D456','article N°4','56.89','m','code1','stockable & non vendable','','Maximum','987654','blanc','1'
'A123','article N°1','13.57','Kg','code1','stockable','cat 3','','','bleu','10'
'A123','article N°1','16.95','Kg','code1','stockable','','Maximum','654321','bleu','15'
"""

        self.factory.xfer = ArticleImport()
        self.calljson('/diacamma.invoice/articleImport', {'step': 3, 'modelname': 'invoice.Article', 'quotechar': "'", 'delimiter': ',',
                                                          'encoding': 'utf-8', 'dateformat': '%d/%m/%Y', 'csvcontent0': csv_content,
                                                          "fld_reference": "num", "fld_designation": "comment", "fld_price": "prix",
                                                          "fld_unit": "unité", "fld_isdisabled": "", "fld_accountposting": "compte",
                                                          "fld_vat": "", "fld_stockable": "stock?",
                                                          "fld_custom_1": "color", "fld_custom_2": "size", }, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleImport')
        self.assert_count_equal('', 2)
        self.assert_json_equal('LABELFORM', 'result', "{[center]}{[i]}4 éléments ont été importés{[/i]}{[/center]}")
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = ArticleList()
        self.calljson('/diacamma.invoice/articleList', {'show_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleList')
        self.assert_count_equal('article', 4)
        self.assert_json_equal('', 'article/@0/reference', "A123")
        self.assert_json_equal('', 'article/@0/designation', "article N°1")
        self.assert_json_equal('', 'article/@0/price_txt', "16.95€")
        self.assert_json_equal('', 'article/@0/unit', 'Kg')
        self.assert_json_equal('', 'article/@0/isdisabled', "0")
        self.assert_json_equal('', 'article/@0/accountposting', "code1")
        self.assert_json_equal('', 'article/@0/stockable', "stockable")

        self.assert_json_equal('', 'article/@1/reference', "B234")
        self.assert_json_equal('', 'article/@1/designation', "article N°2")
        self.assert_json_equal('', 'article/@1/price_txt', "23.56€")
        self.assert_json_equal('', 'article/@1/unit', 'L')
        self.assert_json_equal('', 'article/@1/isdisabled', "0")
        self.assert_json_equal('', 'article/@1/accountposting', "code1")
        self.assert_json_equal('', 'article/@1/stockable', "stockable")

        self.assert_json_equal('', 'article/@2/reference', "C345")
        self.assert_json_equal('', 'article/@2/designation', "article N°3")
        self.assert_json_equal('', 'article/@2/price_txt', "45.74€")
        self.assert_json_equal('', 'article/@2/unit', '')
        self.assert_json_equal('', 'article/@2/isdisabled', "0")
        self.assert_json_equal('', 'article/@2/accountposting', "code2")
        self.assert_json_equal('', 'article/@2/stockable', "non stockable")

        self.assert_json_equal('', 'article/@3/reference', "D456")
        self.assert_json_equal('', 'article/@3/designation', "article N°4")
        self.assert_json_equal('', 'article/@3/price_txt', "56.89€")
        self.assert_json_equal('', 'article/@3/unit', 'm')
        self.assert_json_equal('', 'article/@3/isdisabled', "0")
        self.assert_json_equal('', 'article/@3/accountposting', "code1")
        self.assert_json_equal('', 'article/@3/stockable', "stockable & non vendable")

        self.factory.xfer = ArticleShow()
        self.calljson('/diacamma.invoice/articleShow', {'article': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'articleShow')
        self.assert_count_equal('', 16)
        self.assert_json_equal('LABELFORM', 'reference', "A123")
        self.assert_json_equal('LABELFORM', 'custom_1', "bleu")
        self.assert_json_equal('LABELFORM', 'custom_2', "15")


class BillTest(InvoiceTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_bankaccount()
        rmtree(get_user_dir(), True)

    def test_add_bill(self):
        default_articles()
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_grid_equal('bill', {"bill_type": "type de facture", "num_txt": "N°", "date": "date", "third": "tiers", "comment": "commentaire", "total": "total", "status": "status"}, 0)  # nb=7

        self.factory.xfer = BillAddModify()
        self.calljson('/diacamma.invoice/billAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billAddModify')
        self.assert_count_equal('', 5)
        self.assert_select_equal('bill_type', 4)  # nb=4

        self.factory.xfer = BillAddModify()
        self.calljson('/diacamma.invoice/billAddModify', {'bill_type': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billAddModify')
        self.assert_count_equal('', 5)
        self.assert_select_equal('bill_type', 4)  # nb=4

        self.factory.xfer = BillAddModify()
        self.calljson('/diacamma.invoice/billAddModify',
                      {'bill_type': 1, 'date': '2014-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.assertEqual(self.response_json['action']['id'], "diacamma.invoice/billShow")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['bill'], 1)
        self.assertEqual(len(self.json_context), 2)

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_count_equal('', 11)
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'num_txt', "---")
        self.assert_json_equal('LABELFORM', 'status', "en création")
        self.assert_json_equal('LABELFORM', 'date', "1 avril 2014")
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}aucun tiers sélectionné{[br/]}pas de détail{[br/]}la date n'est pas incluse dans l'exercice{[/font]}")

        self.factory.xfer = BillAddModify()
        self.calljson('/diacamma.invoice/billAddModify',
                      {'bill': 1, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}aucun tiers sélectionné{[br/]}pas de détail{[/font]}")

        self.factory.xfer = SupportingThird()
        self.calljson('/diacamma.payoff/supportingThird', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'supportingThird')
        self.assert_count_equal('third', 7)

        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 1, 'third': 6}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}pas de détail{[/font]}")

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('', 7)
        self.assert_json_equal('FLOAT', 'quantity', 1.0)
        self.assert_json_equal('', '#quantity/min', 0.0)
        self.assert_json_equal('', '#quantity/max', 9999999.99)
        self.assert_json_equal('', '#quantity/prec', 3)

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify', {'bill': 1, 'article': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('', 8)
        self.assert_json_equal('FLOAT', 'quantity', 1.0)
        self.assert_json_equal('', '#quantity/min', 0.0)
        self.assert_json_equal('', '#quantity/max', 9999999.99)
        self.assert_json_equal('', '#quantity/prec', 3)

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify', {'bill': 1, 'article': 3}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('', 8)
        self.assert_json_equal('FLOAT', 'quantity', 1.0)
        self.assert_json_equal('', '#quantity/min', 0.0)
        self.assert_json_equal('', '#quantity/max', 9999999.99)
        self.assert_json_equal('', '#quantity/prec', 0)

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify',
                      {'SAVE': 'YES', 'bill': 1, 'article': 1, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('', 12)
        self.assert_json_equal('LABELFORM', 'date', "1 avril 2015")
        self.assert_json_equal('LINK', 'third', "Dalton Jack")
        self.assert_json_equal('', '#third/link', "mailto:Jack.Dalton@worldcompany.com")
        self.assert_count_equal('detail', 1)
        self.assert_json_equal('', 'detail/@0/article', 'ABC1')
        self.assert_json_equal('', 'detail/@0/designation', 'My article')
        self.assert_json_equal('', 'detail/@0/price_txt', '43.72€')
        self.assert_json_equal('', 'detail/@0/unit', '')
        self.assert_json_equal('', 'detail/@0/quantity', '2.000')
        self.assert_json_equal('', 'detail/@0/reduce_txt', '---')
        self.assert_json_equal('', 'detail/@0/total', '87.44€')

        self.assert_json_equal('LABELFORM', 'total_excltax', "87.44€")
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}{[/font]}")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'filter': 'Dalton Jack'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)

    def test_add_bill_with_filter(self):
        default_categories()
        default_articles(True)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)

        self.factory.xfer = BillAddModify()
        self.calljson('/diacamma.invoice/billAddModify',
                      {'bill_type': 1, 'date': '2014-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billAddModify')

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('', 12)
        self.assert_select_equal('article', 5)  # nb=5

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify', {'bill': 1, 'third': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('', 12)
        self.assert_select_equal('article', 2)  # nb=2

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify', {'bill': 1, 'reference': '34'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('', 12)
        self.assert_select_equal('article', 2)  # nb=2

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify', {'bill': 1, 'cat_filter': '2;3'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'detailAddModify')
        self.assert_count_equal('', 12)
        self.assert_select_equal('article', 1)  # nb=1

    def test_add_bill_bad(self):
        default_articles()
        self.factory.xfer = BillAddModify()
        self.calljson('/diacamma.invoice/billAddModify',
                      {'bill_type': 1, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid',
                      {'supporting': 1, 'third': 6}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}pas de détail{[/font]}")

        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify',
                      {'SAVE': 'YES', 'bill': 1, 'article': 4, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('detail', 1)
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}au moins un article a un compte inconnu !{[/font]}")

        self.factory.xfer = DetailDel()
        self.calljson('/diacamma.invoice/detailDel',
                      {'CONFIRME': 'YES', 'bill': 1, 'detail': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailDel')
        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify',
                      {'SAVE': 'YES', 'bill': 1, 'article': 3, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('detail', 1)
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}au moins un article a un compte inconnu !{[/font]}")

        self.factory.xfer = DetailDel()
        self.calljson('/diacamma.invoice/detailDel',
                      {'CONFIRME': 'YES', 'bill': 1, 'detail': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailDel')
        self.factory.xfer = DetailAddModify()
        self.calljson('/diacamma.invoice/detailAddModify',
                      {'SAVE': 'YES', 'bill': 1, 'article': 2, 'designation': 'My article', 'price': '43.72', 'quantity': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid',
                      {'supporting': 1, 'third': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('detail', 1)
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}Ce tiers n'a pas de compte correct !{[/font]}")

    def check_list_del_archive(self):
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': -1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.assert_count_equal('#bill/actions', 3)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)
        self.assert_count_equal('#bill/actions', 4)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.assert_count_equal('#bill/actions', 5)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)
        self.assert_count_equal('#bill/actions', 1)

        self.factory.xfer = BillDel()
        self.calljson(
            '/diacamma.invoice/billDel', {'CONFIRME': 'YES', 'bill': 1}, False)
        self.assert_observer('core.exception', 'diacamma.invoice', 'billDel')

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billArchive',
                      {'CONFIRME': 'YES', 'bill': 1, 'TRANSITION': 'archive'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billArchive')

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': -1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 3}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.assert_count_equal('#bill/actions', 2)

    def test_compta_valid_with_pay(self):
        default_articles()
        Parameter.change_value('payoff-bankcharges-account', '627')
        Params.clear()
        details = [{'article': 1, 'designation': 'article 1', 'price': '22.50', 'quantity': 3, 'reduce': '5.0'},
                   {'article': 2, 'designation': 'article 2',
                       'price': '3.25', 'quantity': 7},
                   {'article': 0, 'designation': 'article 3',
                       'price': '11.10', 'quantity': 2}]
        self._create_bill(details, 1, '2015-04-01', 6)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid', {'bill': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billValid')
        self.assert_count_equal('', 2 + 7 + 0)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid', {'bill': 1, 'TRANSITION': 'valid', 'mode': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billValid')
        self.assert_count_equal('', 2 + 9 + 0)

        configSMTP('localhost', 2025)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid', {'bill': 1, 'TRANSITION': 'valid', 'mode': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billValid')
        self.assert_count_equal('', 2 + 9 + 4)
        self.assert_json_equal('', 'withpayoff', False)
        self.assert_json_equal('', 'amount', '107.45')
        self.assert_json_equal('', 'sendemail', False)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid', {'bill': 1, 'TRANSITION': 'valid', 'CONFIRME': 'YES',
                                                      'withpayoff': True, 'mode': 1, 'amount': '107.45', 'date_payoff': '2015-04-07', 'mode': 1, 'reference': 'abc123', 'bank_account': 1, 'payer': "Ma'a Dalton", 'bank_fee': '1.08',
                                                      'sendemail': True, 'subject': 'my bill', 'message': 'this is a bill.', 'model': 8}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')
        self.assert_action_equal(self.response_json['action'], ("", None, "diacamma.payoff", "payableEmail", 1, 1, 1))

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5 + 3)

        self.assert_json_equal('', 'entryline/@5/entry.num', '---')
        self.assert_json_equal('', 'entryline/@5/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@5/entry.date_value', '2015-04-07')
        self.assert_json_equal('', 'entryline/@5/designation_ref', 'règlement de facture - 1 avril 2015')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[411 Dalton Jack]')
        self.assert_json_equal('', 'entryline/@5/credit', '{[font color="green"]}107.45€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@6/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@6/debit', '{[font color="blue"]}106.37€{[/font]}')
        self.assert_json_equal('', 'entryline/@6/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[627] 627')
        self.assert_json_equal('', 'entryline/@7/debit', '{[font color="blue"]}1.08€{[/font]}')
        self.assert_json_equal('', 'entryline/@7/costaccounting', '---')

    def test_compta_bill(self):
        default_articles()
        CostAccounting.objects.create(name='new', description='New cost', status=0)
        post1 = AccountPosting.objects.get(id=1)
        post1.cost_accounting_id = 2
        post1.save()
        post2 = AccountPosting.objects.get(id=2)
        post2.cost_accounting_id = 3
        post2.save()

        details = [{'article': 1, 'designation': 'article 1', 'price': '22.50', 'quantity': 3, 'reduce': '5.0'},
                   {'article': 2, 'designation': 'article 2', 'price': '3.25', 'quantity': 7},
                   {'article': 0, 'designation': 'article 3', 'price': '11.10', 'quantity': 2}]
        self._create_bill(details, 1, '2015-04-01', 6)

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_attrib_equal('total_excltax', 'description', "total")
        self.assert_json_equal('LABELFORM', 'total_excltax', "107.45€")
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}{[/font]}")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid',
                      {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('', 13)
        self.assert_json_equal('LABELFORM', 'num_txt', "A-1")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assertEqual(len(self.json_actions), 4)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5)

        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-04-01')
        self.assert_json_equal('', 'entryline/@0/designation_ref', 'facture A-1 - 1 avril 2015')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[411 Dalton Jack]')
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}107.45€{[/font]}')
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[701] 701')
        self.assert_json_equal('', 'entryline/@1/credit', '{[font color="green"]}67.50€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/costaccounting', 'open')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[706] 706')
        self.assert_json_equal('', 'entryline/@2/credit', '{[font color="green"]}22.20€{[/font]}')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@3/credit', '{[font color="green"]}22.75€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/costaccounting', 'new')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[709] 709')
        self.assert_json_equal('', 'entryline/@4/debit', '{[font color="blue"]}5.00€{[/font]}')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'open')

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': -1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billCancel',
                      {'CONFIRME': 'YES', 'bill': 1, 'TRANSITION': 'cancel'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billCancel')
        self.assertEqual(self.response_json['action']['id'], "diacamma.invoice/billShow")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['bill'], 2)

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': -1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('', 12)
        self.assert_json_equal('LABELFORM', 'total_excltax', "107.45€")
        self.assert_json_equal('LABELFORM', 'num_txt', "---")
        self.assert_json_equal('LABELFORM', 'status', "en création")
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}avoir{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'date', formats.date_format(date.today(), "DATE_FORMAT"))
        self.factory.xfer = BillAddModify()
        self.calljson('/diacamma.invoice/billAddModify',
                      {'bill': 2, 'date': '2015-04-01', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'date', "1 avril 2015")
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}{[/font]}")

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid',
                      {'CONFIRME': 'YES', 'bill': 2, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 10)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_add_quotation(self):
        default_articles()
        self._create_bill([{'article': 1, 'designation': 'article 1',
                            'price': '22.50', 'quantity': 3, 'reduce': '5.0'}], 0, '2015-04-01', 6)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid',
                      {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('', 10)
        self.assert_json_equal('LABELFORM', 'num_txt', "A-1")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}devis{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'date', "1 avril 2015")
        self.assert_json_equal('LABELFORM', 'total_excltax', "62.50€")
        self.assertEqual(len(self.json_actions), 5)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

        self.factory.xfer = BillFromQuotation()
        self.calljson('/diacamma.invoice/billFromQuotation',
                      {'CONFIRME': 'YES', 'bill': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billFromQuotation')
        self.assertEqual(self.response_json['action']['id'], "diacamma.invoice/billShow")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['bill'], 2)

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': -1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 0)
        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'status_filter': 3}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 1)

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('', 12)
        self.assert_json_equal('LABELFORM', 'total_excltax', "62.50€")
        self.assert_json_equal('LABELFORM', 'num_txt', "---")
        self.assert_json_equal('LABELFORM', 'status', "en création")
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'date', formats.date_format(date.today(), "DATE_FORMAT"))

    def test_compta_asset(self):
        default_articles()
        self._create_bill([{'article': 0, 'designation': 'article A', 'price': '22.20', 'quantity': 3},
                           {'article': 0, 'designation': 'article B', 'price': '11.10', 'quantity': 2}], 2, '2015-04-01', 6)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid',
                      {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('', 13)
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}avoir{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'total_excltax', "88.80€")
        self.assert_json_equal('LABELFORM', 'num_txt', "A-1")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)

        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-04-01')
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[411 Dalton Jack]')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}88.80€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[706] 706')
        self.assert_json_equal('', 'entryline/@1/debit', '{[font color="blue"]}88.80€{[/font]}')

        self.check_list_del_archive()

    def test_compta_receive(self):
        default_articles()
        self._create_bill([{'article': 2, 'designation': 'article', 'price': '25.00', 'quantity': 1}],
                          3, '2015-04-01', 6)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid',
                      {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_count_equal('', 13)
        self.assert_json_equal('LABELFORM', 'total_excltax', "25.00€")
        self.assert_json_equal('LABELFORM', 'num_txt', "A-1")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}reçu{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'date', "1 avril 2015")
        self.assertEqual(len(self.json_actions), 4)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)

        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-04-01')
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', "[411 Dalton Jack]")
        self.check_list_del_archive()

    def test_bill_price_with_vat(self):
        default_articles()
        Parameter.change_value('invoice-vat-mode', '2')
        Params.clear()
        details = [{'article': 1, 'designation': 'article 1', 'price': '22.50', 'quantity': 3, 'reduce': '5.0'},  # code 701
                   {'article': 2, 'designation': 'article 2',  # +5% vat => 1.08 - code 707
                       'price': '3.25', 'quantity': 7},
                   {'article': 0, 'designation': 'article 3',
                       'price': '11.10', 'quantity': 2},  # code 709
                   {'article': 5, 'designation': 'article 4', 'price': '6.33', 'quantity': 3.25}]  # +20% vat => 3.43  - code 701
        self._create_bill(details, 1, '2015-04-01', 6)

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)

        self.assert_grid_equal('detail', {"article": "article", "designation": "désignation", "price_txt": "prix TTC", "unit": "unité",
                                          "quantity": "quantité", "storagearea": "lieu de stockage", "reduce_txt": "réduction", "total": "total TTC"}, 4)  # nb=8
        self.assert_attrib_equal('total_excltax', 'description', "total HT")
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}{[/font]}")
        self.assert_attrib_equal('total_incltax', 'description', "total TTC")
        self.assert_json_equal('LABELFORM', 'total_incltax', "128.02€")
        self.assert_json_equal('LABELFORM', 'vta_sum', "4.51€")
        self.assert_json_equal('LABELFORM', 'total_excltax', "123.51€")

        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid',
                      {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/entry_account', "[411 Dalton Jack]")
        self.assert_json_equal('', 'entryline/@1/entry_account', "[4455] 4455")
        self.assert_json_equal('', 'entryline/@1/credit', '{[font color="green"]}4.51€{[/font]}')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 123.51€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 123.51€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_grid_equal('bill', {"bill_type": "type de facture", "num_txt": "N°", "date": "date", "third": "tiers", "comment": "commentaire", "total": "total TTC", "status": "status"}, 1)  # nb=7

    def test_bill_price_without_vat(self):
        default_articles()
        Parameter.change_value('invoice-vat-mode', '1')
        Params.clear()
        details = [{'article': 1, 'designation': 'article 1', 'price': '22.50', 'quantity': 3, 'reduce': '5.0'},
                   {'article': 2, 'designation': 'article 2',  # +5% vat => 1.14
                       'price': '3.25', 'quantity': 7},
                   {'article': 0, 'designation': 'article 3',
                       'price': '11.10', 'quantity': 2},
                   {'article': 5, 'designation': 'article 4', 'price': '6.33', 'quantity': 3.25}]  # +20% vat => 4.11
        self._create_bill(details, 1, '2015-04-01', 6)

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)

        self.assert_grid_equal('detail', {"article": "article", "designation": "désignation", "price_txt": "prix HT", "unit": "unité",
                                          "quantity": "quantité", "storagearea": "lieu de stockage", "reduce_txt": "réduction", "total": "total HT"}, 4)  # nb=8
        self.assert_attrib_equal('total_excltax', 'description', "total HT")
        self.assert_json_equal('LABELFORM', 'info', "{[font color=\"red\"]}{[/font]}")
        self.assert_attrib_equal('total_incltax', 'description', "total TTC")
        self.assert_json_equal('LABELFORM', 'total_incltax', "133.27€")
        self.assert_json_equal('LABELFORM', 'vta_sum', "5.25€")
        self.assert_json_equal('LABELFORM', 'total_excltax', "128.02€")

        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = BillTransition()
        self.calljson('/diacamma.invoice/billValid',
                      {'CONFIRME': 'YES', 'bill': 1, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billValid')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/entry_account', "[411 Dalton Jack]")
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}133.27€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', "[4455] 4455")
        self.assert_json_equal('', 'entryline/@1/credit', '{[font color="green"]}5.25€{[/font]}')
        self.assert_json_equal('', 'entryline/@2/entry_account', "[701] 701")
        self.assert_json_equal('', 'entryline/@2/credit', '{[font color="green"]}88.07€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry_account', "[706] 706")
        self.assert_json_equal('', 'entryline/@3/credit', '{[font color="green"]}22.20€{[/font]}')
        self.assert_json_equal('', 'entryline/@4/entry_account', "[707] 707")
        self.assert_json_equal('', 'entryline/@4/credit', '{[font color="green"]}22.75€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/entry_account', "[709] 709")
        self.assert_json_equal('', 'entryline/@5/debit', '{[font color="blue"]}5.00€{[/font]}')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 128.02€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 128.02€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_grid_equal('bill', {"bill_type": "type de facture", "num_txt": "N°", "date": "date", "third": "tiers", "comment": "commentaire", "total": "total HT", "status": "status"}, 1)  # nb=7

    def test_list_sorted(self):
        default_articles()
        details = [{'article': 0, 'designation': 'article 0', 'price': '20.00', 'quantity': 15}]
        self._create_bill(details, 0, '2015-04-01', 6, True)  # 59.50
        details = [{'article': 1, 'designation': 'article 1', 'price': '22.00', 'quantity': 3, 'reduce': '5.0'},
                   {'article': 2, 'designation': 'article 2', 'price': '3.25', 'quantity': 7}]
        self._create_bill(details, 1, '2015-04-01', 6, True)  # 83.75
        details = [{'article': 0, 'designation': 'article 0', 'price': '50.00', 'quantity': 2},
                   {'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 6.75}]
        self._create_bill(details, 3, '2015-04-01', 4, True)  # 142.73
        details = [{'article': 1, 'designation': 'article 1', 'price': '23.00', 'quantity': 3},
                   {'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 3.50}]
        self._create_bill(details, 1, '2015-04-01', 5, True)  # 91.16
        details = [{'article': 2, 'designation': 'article 2', 'price': '3.30', 'quantity': 5},
                   {'article': 5, 'designation': 'article 5', 'price': '6.35', 'quantity': 4.25, 'reduce': '2.0'}]
        self._create_bill(details, 1, '2015-04-01', 6, True)  # 41.49
        details = [{'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 1.25}]
        self._create_bill(details, 2, '2015-04-01', 4, True)  # 7.91

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_count_equal('bill', 6)
        self.assert_json_equal('', 'bill/@0/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@1/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@2/third', 'Minimum')
        self.assert_json_equal('', 'bill/@3/third', 'Dalton William')
        self.assert_json_equal('', 'bill/@4/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@5/third', 'Minimum')

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'GRID_ORDER%bill': 'third'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_json_equal('', 'bill/@0/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@1/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@2/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@3/third', 'Dalton William')
        self.assert_json_equal('', 'bill/@4/third', 'Minimum')
        self.assert_json_equal('', 'bill/@5/third', 'Minimum')

        self.factory.xfer = BillList()
        self.calljson('/diacamma.invoice/billList', {'GRID_ORDER%bill': 'third', 'GRID_ORDER%bill_third': '+'}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billList')
        self.assert_json_equal('', 'bill/@5/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@4/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@3/third', 'Dalton Jack')
        self.assert_json_equal('', 'bill/@2/third', 'Dalton William')
        self.assert_json_equal('', 'bill/@1/third', 'Minimum')
        self.assert_json_equal('', 'bill/@0/third', 'Minimum')

    def test_statistic(self):
        default_articles()
        details = [{'article': 0, 'designation': 'article 0', 'price': '20.00', 'quantity': 15}]
        self._create_bill(details, 0, '2015-04-01', 6, True)  # 59.50
        details = [{'article': 1, 'designation': 'article 1', 'price': '22.00', 'quantity': 3, 'reduce': '5.0'},
                   {'article': 2, 'designation': 'article 2', 'price': '3.25', 'quantity': 7}]
        self._create_bill(details, 1, '2015-04-01', 6, True)  # 83.75
        details = [{'article': 0, 'designation': 'article 0', 'price': '50.00', 'quantity': 2},
                   {'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 6.75}]
        self._create_bill(details, 3, '2015-04-01', 4, True)  # 142.73
        details = [{'article': 1, 'designation': 'article 1', 'price': '23.00', 'quantity': 3},
                   {'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 3.50}]
        self._create_bill(details, 1, '2015-04-01', 5, True)  # 91.16
        details = [{'article': 2, 'designation': 'article 2', 'price': '3.30', 'quantity': 5},
                   {'article': 5, 'designation': 'article 5', 'price': '6.35', 'quantity': 4.25, 'reduce': '2.0'}]
        self._create_bill(details, 1, '2015-04-01', 6, True)  # 41.49
        details = [{'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 1.25}]
        self._create_bill(details, 2, '2015-04-01', 4, True)  # 7.91

        self.factory.xfer = BillStatistic()
        self.calljson('/diacamma.invoice/billStatistic', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billStatistic')
        self.assert_count_equal('', 7)

        self.assert_count_equal('articles', 5)
        self.assert_json_equal('', 'articles/@0/article', "ABC1")
        self.assert_json_equal('', 'articles/@0/amount', "130.00€")
        self.assert_json_equal('', 'articles/@0/number', "6.00")
        self.assert_json_equal('', 'articles/@1/article', "---")
        self.assert_json_equal('', 'articles/@1/amount', "100.00€")
        self.assert_json_equal('', 'articles/@1/number', "2.00")
        self.assert_json_equal('', 'articles/@1/mean', "50.00€")
        self.assert_json_equal('', 'articles/@1/ratio', "28.47 %")

        self.assert_json_equal('', 'articles/@2/article', "ABC5")
        self.assert_json_equal('', 'articles/@2/amount', "81.97€")
        self.assert_json_equal('', 'articles/@2/number', "13.25")
        self.assert_json_equal('', 'articles/@3/article', "ABC2")
        self.assert_json_equal('', 'articles/@3/amount', "39.25€")
        self.assert_json_equal('', 'articles/@3/number', "12.00")
        self.assert_json_equal('', 'articles/@4/article', '{[b]}total{[/b]}')
        self.assert_json_equal('', 'articles/@4/amount', '{[b]}351.22€{[/b]}')
        self.assert_json_equal('', 'articles/@4/number', '{[b]}---{[/b]}')

        self.assert_count_equal('customers', 4)
        self.assert_json_equal('', 'customers/@0/customer', "Minimum")
        self.assert_json_equal('', 'customers/@0/amount', "134.82€")
        self.assert_json_equal('', 'customers/@1/customer', "Dalton Jack")
        self.assert_json_equal('', 'customers/@1/amount', "125.24€")
        self.assert_json_equal('', 'customers/@1/ratio', "35.66 %")
        self.assert_json_equal('', 'customers/@2/customer', "Dalton William")
        self.assert_json_equal('', 'customers/@2/amount', "91.16€")
        self.assert_json_equal('', 'customers/@3/customer', '{[b]}total{[/b]}')
        self.assert_json_equal('', 'customers/@3/amount', '{[b]}351.22€{[/b]}')

        self.factory.xfer = BillStatisticPrint()
        self.calljson('/diacamma.invoice/billStatisticPrint', {'PRINT_MODE': '4'}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'billStatisticPrint')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 24, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Impression des statistiques"')
        self.assertEqual(content_csv[12].strip(), '"total";"351.22€";"100.00 %";')
        self.assertEqual(content_csv[20].strip(), '"total";"351.22€";"---";"---";"100.00 %";')

        self.factory.xfer = BillPrint()
        self.calljson('/diacamma.invoice/billPrint', {'bill': '1;2;3;4;5', 'PRINT_MODE': 3, 'MODEL': 8}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'billPrint')

    def test_payoff_bill(self):
        default_articles()
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        bill_id = self._create_bill(details, 1, '2015-04-01', 6, True)  # 59.50

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 100.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 100.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id}, False)
        self.assertEqual(self.json_context['supporting'], bill_id)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "0.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "100.00€")
        self.assert_count_equal('payoff', 0)
        self.assert_count_equal('#payoff/actions', 3)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supporting': bill_id}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_count_equal('', 7)
        self.assert_json_equal('FLOAT', 'amount', "100.00")
        self.assert_attrib_equal('amount', 'max', "100.0")
        self.assert_json_equal('EDIT', 'payer', "Dalton Jack")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': bill_id, 'amount': '60.0', 'payer': "Ma'a Dalton", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id}, False)
        self.assertEqual(self.json_context['supporting'], bill_id)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "60.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "40.00€")
        self.assert_count_equal('payoff', 1)
        self.assert_count_equal('#payoff/actions', 3)
        self.assert_json_equal('', 'payoff/@0/date', "2015-04-03")
        self.assert_json_equal('', 'payoff/@0/mode', "espèce")
        self.assert_json_equal('', 'payoff/@0/value', "60.00€")
        self.assert_json_equal('', 'payoff/@0/payer', "Ma'a Dalton")
        self.assert_json_equal('', 'payoff/@0/reference', "abc")
        self.assert_json_equal('', 'payoff/@0/bank_account', "---")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@3/entry_account', "[531] 531")
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 100.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 100.00€{[br/]}{[b]}Trésorerie :{[/b]} 60.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supporting': bill_id}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "40.00")
        self.assert_attrib_equal('amount', 'max', "40.0")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': bill_id, 'amount': '40.0', 'payer': "Dalton Jack", 'date': '2015-04-04', 'mode': 2, 'reference': 'efg', 'bank_account': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id}, False)
        self.assertEqual(self.json_context['supporting'], bill_id)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")
        self.assert_count_equal('payoff', 2)
        self.assert_count_equal('#payoff/actions', 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@5/entry_account', "[581] 581")
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 100.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 100.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_payoff_avoid(self):
        default_articles()
        details = [
            {'article': 0, 'designation': 'article 0', 'price': '50.00', 'quantity': 1}]
        bill_id = self._create_bill(details, 2, '2015-04-01', 6, True)  # 59.50

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} -50.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} -50.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.calljson(
            '/diacamma.payoff/payoffAddModify', {'supporting': bill_id, 'mode': 3}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_count_equal('', 7)
        self.assert_select_equal('bank_account', 2)  # nb=2

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': bill_id, 'amount': '50.0', 'date': '2015-04-04', 'mode': 3, 'reference': 'ijk', 'bank_account': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id}, False)
        self.assertEqual(self.json_context['supporting'], bill_id)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "50.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "50.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")
        self.assert_count_equal('payoff', 1)
        self.assert_count_equal('#payoff/actions', 2)
        self.assert_json_equal('', 'payoff/@0/date', "2015-04-04")
        self.assert_json_equal('', 'payoff/@0/mode', "carte de crédit")
        self.assert_json_equal('', 'payoff/@0/value', "50.00€")
        self.assert_json_equal('', 'payoff/@0/reference', "ijk")
        self.assert_json_equal('', 'payoff/@0/bank_account', "My bank")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@2/entry_account', "[411 Dalton Jack]")
        self.assert_json_equal('', 'entryline/@3/entry_account', "[512] 512")
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} -50.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} -50.00€{[br/]}{[b]}Trésorerie :{[/b]} -50.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffDel()
        self.calljson('/diacamma.payoff/payoffDel', {'CONFIRME': 'YES', 'payoff': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffDel')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} -50.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} -50.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = BillPrint()
        self.calljson('/diacamma.invoice/billPrint', {'bill': '1', 'PRINT_MODE': 3, 'MODEL': 9}, False)
        self.assert_observer('core.print', 'diacamma.invoice', 'billPrint')

    def test_payoff_multi(self):
        default_articles()
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        bill_id1 = self._create_bill(details, 1, '2015-04-01', 6, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '50.00', 'quantity': 1}]
        bill_id2 = self._create_bill(details, 1, '2015-04-01', 4, True)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('', 'entryline/@1/entry.link', '---')
        self.assert_json_equal('', 'entryline/@2/entry.link', '---')
        self.assert_json_equal('', 'entryline/@3/entry.link', '---')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 150.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 150.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = BillMultiPay()
        self.calljson('/diacamma.invoice/billMultiPay', {'bill': '%s;%s' % (bill_id1, bill_id2)}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billMultiPay')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payoffAddModify")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['supportings'], '%s;%s' % (bill_id1, bill_id2))

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supportings': '%s;%s' % (bill_id1, bill_id2)}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "150.00")
        self.assert_attrib_equal('amount', 'max', "150.0")
        self.assert_json_equal('EDIT', 'payer', "Dalton Jack")
        self.assert_select_equal('repartition', 2)  # nb=2
        self.assert_json_equal('SELECT', 'repartition', "0")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supportings': '%s;%s' % (bill_id1, bill_id2),
                                                           'amount': '100.0', 'date': '2015-04-04', 'mode': 0, 'reference': '', 'bank_account': 0, 'payer': "Ma'a Dalton"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "66.67€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "33.33€")

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "50.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "33.33€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "16.67€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 7)
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('', 'entryline/@1/entry.link', '---')
        self.assert_json_equal('', 'entryline/@2/entry.link', '---')
        self.assert_json_equal('', 'entryline/@3/entry.link', '---')
        self.assert_json_equal('', 'entryline/@4/entry.link', '---')
        self.assert_json_equal('', 'entryline/@5/entry.link', '---')
        self.assert_json_equal('', 'entryline/@6/entry.link', '---')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 150.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 150.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_payoff_multi_samethird(self):
        default_articles()
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        bill_id1 = self._create_bill(details, 1, '2015-04-01', 6, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '50.00', 'quantity': 1}]
        bill_id2 = self._create_bill(details, 1, '2015-04-01', 6, True)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('', 'entryline/@1/entry.link', '---')
        self.assert_json_equal('', 'entryline/@2/entry.link', '---')
        self.assert_json_equal('', 'entryline/@3/entry.link', '---')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 150.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 150.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = BillMultiPay()
        self.calljson('/diacamma.invoice/billMultiPay', {'bill': '%s;%s' % (bill_id1, bill_id2)}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billMultiPay')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payoffAddModify")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['supportings'], '%s;%s' % (bill_id1, bill_id2))

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supportings': '%s;%s' % (bill_id1, bill_id2)}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "150.00")
        self.assert_attrib_equal('amount', 'max', "150.0")
        self.assert_json_equal('EDIT', 'payer', "Dalton Jack")
        self.assert_select_equal('repartition', 2)  # nb=2
        self.assert_json_equal('SELECT', 'repartition', "0")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supportings': '%s;%s' % (bill_id1, bill_id2), 'amount': '150.0',
                                                           'date': '2015-04-04', 'mode': 0, 'reference': '', 'bank_account': 0, 'payer': "Ma'a Dalton", "repartition": 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "50.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "50.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@5/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@4/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@3/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@2/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@1/entry.link', 'A')
        self.assert_json_equal('', 'entryline/@0/entry.link', 'A')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 150.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 150.00€{[br/]}{[b]}Trésorerie :{[/b]} 150.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_payoff_multi_bydate(self):
        default_articles()
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        bill_id1 = self._create_bill(details, 1, '2015-04-01', 6, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '50.00', 'quantity': 1}]
        bill_id2 = self._create_bill(details, 1, '2015-04-03', 6, True)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@3/entry.link', '---')
        self.assert_json_equal('', 'entryline/@2/entry.link', '---')
        self.assert_json_equal('', 'entryline/@1/entry.link', '---')
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 150.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 150.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = BillMultiPay()
        self.calljson('/diacamma.invoice/billMultiPay',
                      {'bill': '%s;%s' % (bill_id1, bill_id2)}, False)
        self.assert_observer('core.acknowledge', 'diacamma.invoice', 'billMultiPay')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payoffAddModify")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['supportings'], '%s;%s' % (bill_id1, bill_id2))

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supportings': '%s;%s' % (bill_id1, bill_id2)}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "150.00")
        self.assert_attrib_equal('amount', 'max', "150.0")
        self.assert_json_equal('EDIT', 'payer', "Dalton Jack")
        self.assert_select_equal('repartition', 2)  # nb=2
        self.assert_json_equal('SELECT', 'repartition', "0")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supportings': '%s;%s' % (bill_id1, bill_id2), 'amount': '120.0',
                                                           'date': '2015-04-07', 'mode': 0, 'reference': '', 'bank_account': 0, 'payer': "Ma'a Dalton", "repartition": 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': bill_id2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'total_excltax', "50.00€")
        self.assert_json_equal('LABELFORM', 'total_payed', "20.00€")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "30.00€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@5/entry.link', '---')
        self.assert_json_equal('', 'entryline/@4/entry.link', '---')
        self.assert_json_equal('', 'entryline/@3/entry.link', '---')
        self.assert_json_equal('', 'entryline/@2/entry.link', '---')
        self.assert_json_equal('', 'entryline/@1/entry.link', '---')
        self.assert_json_equal('', 'entryline/@0/entry.link', '---')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 150.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 150.00€{[br/]}{[b]}Trésorerie :{[/b]} 120.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_send_bill(self):
        default_articles()
        configSMTP('localhost', 2025)
        server = TestReceiver()
        server.start(2025)
        try:
            self.assertEqual(0, server.count())
            details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
            bill_id = self._create_bill(
                details, 1, '2015-04-01', 6, True)  # 59.50
            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail',
                          {'item_name': 'bill', 'bill': bill_id}, False)
            self.assert_observer('core.custom', 'diacamma.payoff', 'payableEmail')
            self.assert_count_equal('', 4)
            self.assert_json_equal('EDIT', 'subject', 'facture A-1 - 1 avril 2015')
            self.assert_json_equal('MEMO', 'message', 'Jack Dalton\n\nVeuillez trouver ci-Joint à ce courriel facture A-1 - 1 avril 2015.\n\nSincères salutations')

            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail',
                          {'bill': bill_id, 'OK': 'YES', 'item_name': 'bill', 'subject': 'my bill', 'message': 'this is a bill.', 'model': 8}, False)
            self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payableEmail')
            self.assertEqual(1, server.count())
            self.assertEqual('mr-sylvestre@worldcompany.com', server.get(0)[1])
            self.assertEqual(['Jack.Dalton@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(0)[2])
            msg, msg_file = server.check_first_message('my bill', 2, {'To': 'Jack.Dalton@worldcompany.com'})
            self.assertEqual('text/html', msg.get_content_type())
            self.assertEqual('base64', msg.get('Content-Transfer-Encoding', ''))
            self.assertEqual('<html>this is a bill.</html>', decode_b64(msg.get_payload()))
            self.assertTrue('facture_A-1_Dalton Jack.pdf' in msg_file.get('Content-Type', ''), msg_file.get('Content-Type', ''))
            self.assertEqual("%PDF".encode('ascii', 'ignore'), b64decode(msg_file.get_payload())[:4])
        finally:
            server.stop()

    def test_search(self):
        CustomField.objects.create(modelname='accounting.Third', name='categorie', kind=4, args="{'list':['---','petit','moyen','gros']}")
        CustomField.objects.create(modelname='accounting.Third', name='value', kind=1, args="{'min':0,'max':100}")
        default_customize()
        initial_thirds()
        default_categories()
        default_articles()
        details = [{'article': 0, 'designation': 'article 0', 'price': '20.00', 'quantity': 15}]
        self._create_bill(details, 0, '2015-04-01', 6, True)  # 59.50
        details = [{'article': 1, 'designation': 'article 1', 'price': '22.00', 'quantity': 3, 'reduce': '5.0'},
                   {'article': 2, 'designation': 'article 2', 'price': '3.25', 'quantity': 7}]
        self._create_bill(details, 1, '2015-04-01', 6, True)  # 83.75
        details = [{'article': 0, 'designation': 'article 0', 'price': '50.00', 'quantity': 2},
                   {'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 6.75}]
        self._create_bill(details, 3, '2015-04-01', 4, True)  # 142.73
        details = [{'article': 1, 'designation': 'article 1', 'price': '23.00', 'quantity': 3},
                   {'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 3.50}]
        self._create_bill(details, 1, '2015-04-01', 5, True)  # 91.16
        details = [{'article': 2, 'designation': 'article 2', 'price': '3.30', 'quantity': 5},
                   {'article': 5, 'designation': 'article 5', 'price': '6.35', 'quantity': 4.25, 'reduce': '2.0'}]
        self._create_bill(details, 1, '2015-04-01', 6, True)  # 41.49
        details = [{'article': 5, 'designation': 'article 5', 'price': '6.33', 'quantity': 1.25}]
        self._create_bill(details, 2, '2015-04-01', 4, True)  # 7.91

        self.factory.xfer = BillSearch()
        self.calljson('/diacamma.invoice/billSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billSearch')
        self.assert_count_equal('bill', 6)

        search_field_list = Bill.get_search_fields()
        self.assertEqual(6 + 8 + 1 + 2 + 2 + 4 + 9 + 2 + 2 + 2, len(search_field_list), search_field_list)  # bill + contact + custom contact + custom third + third + detail + article  + art custom + category + provider
