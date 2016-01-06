Exercice
========

Paramétrages
------------

.. image:: parameters.png

Initialement, vous pouvez définir ici le type de système comptable que
vous voulez utiliser (ex: Plan comptable générale Français). 
*Attention:* une fois défini, ce système n'est plus modifiable.

Vous pouvez changer également la monnaie courrante de votre comptabilité.

Création d'un exercice comptable
--------------------------------

Pour créer un exercice comptable, rendez vous dans le menu *Administration/Modules (conf.)/Configuration comptable*.

.. image:: fiscalyear_list.png

De là, cliquez sur Ajouter afin de faire apparaître le formulaire vous permettant de renseigner les bornes de l'exercice

.. image:: fiscalyear_create.png

Indiquez la date de début (celle-ci doit étre le lendemain de la date
de clôture de l'exercice précédent) et la date de fin (au maximum 2 ans
aprés le début de l'exercice) de l'exercice puis cliquez sur le bouton
OK.

Votre nouvel exercice sera alors disponible dans la
liste des exercices. Pour en continuer la création, il vous faudra le
sélectionner dans la liste et cliquer sur le bouton Activer afin de
pouvoir travailler dessus par défaut.

Fermez maintenant la liste des exercices afin de vous rendre dans la comptabilité et
pouvoir créer le plan comptable de l'exercice ainsi qu'affecter le
report à nouveau avant de pouvoir commencer éà saisir des écritures.

Pour ce faire, rendrez-vous dans le menu *Financier/Comptabilité/plan	comptable*

.. image:: account_list.png

Ici, commencez par créer les comptes de base de votre exercice.

Si vous avez déjà un précédent exercice, vous pouvez en importer la liste de code comptable.

Une fois ceci fait, plusieurs choix se présentent à vous:
 - Il s'agit de votre premier exercice comptable
	Vous venez de créer votre structure, vous n'avez pas de report à nouveau, cliquez donc dès maintenant sur le bouton commencer, vous aurez alors achevé la création de votre exercice.
 - Il ne s'agit pas de votre premier exercice mais vous n'utilisiez pas ce logiciel avant
	Il va falloir saisir manuellement votre report à nouveau.
	Pour cela, sortez du plan comptable de l'exercice, entrez dans la liste des écritures et saisissez manuellement une écriture complète, cohérente et équilibrée pour votre report à nouveau.
	Une fois ceci fait, retournez dans votre plan comptable pour cliquer sur commencer.
 - Il ne s'agit pas de votre premier exercice et vous utilisiez déjà ce logiciel
	Utilisez le bouton "report à nouveau"" afin d'importer le résultat de l'exercice précédent.
	Comme il n'est pas possible de commencer un exercice avec un résultat (qu'il soit bénéficiaire ou déficitaire).
	Vous devez avant de commencer votre exercice, ventiler cette somme sur un compte de capitaux (capital, réserve, ..).
	La décision de cette affectation est prise par le conseil d'administration sous le contrôle de votre vérificateur aux comptes.
	Pour cela, vous pouvez créer une écriture spécifique (journal 'report à nouveau') ou utilisez le questionnaire l'or du commencement de l'exercice.
	Pour commencer l'exercice, clique sur le bouton afin de clore cette phase de création.

Création, modification et édition de comptes dans le plan
---------------------------------------------------------

Plaçons nous dans le menu *finance/comptabilité/plan comptable de l'exercice*.

A tout moment au cours d'un exercice vous pouvez être amener à ajouter un nouveau compte dans votre plan.

.. image:: account_new.png

Référez vous aux codes légaux définis par la réglementation de votre pays pour définir correctement les 3 premiers chiffres.
Pour les associations dépendant du droit français, vous pourrez trouver des informations sur le site du gouvernement des finances français (http://www.minefe.gouv.fr/themes/entreprises/compta_entreprises/index.htm).
Les 3 derniers chiffres du compte vous sont propres suivant votre besoin. Modifiez la désignation pour simplifier l'identification de votre compte.

Si vous vous étes trompé, vous pouvez changer le compte et sa désignation. Si des écritures ont été saisies avec ce compte, elles seront automatiquement migrées.

Par contre, le nouveau compte doit rester dans la même catégorie comptable.
Vous pouvez consulter un compte précis. Vous pouvez alors voir
l'ensemble des lignes d'écritures associées à ce compte, ainsi que la
valeur du compte au début (report à nouveau) et la valeur actuelle.

.. image:: account_edit.png

Il vous est aussi possible de supprimer un compte du plan si aucune opération n'y a été réalisée.

Clôture d'un exercice
---------------------

A la fin de la période, vous devez clôturer votre exercice. Cette
opération, définitive, se réalise sous le contrôle de votre
vérificateur aux comptes.
Dans le menu *Financier/Comptabilité/plan comptable*, cliquez sur le bouton "Clôturer".

**Attention:** Toutes les écritures doivent être validées avant de commencer cette procédure.

La phase de validation va réaliser un traitement consistant à
créer une série d'écritures de fin d'exercice résumant le résultat et
les dettes tiers (factures clients ou fournisseurs transmises mais pas encore réglées).
