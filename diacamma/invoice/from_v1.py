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
import datetime

from django.apps import apps
from django.utils import six

from lucterios.install.lucterios_migration import MigrateAbstract
from lucterios.CORE.models import Parameter
from diacamma.accounting.from_v1 import convert_code
from lucterios.CORE.parameters import Params


class InvoiceMigrate(MigrateAbstract):

    def __init__(self, old_db):
        MigrateAbstract.__init__(self, old_db)
        self.vat_list = {}
        self.article_list = {}
        self.bill_list = {}
        self.detail_list = {}
        self.payoff_list = {}

    def _vat(self):
        vat_mdl = apps.get_model("invoice", "Vat")
        vat_mdl.objects.all().delete()
        self.vat_list = {}
        cur_v = self.old_db.open()
        cur_v.execute(
            "SELECT id,name,taux,actif FROM fr_sdlibre_facture_tva")
        for vatid, name, taux, actif in cur_v.fetchall():
            self.print_debug("=> VAT %s", (name,))
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
            if unit == 'NULL':
                unit = ''
            self.print_debug("=> article %s - %s %s", (reference, prix, unit))
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
                self.print_debug(
                    "=> bill ex:%s - type:%s - num:%s - date=%s", (exercice, typeFact, num, factdate))
                if typeFact == 4:
                    typeFact = 3
                if comment is None:
                    comment = ''
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
                self.bill_list[billid].is_revenu = typeFact != 2
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
                        detailid].vta_rate = taxe / (100 * prix * quantite - remise)
                else:
                    self.detail_list[detailid].vta_rate = 0.0
                self.detail_list[detailid].save()

    def _payoff(self):
        payoff_mdl = apps.get_model("payoff", "Payoff")
        payoff_mdl.objects.all().delete()
        self.payoff_list = {}
        bank_mdl = apps.get_model("payoff", "BankAccount")
        bank_mdl.objects.all().delete()
        self.bank_list = {}

        cur_b = self.old_db.open()
        cur_b.execute(
            "SELECT id, designation,etab,guichet,compte,clef,compteBank  FROM fr_sdlibre_facture_compteCheque")
        for bankid, designation, etab, guichet, compte, clef, compteBank in cur_b.fetchall():
            self.print_debug(
                "=> bank account:%s", (designation,))
            reference = "%s %s %s %s" % (etab, guichet, compte, clef)
            self.bank_list[bankid] = bank_mdl.objects.create(
                designation=designation, reference=reference, account_code=convert_code(compteBank))

        cur_p = self.old_db.open()
        cur_p.execute(
            "SELECT id, facture, date, montant, mode, reference, operation, CompteCheque, payeur FROM fr_sdlibre_facture_payement")
        for payoffid, facture, date, montant, mode, reference, operation, compte_cheque, payeur in cur_p.fetchall():
            if facture in self.bill_list.keys():
                self.print_debug(
                    "=> payoff bill:%s - date=%s - amount=%.2f", (facture, date, montant))
                if mode is None:
                    mode = 4
                self.payoff_list[payoffid] = payoff_mdl.objects.create(supporting=self.bill_list[facture],
                                                                       date=date, amount=montant, mode=mode,
                                                                       reference=reference, payer=payeur)
                if operation in self.old_db.objectlinks['entryaccount'].keys():
                    self.payoff_list[payoffid].entry = self.old_db.objectlinks[
                        'entryaccount'][operation]
                if compte_cheque in self.bank_list.keys():
                    self.payoff_list[payoffid].bank_account = self.bank_list[
                        compte_cheque]
                self.payoff_list[payoffid].save(
                    do_generate=False, do_linking=False)

    def _deposit(self):
        deposit_mdl = apps.get_model("payoff", "DepositSlip")
        deposit_mdl.objects.all().delete()
        self.deposit_list = {}
        ddetail_mdl = apps.get_model("payoff", "DepositDetail")
        ddetail_mdl.objects.all().delete()
        self.ddetail_list = {}

        cur_s = self.old_db.open()
        cur_s.execute(
            "SELECT id, etat,CompteCheque,date,reference FROM fr_sdlibre_facture_bordereauCheque")
        for depositid, etat, compte_cheque, date, reference in cur_s.fetchall():
            if compte_cheque in self.bank_list.keys():
                self.print_debug(
                    "=> deposit:%s %s %s", (compte_cheque, date, reference))
                if date is None:
                    date = datetime.date.today()
                self.deposit_list[depositid] = deposit_mdl.objects.create(
                    status=etat, bank_account=self.bank_list[compte_cheque], date=date, reference=reference)

        cur_d = self.old_db.open()
        cur_d.execute(
            "SELECT id,  bordereau,payement  FROM fr_sdlibre_facture_detailCheque")
        for ddetailid, bordereau, payement in cur_d.fetchall():
            if (bordereau in self.deposit_list.keys()) and (payement in self.payoff_list.keys()):
                self.ddetail_list[ddetailid] = ddetail_mdl.objects.create(deposit=self.deposit_list[bordereau],
                                                                          payoff=self.payoff_list[payement])

    def _params(self):
        cur_p = self.old_db.open()
        cur_p.execute(
            "SELECT paramName,value FROM CORE_extension_params WHERE extensionId LIKE 'fr_sdlibre_facture' and paramName in ('ModeTVA','DefaultCompteVente','compteTVAVente','CompteRemise','CompteFraisBank','CompteCaisse')")
        for param_name, param_value in cur_p.fetchall():
            pname = ''
            if param_name == 'ModeTVA':
                pname = 'invoice-vat-mode'
                if param_value == '':
                    param_value = '0'
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
                pname = 'payoff-bankcharges-account'
                param_value = convert_code(param_value)
            elif param_name == 'CompteCaisse':
                pname = 'payoff-cash-account'
                param_value = convert_code(param_value)
            if pname != '':
                self.print_debug(
                    "=> parameter of invoice %s - %s", (pname, param_value))
                Parameter.change_value(pname, param_value)
        Params.clear()

    def run(self):
        try:
            self._params()
            self._vat()
            self._article()
            self._bill()
            self._payoff()
            self._deposit()
        except:
            import traceback
            traceback.print_exc()
            six.print_("*** Unexpected error: %s ****" % sys.exc_info()[0])
        self.print_info("Nb articles:%d", len(self.article_list))
        self.print_info("Nb bills:%d", len(self.bill_list))
        self.old_db.objectlinks['article'] = self.article_list
        self.old_db.objectlinks['bill'] = self.bill_list
