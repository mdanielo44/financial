# -*- coding: utf-8 -*-
'''
lucterios.contacts package
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

from django.utils import six

from diacamma.accounting.system.default import DefaultSystemAccounting
from os.path import dirname, join
from lucterios.framework.tools import get_icon_path
from lucterios.framework.xferadvance import TITLE_OK, TITLE_CANCEL

GENERAL_MASK = r'^[0-8][0-9]{2}[0-9a-zA-Z]*$'

CASH_MASK = r'^5[0-9][0-9][0-9a-zA-Z]*$'

CASH_MASK_BEGIN = '5'

PROVIDER_MASK = r'^40[0-9][0-9a-zA-Z]*$'

CUSTOMER_MASK = r'^41[0-9][0-9a-zA-Z]*$'

EMPLOYED_MASK = r'^42[0-9][0-9a-zA-Z]*$'

SOCIETARY_MASK = r'^45[0-9][0-9a-zA-Z]*$'

REVENUE_MASK = r'^7[0-9][0-9][0-9a-zA-Z]*$'

EXPENSE_MASK = r'^6[0-9][0-9][0-9a-zA-Z]*$'

THIRD_MASK = "%s|%s|%s|%s" % (
    PROVIDER_MASK, CUSTOMER_MASK, EMPLOYED_MASK, SOCIETARY_MASK)

GENERAL_CHARTS_ACCOUNT = [
    ("100", "10799999", "Compte de capital et réserves", 2),
    ("108", "10899999", "Compte de l'exploitant", 2),
    ("109", "10999999",
     "Actionnaires :capital souscrit non appelé", 2),
    ("110", "11899999",
     "Report à nouveau (solde créditeur)", 2),
    ("119", "11999999",
     "Report à nouveau (solde débiteur)", 2),
    ("120", "12899999",
     "Résultat de l'exercice (bénéfice)", 2),
    ("129", "12999999",
     "Résultat de l'exercice (perte)", 2),
    ("130", "13999999",
     "Subventions d'investissements", 2),
    ("140", "15999999", "Provisions règlementées", 2),
    ("150", "15999999",
     "Provisions pour risques et charges", 2),
    ("160", "16999999",
     "Comptes d'emprunts (ou dettes assimilées)", 2),
    ("170", "17999999",
     "Dettes rattachées à des participations", 2),
    ("180", "18999999", "Comptes de liaison", 2),
    ("190", "19999999", "Fonds dédiés", 2),
    ("200", "20999999",
     "Immobilisations incorporelles", 0),
    ("210", "21999999", "Immobilisations corporelles", 0),
    ("220", "22999999",
     "Immobilisations mises en concession", 0),
    ("230", "23999999", "Immobilisations en cours", 0),
    ("250", "25999999",
     "Parts dans des entreprises liées et créances sur des entreprises liées", 0),
    ("260", "26999999",
     "Participations et créances rattachées à des participations", 0),
    ("270", "27999999",
     "Immobilisations financiéres", 0),
    ("280", "28999999",
     "Amortissements des immobilisations", 0),
    ("290", "29999999",
     "Provisions pour dépréciation des immobilisations", 0),
    ("310", "31999999",
     "Stocks de Matiéres premiéres et fournitures", 0),
    ("320", "32999999",
     "Stocks d'autres approvisionnements", 0),
    ("330", "33999999",
     "En-cours de production de biens ", 0),
    ("340", "34999999",
     "En-cours de production de services", 0),
    ("350", "35999999", "Stocks de produits", 0),
    ("360", "36999999",
     "Stocks provenant d'immobilisations", 0),
    ("370", "37999999", "Stocks de marchandises", 0),
    ("380", "38999999",
     "Stocks en voie d'acheminement, mis en dépét ou donnés en consignation", 0),
    ("390", "39999999",
     "Provisions pour dépréc. comptes de stocks.", 0),
    ("400", "400", "Fournisseurs Collectif", 1),
    ("4000", "40999999",
     "Fournisseurs et comptes rattachés", 1),
    ("410", "410", "Clients Collectif", 0),
    ("4100", "41999999",
     "Clients et comptes rattachés", 0),
    ("420", "42999999",
     "Personnel et comptes rattachés", 1),
    ("430", "43999999",
     "Sécurité sociale et autres organismes sociaux", 1),
    ("440", "44499999",
     "Etat et autres collectivités publiques", 1),
    ("445", "44549999",
     "état - Taxes sur le chiffre d'affaires", 1),
    ("4455", "44559999", "TVA à décaisser", 1),
    ("4456", "44561999", "TVA déductible", 1),
    ("44562", "44562999",
     "TVA déductible sur immobilisations", 1),
    ("44563", "44569999",
     "TVA déductible sur 0 et services", 1),
    ("4457", "44579999", "TVA sur ventes due à l'Etat", 1),
    ("4458", "44999999",
     "Autres impôts et taxes dus à l'état", 1),
    ("447", "44799999",
     "Autres impôts, taxes et versements assimilés", 1),
    ("448", "44899999",
     "état - Charges à payer et produits à recevoir", 1),
    ("449", "44999999",
     "Quotas d'émission à restituer à l'état", 1),
    ("450", "45099999", "Groupe et associés", 0),
    ("451", "45199999", "Groupe", 0),
    ("455", "45599999", "Associés - Comptes courants", 0),
    ("456", "45699999",
     "Associés - Opérations sur le capital", 0),
    ("457", "45799999",
     "Associés - Dividendes à payer", 0),
    ("458", "45899999",
     "Associés - Opérations faites en commun et en G.I.E.", 0),
    ("460", "46999999",
     "Débiteurs divers et créditeurs divers", 1),
    ("470", "47999999",
     "Comptes transitoire ou d'attente", 1),
    ("481", "48199999",
     "Charges à répartir sur plusieurs exercices", 1),
    ("486", "48699999", "Charges constatées d'avance", 1),
    ("487", "48799999", "Produits constatés d'avance", 1),
    ("490", "49999999",
     "Provisions pour dépréciation des comptes de tiers", 1),
    ("500", "50999999",
     "Valeurs mobiliéres de placements", 0),
    ("510", "52999999",
     "Compte de trésorerie, banque, CCP, etc.", 0),
    ("520", "52999999", "Instruments de trésorerie", 0),
    ("530", "53999999", "Compte de caisse", 0),
    ("540", "54999999",
     "Régies d'avances et accréditifs", 0),
    ("580", "58999999", "Virements internes", 0),
    ("590", "59999999",
     "Provisions pour dépréc. comptes financiers", 0),
    ("600", "60299999",
     "Achats de matiéres premiéres, fournitures, etc.", 4),
    ("603", "60399999",
     "Variations des stocks (approv., marchandises, ...)", 4),
    ("604", "60699999",
     "Achats et fournitures divers non stockés", 4),
    ("607", "60799999", "Achats de marchandises", 4),
    ("608", "60899999", "Frais divers sur achats", 4),
    ("609", "60999999",
     "Rabais, remise, ristournes obtenues sur achats", 4),
    ("610", "62999999", "Services extérieurs", 4),
    ("630", "63999999",
     "Impéts, taxes et versements assimilés", 4),
    ("640", "64499999", "Rémunération du personnel", 4),
    ("645", "64699999",
     "Charges de sécurité sociale et prévoyance", 4),
    ("647", "64999999", "Autres charges sociales", 4),
    ("650", "65499999",
     "Autres charges de gestion courante", 4),
    ("655", "65599999",
     "Quote-part de résultat sur opérations faites en commun", 4),
    ("656", "65999999",
     "Autres charges de gestion courante", 4),
    ("660", "66999999", "Charges financiéres", 4),
    ("670", "67999999", "Charges exceptionnelles", 4),
    ("680", "68999999",
     "Dotations aux amortissements et provisions", 4),
    ("691", "69199999", "Participations des salariés", 4),
    ("695", "69899999", "Impôts sur bénéfices", 4),
    ("699", "699", "Compte pour résultat positif", 4),
    ("700", "70899999",
     "Ventes de produits, services, marchandises, etc.", 3),
    ("709", "70999999",
     "Rabais, remises, ristournes accordés", 3),
    ("710", "71999999",
     "Variations des stocks de production", 3),
    ("720", "72999999", "Production immobilisée", 3),
    ("730", "73999999",
     "Produits sur opérations à long terme", 3),
    ("740", "74999999", "Subventions d'exploitation", 3),
    ("750", "75499999",
     "Autres produits de gestion courante", 3),
    ("755", "75599999",
     "Quote-part de résultat sur opérations faites en commun", 3),
    ("756", "75999999",
     "Autres produits de gestion courante", 3),
    ("760", "76999999", "Produits financiers", 3),
    ("770", "77999999", "Produits exceptionnels", 3),
    ("780", "79899999", "Autres produits divers", 3),
    ("799", "799", "Compte pour résultat négatif", 3),
    ("80", "80999999", "Engagements", 5),
    ("86", "86999999",
     "Emplois des contributions volontaires en nature", 5),
    ("87", "87999999",
     "Contributions volontaires en nature", 5),
    ("88", "88999999",
     "Résultat en instance d'affectation", 5),
    ("89", "89999999", "Bilan", 5)]


def find_charts(code):
    current_charts = None
    for chart_item in GENERAL_CHARTS_ACCOUNT:
        if (chart_item[0] <= code) and (code <= chart_item[1]):
            current_charts = chart_item
            break
    return current_charts


class FrenchSystemAcounting(DefaultSystemAccounting):

    def get_general_mask(self):
        return GENERAL_MASK

    def get_cash_mask(self):
        return CASH_MASK

    def get_cash_begin(self):
        return CASH_MASK_BEGIN

    def get_provider_mask(self):
        return PROVIDER_MASK

    def get_customer_mask(self):
        return CUSTOMER_MASK

    def get_employed_mask(self):
        return EMPLOYED_MASK

    def get_societary_mask(self):
        return SOCIETARY_MASK

    def get_third_mask(self):
        return THIRD_MASK

    def get_revenue_mask(self):
        return REVENUE_MASK

    def get_expence_mask(self):
        return EXPENSE_MASK

    def new_charts_account(self, code):
        code = code.strip()
        if code == '':
            return '', -1
        pattern = re.compile(GENERAL_MASK)
        if pattern.match(code):
            current_charts = find_charts(code)
            if current_charts is not None:
                return current_charts[2], current_charts[3]
        return '', -2

    def _create_custom_for_profit(self, year, custom, val_profit):
        from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm, XferCompSelect
        from diacamma.accounting.models import format_devise
        if val_profit > 0.0001:
            type_profit = 'bénéfice'
        else:
            type_profit = 'déficite'
        img = XferCompImage("img")
        img.set_location(0, 0)
        img.set_value(get_icon_path("diacamma.accounting/images/account.png"))
        custom.add_component(img)
        lbl = XferCompLabelForm("title")
        lbl.set_value_as_headername("Bénéfices et Pertes")
        lbl.set_location(1, 0)
        custom.add_component(lbl)
        text = "{[i]}Vous avez un %s de %s.{[br/]}Vous devez definir sur quel compte l'affecter.{[br/]}{[/i]}" % (
            type_profit, format_devise(val_profit, 4))
        text += "{[br/]}En validant, vous commencerez '%s'{[br/]}{[br/]}{[i]}{[u]}Attention:{[/u]} Votre report à nouveau doit être totalement fait.{[/i]}" % six.text_type(
            year)
        lbl = XferCompLabelForm("info")
        lbl.set_value(text)
        lbl.set_location(0, 1, 2)
        custom.add_component(lbl)
        sel_cmpt = []
        for account in year.chartsaccount_set.all().filter(code__startswith='10').order_by('code'):
            sel_cmpt.append((account.id, six.text_type(account)))
        sel = XferCompSelect("profit_account")
        sel.set_select(sel_cmpt)
        sel.set_location(1, 2)
        custom.add_component(sel)
        return custom

    def _get_profit(self, year):
        from diacamma.accounting.models import EntryLineAccount, get_amount_sum
        from django.db.models.aggregates import Sum
        from django.db.models import Q
        query = Q(account__code__startswith='110') | Q(
            account__code__startswith='119')
        query &= Q(account__year=year)
        val_profit = get_amount_sum(EntryLineAccount.objects.filter(
            query).aggregate(Sum('amount')))
        return val_profit

    def _create_profit_entry(self, year, profit_account):
        from diacamma.accounting.models import Journal, EntryAccount, EntryLineAccount, ChartsAccount
        from django.db.models import Q
        paym_journ = Journal.objects.get(id=1)
        paym_desig = 'Affectation des bénéfices/pertes'
        new_entry = EntryAccount.objects.create(
            year=year, journal=paym_journ, designation=paym_desig, date_value=year.begin)
        query = Q(account__code__startswith='110') | Q(
            account__code__startswith='119')
        query &= Q(account__year=year)
        sum_profit = 0
        for new_line in EntryLineAccount.objects.filter(query):
            sum_profit += new_line.amount
            new_line.id = None
            new_line.entry = new_entry
            new_line.amount = -1 * new_line.amount
            new_line.save()
        new_line = EntryLineAccount()
        new_line.entry = new_entry
        new_line.amount = sum_profit
        new_line.account = ChartsAccount.objects.get(
            id=profit_account)
        new_line.save()
        new_entry.closed()
        return True

    def check_begin(self, year, xfer):
        profit_account = xfer.getparam('profit_account', 0)
        if profit_account > 0:
            return self._create_profit_entry(year, profit_account)
        val_profit = self._get_profit(year)
        if abs(val_profit) > 0.0001:
            from lucterios.framework.tools import WrapAction, CLOSE_YES, FORMTYPE_MODAL
            custom = xfer.create_custom()
            self._create_custom_for_profit(year, custom, val_profit)
            custom.add_action(xfer.get_action(TITLE_OK, "images/ok.png"), modal=FORMTYPE_MODAL, close=CLOSE_YES)
            custom.add_action(WrapAction(TITLE_CANCEL, "images/cancel.png"))
            return False
        else:
            text = "Voulez-vous commencer '%s'? {[br/]}{[br/]}{[i]}{[u]}Attention:{[/u]} Votre report à nouveau doit être totalement fait.{[/i]}" % six.text_type(
                year)
            return xfer.confirme(text)

    def _create_result_entry(self, year):
        revenue = year.total_revenue
        expense = year.total_expense
        if abs(expense - revenue) > 0.0001:
            from diacamma.accounting.models import Journal, EntryAccount
            end_journ = Journal.objects.get(id=5)
            end_desig = "Cloture d'exercice - Résultat"
            new_entry = EntryAccount.objects.create(
                year=year, journal=end_journ, designation=end_desig, date_value=year.end)
            if expense > revenue:
                new_entry.add_entry_line(revenue - expense, '129')
            else:
                new_entry.add_entry_line(revenue - expense, '120')
            new_entry.closed(check_balance=False)

    def _create_thirds_ending_entry(self, year):
        from diacamma.accounting.models import get_amount_sum, Journal, EntryAccount, EntryLineAccount, ChartsAccount, Third
        from django.db.models.aggregates import Sum
        sum40 = get_amount_sum(EntryLineAccount.objects.filter(
            account__code__startswith='401', account__year=year).aggregate(Sum('amount')))
        sum41 = get_amount_sum(EntryLineAccount.objects.filter(
            account__code__startswith='411', account__year=year).aggregate(Sum('amount')))
        sum42 = get_amount_sum(EntryLineAccount.objects.filter(
            account__code__startswith='421', account__year=year).aggregate(Sum('amount')))
        sum45 = get_amount_sum(EntryLineAccount.objects.filter(
            account__code__startswith='450', account__year=year).aggregate(Sum('amount')))
        if (abs(sum40) > 0.001) or (abs(sum41) > 0.001) or (abs(sum42) > 0.001) or (abs(sum45) > 0.001):
            end_journ = Journal.objects.get(id=5)
            end_desig = "Cloture d'exercice - Résultat"
            new_entry = EntryAccount.objects.create(
                year=year, journal=end_journ, designation=end_desig, date_value=year.end)
            for data_line in EntryLineAccount.objects.filter(account__code__regex=THIRD_MASK, account__year=year).values('account', 'third').annotate(data_sum=Sum('amount')):
                if abs(data_line['data_sum']) > 0.0001:
                    new_line = EntryLineAccount()
                    new_line.entry = new_entry
                    new_line.amount = -1 * data_line['data_sum']
                    new_line.account = ChartsAccount.objects.get(
                        id=data_line['account'])
                    if data_line['third'] is not None:
                        new_line.third = Third.objects.get(
                            id=data_line['third'])
                    new_line.save()
            new_entry.add_entry_line(sum40, '401')
            new_entry.add_entry_line(sum41, '411')
            new_entry.add_entry_line(sum42, '421')
            new_entry.add_entry_line(sum45, '450')
            new_entry.closed()

    def finalize_year(self, year):
        self._create_result_entry(year)
        self._create_thirds_ending_entry(year)

    def _create_report_lastyearresult(self, year, import_result):
        from diacamma.accounting.models import Journal, EntryAccount
        end_journ = Journal.objects.get(id=1)
        end_desig = "Report à nouveau - Bilan"
        new_entry = EntryAccount.objects.create(
            year=year, journal=end_journ, designation=end_desig, date_value=year.begin)
        for charts_account in year.last_fiscalyear.chartsaccount_set.filter(type_of_account__in=(0, 1, 2)):
            if import_result and charts_account.code[:3] == '120':
                code = "110"
                name = None
            elif import_result and charts_account.code[:3] == '129':
                code = "119"
                name = None
            else:
                code = charts_account.code
                name = charts_account.name
            new_entry.add_entry_line(charts_account.get_current_validated(), code, name)
        new_entry.closed()

    def _create_report_third(self, year):
        from diacamma.accounting.models import Journal, EntryAccount
        last_entry_account = list(
            year.last_fiscalyear.entryaccount_set.filter(journal__id=5).order_by('num'))[-1]
        end_journ = Journal.objects.get(id=1)
        end_desig = "Report à nouveau - Dette tiers"
        new_entry = EntryAccount.objects.create(
            year=year, journal=end_journ, designation=end_desig, date_value=year.begin)
        for entry_line in last_entry_account.entrylineaccount_set.all():
            if re.match(THIRD_MASK, entry_line.account.code):
                new_entry.add_entry_line(-1 * entry_line.amount,
                                         entry_line.account.code, entry_line.account.name, entry_line.third)
        new_entry.closed()

    def import_lastyear(self, year, import_result):
        self._create_report_lastyearresult(year, import_result)
        self._create_report_third(year)
        return

    def get_export_xmlfiles(self):
        file_path = dirname(__file__)
        return (join(file_path, 'french_accountexport.xml'), join(file_path, 'french_fichedescriptive_6709.xsd'))
