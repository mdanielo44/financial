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
import re

from django.apps import apps
from django.utils import six

from lucterios.install.lucterios_migration import MigrateAbstract
import sys
import datetime
from lucterios.CORE.parameters import Params


def decode_html(data):
    def _callback(matches):
        match_id = matches.group(1)
        return six.unichr(int(match_id))
    return re.sub(r"&#(\d+)(;|(?=\s))", _callback, data)


def convert_code(num_cpt):
    return num_cpt


class AccountingMigrate(MigrateAbstract):

    def __init__(self, old_db):
        MigrateAbstract.__init__(self, old_db)
        self.abstract_list = self.old_db.objectlinks['abstracts']
        self.third_list = {}
        self.year_list = {}
        self.costaccounting_list = {}
        self.chartsaccount_list = {}
        self.journal_list = {}
        self.accountlink_list = {}
        self.entryaccount_list = {}
        self.entrylineaccount_list = {}
        self.model_list = {}
        self.modelline_list = {}

    def _thirds(self):
        third_mdl = apps.get_model("accounting", "Third")
        third_mdl.objects.all().delete()
        accountthird_mdl = apps.get_model("accounting", "AccountThird")
        accountthird_mdl.objects.all().delete()
        self.third_list = {}
        cur = self.old_db.open()
        cur.execute(
            "SELECT id,contact,compteFournisseur,compteClient,compteSalarie,compteSocietaire,etat FROM fr_sdlibre_compta_Tiers")
        for thirdid, abstractid, compte_fournisseur, compte_client, compte_salarie, compte_societaire, etat in cur.fetchall():
            self.print_debug(
                "=> Third of %s", (self.abstract_list[abstractid],))
            self.third_list[thirdid] = third_mdl.objects.create(
                contact=self.abstract_list[abstractid], status=etat)
            if (compte_fournisseur is not None) and (compte_fournisseur != ''):
                accountthird_mdl.objects.create(
                    third=self.third_list[thirdid], code=convert_code(compte_fournisseur))
            if (compte_client is not None) and (compte_client != ''):
                accountthird_mdl.objects.create(
                    third=self.third_list[thirdid], code=convert_code(compte_client))
            if (compte_salarie is not None) and (compte_salarie != ''):
                accountthird_mdl.objects.create(
                    third=self.third_list[thirdid], code=convert_code(compte_salarie))
            if (compte_societaire is not None) and (compte_societaire != ''):
                accountthird_mdl.objects.create(
                    third=self.third_list[thirdid], code=convert_code(compte_societaire))

    def _years(self):
        def get_date(new_date):
            return datetime.date(*[int(subvalue) for subvalue in re.split(r'[^\d]', new_date)[:3]])
        year_mdl = apps.get_model("accounting", "FiscalYear")
        year_mdl.objects.all().delete()
        self.year_list = {}
        cur = self.old_db.open()
        last_exercice = None
        cur.execute(
            "SELECT id, debut,fin,etat,actif  FROM fr_sdlibre_compta_Exercices ORDER BY fin")
        for yearid, debut, fin, etat, actif in cur.fetchall():
            self.print_debug("=> Year of %s => %s", (debut, fin))
            self.year_list[yearid] = year_mdl.objects.create(
                begin=get_date(debut), end=get_date(fin), status=etat, is_actif=(actif == 'o'))
            if last_exercice is not None:
                self.year_list[yearid].last_fiscalyear = self.year_list[
                    last_exercice]
                self.year_list[yearid].save()
            last_exercice = yearid

    def _costaccounting(self):
        costaccounting_mdl = apps.get_model("accounting", "CostAccounting")
        costaccounting_mdl.objects.all().delete()
        self.costaccounting_list = {}
        cur = self.old_db.open()
        cur.execute(
            "SELECT id, title, description, etat, last, codeDefault FROM fr_sdlibre_compta_Analytique ORDER BY id")
        for yearid, title, description, etat, last, code_default in cur.fetchall():
            self.print_debug("=> cost accounting %s", (title,))
            self.costaccounting_list[yearid] = costaccounting_mdl.objects.create(name=title, description=description,
                                                                                 status=etat, is_default=(code_default == 'o'))
            if (last is not None) and (last in self.costaccounting_list.keys()):
                self.costaccounting_list[
                    yearid].last_costaccounting = self.costaccounting_list[last]
                self.costaccounting_list[yearid].save()

    def _chartsaccount(self):
        chartsaccount_mdl = apps.get_model("accounting", "ChartsAccount")
        chartsaccount_mdl.objects.all().delete()
        self.chartsaccount_list = {}
        cur = self.old_db.open()
        cur.execute(
            "SELECT id,numCpt,designation,exercice FROM fr_sdlibre_compta_Plan")
        for chartsaccountid, num_cpt, designation, exercice in cur.fetchall():
            num_cpt = convert_code(num_cpt)
            if (len(num_cpt) > 1) and (num_cpt not in ('600000', '700000')):
                self.print_debug(
                    "=> charts of account %s - %d", (num_cpt, exercice))
                try:
                    self.chartsaccount_list[chartsaccountid] = chartsaccount_mdl.objects.get(
                        code=num_cpt, year=self.year_list[exercice])
                except:
                    self.chartsaccount_list[chartsaccountid] = chartsaccount_mdl.objects.create(
                        code=num_cpt, name=designation, year=self.year_list[exercice])
                if (num_cpt[0] == '2') or (num_cpt[0] == '3') or (num_cpt[0:2] == '41') or (num_cpt[0:2] == '45') or (num_cpt[0] == '5'):
                    self.chartsaccount_list[
                        chartsaccountid].type_of_account = 0  # Asset / 'actif'
                if (num_cpt[0] == '4') and (num_cpt[0:2] != '41') and (num_cpt[0:2] != '45'):
                    # Liability / 'passif'
                    self.chartsaccount_list[
                        chartsaccountid].type_of_account = 1
                if num_cpt[0] == '1':
                    # Equity / 'capital'
                    self.chartsaccount_list[
                        chartsaccountid].type_of_account = 2
                if num_cpt[0] == '7':
                    self.chartsaccount_list[
                        chartsaccountid].type_of_account = 3  # Revenue
                if num_cpt[0] == '6':
                    self.chartsaccount_list[
                        chartsaccountid].type_of_account = 4  # Expense
                if num_cpt[0] == '8':
                    self.chartsaccount_list[
                        chartsaccountid].type_of_account = 5  # Contra-accounts
                self.chartsaccount_list[chartsaccountid].save()
            else:
                self.print_debug("=> charts of account %s - XXX", (num_cpt,))
                self.chartsaccount_list[chartsaccountid] = None

    def _extra(self):
        journal_mdl = apps.get_model("accounting", "Journal")
        accountlink_mdl = apps.get_model("accounting", "AccountLink")
        accountlink_mdl.objects.all().delete()
        self.journal_list = {}
        self.journal_list[0] = journal_mdl.objects.get(id=5)
        self.journal_list[1] = journal_mdl.objects.get(id=2)
        self.journal_list[2] = journal_mdl.objects.get(id=3)
        self.journal_list[3] = journal_mdl.objects.get(id=4)
        self.journal_list[4] = journal_mdl.objects.get(id=5)
        self.journal_list[5] = journal_mdl.objects.get(id=1)
        self.accountlink_list = {}
        cur_al = self.old_db.open()
        cur_al.execute(
            "SELECT id FROM fr_sdlibre_compta_raprochement ORDER BY id")
        for (accountlinkid,) in cur_al.fetchall():
            self.accountlink_list[
                accountlinkid] = accountlink_mdl.objects.create()

    def _entryaccount(self):
        def convert_date(current_date):
            try:
                return datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                return datetime.date.today()
        entryaccount_mdl = apps.get_model("accounting", "EntryAccount")
        entryaccount_mdl.objects.all().delete()
        entrylineaccount_mdl = apps.get_model("accounting", "EntryLineAccount")
        entrylineaccount_mdl.objects.all().delete()
        self.entryaccount_list = {}
        self.entrylineaccount_list = {}
        self._extra()
        cur_e = self.old_db.open()
        cur_e.execute(
            "SELECT id, num, dateEcr, datePiece, designation, exercice, point, journal, opeRaproch, analytique FROM fr_sdlibre_compta_Operation")
        for entryaccountid, num, date_ecr, date_piece, designation, exercice, point, journal, operaproch, analytique in cur_e.fetchall():
            self.print_debug(
                "=> entry account %s - %d - %s", (six.text_type(num), exercice, journal))
            self.entryaccount_list[entryaccountid] = entryaccount_mdl.objects.create(num=num, designation=designation,
                                                                                     year=self.year_list[
                                                                                         exercice], date_entry=convert_date(date_ecr), date_value=convert_date(date_piece),
                                                                                     close=point == 'o', journal=self.journal_list[journal])
            if analytique is not None:
                self.entryaccount_list[
                    entryaccountid].costaccounting = self.costaccounting_list[analytique]
            self.entryaccount_list[entryaccountid].editor.before_save(None)
            if operaproch is not None:
                self.entryaccount_list[
                    entryaccountid].link = self.accountlink_list[operaproch]
            self.entryaccount_list[entryaccountid].check_date()
            if isinstance(self.entryaccount_list[entryaccountid].date_entry, datetime.date):
                self.entryaccount_list[entryaccountid].date_entry = self.entryaccount_list[
                    entryaccountid].date_entry.isoformat()
            if self.entryaccount_list[entryaccountid].date_entry > self.year_list[exercice].end.isoformat():
                self.entryaccount_list[entryaccountid].date_entry = self.year_list[
                    exercice].end.isoformat()
            self.entryaccount_list[entryaccountid].save()
        cur_l = self.old_db.open()
        cur_l.execute(
            "SELECT id,numCpt,montant,reference,operation,tiers  FROM fr_sdlibre_compta_Ecriture")
        for entrylineaccountid, num_cpt, montant, reference, operation, tiers in cur_l.fetchall():
            if self.chartsaccount_list[num_cpt] is not None:
                self.print_debug(
                    "=> line entry account %f - %d", (montant, num_cpt))
                current_chartsaccount = self.chartsaccount_list[num_cpt]
                self.entrylineaccount_list[entrylineaccountid] = entrylineaccount_mdl.objects.create(account=current_chartsaccount, entry=self.entryaccount_list[operation],
                                                                                                     amount=montant, reference=reference)
                if (tiers is not None) and (current_chartsaccount.code[0] == '4'):
                    self.entrylineaccount_list[
                        entrylineaccountid].third = self.third_list[tiers]
                    self.entrylineaccount_list[entrylineaccountid].save()

    def _model(self):
        model_mdl = apps.get_model("accounting", "ModelEntry")
        model_mdl.objects.all().delete()
        modelline_mdl = apps.get_model("accounting", "ModelLineEntry")
        modelline_mdl.objects.all().delete()
        self.model_list = {}
        self.modelline_list = {}
        cur_m = self.old_db.open()
        cur_m.execute(
            "SELECT id, journal, designation FROM fr_sdlibre_compta_Model")
        for modelid, journal, designation in cur_m.fetchall():
            self.print_debug("=> model %s", (designation,))
            self.model_list[modelid] = model_mdl.objects.create(
                journal=self.journal_list[journal], designation=designation)

        cur_ml = self.old_db.open()
        cur_ml.execute(
            "SELECT id, model, compte, montant, tiers FROM fr_sdlibre_compta_ModelLigne")
        for modellineid, model, compte, montant, tiers in cur_ml.fetchall():
            self.print_debug("=> model line %d %s", (model, compte))
            self.modelline_list[modellineid] = modelline_mdl.objects.create(
                model=self.model_list[model], code=convert_code(compte), amount=montant)
            if tiers is not None:
                self.modelline_list[modellineid].third = self.third_list[tiers]
                self.modelline_list[modellineid].save()

    def _params(self):
        from lucterios.CORE.models import Parameter
        Parameter.change_value(
            'accounting-system', 'diacamma.accounting.system.french.FrenchSystemAcounting')
        Parameter.change_value("accounting-sizecode", 6)
        cur_p = self.old_db.open()
        cur_p.execute(
            "SELECT paramName,value FROM CORE_extension_params WHERE extensionId LIKE 'fr_sdlibre_compta' and paramName in ('Devise','DeviseOff','PrecDevise')")
        for param_name, param_value in cur_p.fetchall():
            pname = ''
            if param_name == 'Devise':
                pname = 'accounting-devise'
                param_value = decode_html(param_value)
            elif param_name == 'DeviseOff':
                pname = 'accounting-devise-iso'
            elif param_name == 'PrecDevise':
                pname = 'accounting-devise-prec'
            if pname != '':
                self.print_debug(
                    "=> parameter of account %s - %s", (pname, param_value))
                Parameter.change_value(pname, param_value)
        Params.clear()

    def run(self):
        try:
            self._params()
            self._thirds()
            self._years()
            self._costaccounting()
            self._chartsaccount()
            self._entryaccount()
            self._model()
        except:
            import traceback
            traceback.print_exc()
            six.print_("*** Unexpected error: %s ****" % sys.exc_info()[0])
        self.print_info("Nb thirds:%d", len(self.third_list))
        self.print_info("Nb fiscal years:%d", len(self.year_list))
        self.print_info(
            "Nb chart of accounts:%d", len(self.chartsaccount_list))
        self.print_info(
            "Nb entries of account:%d", len(self.entryaccount_list))
        self.print_info(
            "Nb cost accountings:%d", len(self.costaccounting_list))
        self.old_db.objectlinks['third'] = self.third_list
        self.old_db.objectlinks['year'] = self.year_list
        self.old_db.objectlinks['costaccounting'] = self.costaccounting_list
        self.old_db.objectlinks['chartsaccount'] = self.chartsaccount_list
        self.old_db.objectlinks['journal'] = self.journal_list
        self.old_db.objectlinks['entryaccount'] = self.entryaccount_list
