# -*- coding: utf-8 -*-
'''
from_v1 module for accounting

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
import sys

from django.apps import apps
from django.utils import six

from lucterios.install.lucterios_migration import MigrateAbstract
from lucterios.CORE.models import Parameter
from diacamma.accounting.from_v1 import convert_code


class InvoiceMigrate(MigrateAbstract):

    def __init__(self, old_db):
        MigrateAbstract.__init__(self, old_db)
        self.vat_list = {}
        self.article_list = {}
        self.bill_list = {}
        self.detail_list = {}

    def _vat(self):
        vat_mdl = apps.get_model("invoice", "Vat")
        vat_mdl.objects.all().delete()
        self.vat_list = {}
        cur_v = self.old_db.open()
        cur_v.execute(
            "SELECT id,name,taux,actif FROM fr_sdlibre_facture_tva")
        for vatid, name, taux, actif in cur_v.fetchall():
            self.print_log("=> VAT %s", (name,))
            self.vat_list[vatid] = vat_mdl.objects.create(
                name=name, rate=taux, isactif=actif == 'o')

    def _article(self):
        article_mdl = apps.get_model("invoice", "Article")
        article_mdl.objects.all().delete()
        self.article_list = {}
        cur_a = self.old_db.open()
        cur_a.execute(
            "SELECT id,reference,designation,prix,unit,compteVente,tva,noactive FROM fr_sdlibre_facture_articles")
        for articleid, reference, designation, prix, unit, compteVente, tva, noactive in cur_a.fetchall():
            self.print_log("=> article %s", (reference,))
            if unit == 'NULL':
                unit = None
            self.article_list[articleid] = article_mdl.objects.create(
                reference=reference, designation=designation, price=prix, unit=unit, sell_account=convert_code(compteVente), isdisabled=noactive == 'o')
            if tva != 0:
                self.article_list[articleid].vat = self.vat_list[tva]
                self.article_list[articleid].save()

    def _bill(self):
        bill_mdl = apps.get_model("invoice", "Bill")
        bill_mdl.objects.all().delete()
        self.bill_list = {}
        detail_mdl = apps.get_model("invoice", "Detail")
        detail_mdl.objects.all().delete()
        self.detail_list = {}
        cur_b = self.old_db.open()
        cur_b.execute(
            "SELECT id,exercice,typeFact,num,date,tiers,comment,etat,operation,analytique FROM fr_sdlibre_facture_factures")
        for billid, exercice, typeFact, num, factdate, tiers, comment, etat, operation, analytique in cur_b.fetchall():
            if typeFact != 3:
                self.print_log(
                    "=> bill ex:%s - type:%s - num:%s - date=%s", (exercice, typeFact, num, factdate))
                if typeFact == 4:
                    typeFact = 3
                self.bill_list[billid] = bill_mdl.objects.create(
                    bill_type=typeFact, date=factdate, comment=comment, status=etat, num=num)
                if exercice in self.old_db.objectlinks['year'].keys():
                    self.bill_list[billid].fiscal_year = self.old_db.objectlinks[
                        'year'][exercice]
                if tiers in self.old_db.objectlinks['third'].keys():
                    self.bill_list[billid].third = self.old_db.objectlinks[
                        'third'][tiers]
                if operation in self.old_db.objectlinks['entryaccount'].keys():
                    self.bill_list[billid].entry = self.old_db.objectlinks[
                        'entryaccount'][operation]
                if analytique in self.old_db.objectlinks['costaccounting'].keys():
                    self.bill_list[billid].cost_accounting = self.old_db.objectlinks[
                        'costaccounting'][analytique]
                self.bill_list[billid].save()
        cur_d = self.old_db.open()
        cur_d.execute(
            "SELECT id,article,designation,prix,quantite,unit,factures,remise,taxe FROM fr_sdlibre_facture_details")
        for detailid, article, designation, prix, quantite, unit, factures, remise, taxe in cur_d.fetchall():
            if factures in self.bill_list.keys():
                self.detail_list[detailid] = detail_mdl.objects.create(bill=self.bill_list[factures], designation=designation,
                                                                       price=prix, unit=unit, quantity=quantite, reduce=remise)
                if article in self.article_list.keys():
                    self.detail_list[
                        detailid].article = self.article_list[article]
                if taxe > 0.0001:
                    self.detail_list[
                        detailid].vta_rate = taxe / (prix * quantite - remise)
                self.detail_list[detailid].save()

    def _params(self):
        cur_p = self.old_db.open()
        cur_p.execute(
            "SELECT paramName,value FROM CORE_extension_params WHERE extensionId LIKE 'fr_sdlibre_facture' and paramName in ('ModeTVA','DefaultCompteVente','compteTVAVente','CompteRemise','CompteFraisBank','CompteCaisse')")
        for param_name, param_value in cur_p.fetchall():
            pname = ''
            if param_name == 'ModeTVA':
                pname = 'invoice-vat-mode'
            elif param_name == 'DefaultCompteVente':
                pname = 'invoice-default-sell-account'
                param_value = convert_code(param_value)
            elif param_name == 'compteTVAVente':
                pname = 'invoice-vatsell-account'
                param_value = convert_code(param_value)
            elif param_name == 'CompteRemise':
                pname = 'invoice-reduce-account'
                param_value = convert_code(param_value)
            elif param_name == 'CompteFraisBank':
                pname = 'invoice-bankcharges-account'
                param_value = convert_code(param_value)
            elif param_name == 'CompteCaisse':
                pname = 'invoice-cash-account'
                param_value = convert_code(param_value)
            if pname != '':
                self.print_log(
                    "=> parameter of invoice %s - %s", (pname, param_value))
                Parameter.change_value(pname, param_value)

    def run(self):
        try:
            self._params()
            self._vat()
            self._article()
            self._bill()
        except:
            import traceback
            traceback.print_exc()
            six.print_("*** Unexpected error: %s ****" % sys.exc_info()[0])
        self.old_db.objectlinks['article'] = self.article_list
        self.old_db.objectlinks['bill'] = self.bill_list
