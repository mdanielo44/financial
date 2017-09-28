# -*- coding: utf-8 -*-
'''
diacamma.invoice test_tools package

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

from diacamma.accounting.models import FiscalYear
from diacamma.accounting.test_tools import create_account, default_costaccounting

from diacamma.invoice.models import Article, Vat, Category, Provider,\
    StorageArea, StorageSheet, StorageDetail
from diacamma.invoice.views import BillTransition, DetailAddModify, BillAddModify
from diacamma.payoff.views import SupportingThirdValid
from lucterios.contacts.models import CustomField


def default_articles(with_provider=False, with_storage=False):
    default_costaccounting()

    create_account(['709'], 3, FiscalYear.get_current())
    create_account(['4455'], 1, FiscalYear.get_current())
    vat1 = Vat.objects.create(name="5%", rate=5.0, account='4455', isactif=True)
    vat2 = Vat.objects.create(name="20%", rate=20.0, account='4455', isactif=True)
    art1 = Article.objects.create(reference='ABC1', designation="Article 01",
                                  price="12.34", unit="kg", isdisabled=False, sell_account="701", vat=None, stockable=1 if with_storage else 0)
    art2 = Article.objects.create(reference='ABC2', designation="Article 02",
                                  price="56.78", unit="l", isdisabled=False, sell_account="707", vat=vat1, stockable=1 if with_storage else 0)
    art3 = Article.objects.create(reference='ABC3', designation="Article 03",
                                  price="324.97", unit="", isdisabled=False, sell_account="601" if not with_storage else "701", vat=None, stockable=0)
    art4 = Article.objects.create(reference='ABC4', designation="Article 04",
                                  price="1.31", unit="", isdisabled=False, sell_account="708", vat=None, stockable=2 if with_storage else 0)
    art5 = Article.objects.create(reference='ABC5', designation="Article 05",
                                  price="64.10", unit="m", isdisabled=True, sell_account="701", vat=vat2, stockable=0)
    cat_list = Category.objects.all()
    if len(cat_list) > 0:
        art1.categories = cat_list.filter(id__in=(1,))
        art1.save()
        art2.categories = cat_list.filter(id__in=(2,))
        art2.save()
        art3.categories = cat_list.filter(id__in=(2, 3,))
        art3.save()
        art4.categories = cat_list.filter(id__in=(3,))
        art4.save()
        art5.categories = cat_list.filter(id__in=(1, 2, 3))
        art5.save()
    if with_provider:
        Provider.objects.create(third_id=1, reference="a123", article=art1)
        Provider.objects.create(third_id=1, reference="b234", article=art2)
        Provider.objects.create(third_id=1, reference="c345", article=art3)
        Provider.objects.create(third_id=2, reference="d456", article=art3)
        Provider.objects.create(third_id=2, reference="e567", article=art4)
        Provider.objects.create(third_id=2, reference="f678", article=art5)


def default_categories():
    Category.objects.create(name='cat 1', designation="categorie N°1")
    Category.objects.create(name='cat 2', designation="categorie N°2")
    Category.objects.create(name='cat 3', designation="categorie N°3")


def default_customize():
    CustomField.objects.create(modelname='invoice.Article', name='couleur', kind=4, args="{'list':['---','noir','blanc','rouge','bleu','jaune']}")
    CustomField.objects.create(modelname='invoice.Article', name='taille', kind=1, args="{'min':0,'max':100}")
    CustomField.objects.create(modelname='contacts.AbstractContact', name='truc', kind=0, args="{'multi':False}")


def default_area():
    StorageArea.objects.create(name='Lieu 1', designation="AAA")
    StorageArea.objects.create(name='Lieu 2', designation="BBB")
    StorageArea.objects.create(name='Lieu 3', designation="CCC")


def insert_storage():
    sheet1 = StorageSheet.objects.create(sheet_type=0, date='2014-01-01', storagearea_id=1, comment="A")
    StorageDetail.objects.create(storagesheet=sheet1, article_id=1, price=5.00, quantity=10.0)
    StorageDetail.objects.create(storagesheet=sheet1, article_id=2, price=4.00, quantity=15.0)
    StorageDetail.objects.create(storagesheet=sheet1, article_id=4, price=3.00, quantity=20.0)
    sheet1.valid()
    sheet2 = StorageSheet.objects.create(sheet_type=0, date='2014-01-02', storagearea_id=2, comment="B")
    StorageDetail.objects.create(storagesheet=sheet2, article_id=1, price=4.00, quantity=5.0)
    StorageDetail.objects.create(storagesheet=sheet2, article_id=2, price=3.00, quantity=10.0)
    StorageDetail.objects.create(storagesheet=sheet2, article_id=4, price=2.00, quantity=15.0)
    sheet2.valid()


class InvoiceTest(LucteriosTest):

    def _create_bill(self, details, bill_type, bill_date, bill_third, valid=False):
        if (bill_type == 0) or (bill_type == 3):
            cost_accounting = 0
        else:
            cost_accounting = 2
        self.factory.xfer = BillAddModify()
        self.call('/diacamma.invoice/billAddModify',
                  {'bill_type': bill_type, 'date': bill_date, 'cost_accounting': cost_accounting, 'SAVE': 'YES'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.invoice', 'billAddModify')
        bill_id = self.get_first_xpath("ACTION/PARAM[@name='bill']").text
        self.factory.xfer = SupportingThirdValid()
        self.call('/diacamma.invoice/supportingThirdValid',
                  {'supporting': bill_id, 'third': bill_third}, False)
        for detail in details:
            detail['SAVE'] = 'YES'
            detail['bill'] = bill_id
            self.factory.xfer = DetailAddModify()
            self.call('/diacamma.invoice/detailAddModify', detail, False)
            self.assert_observer(
                'core.acknowledge', 'diacamma.invoice', 'detailAddModify')
        if valid:
            self.factory.xfer = BillTransition()
            self.call('/diacamma.invoice/billTransition',
                      {'CONFIRME': 'YES', 'bill': bill_id, 'withpayoff': False, 'TRANSITION': 'valid'}, False)
            self.assert_observer(
                'core.acknowledge', 'diacamma.invoice', 'billTransition')
        return bill_id
