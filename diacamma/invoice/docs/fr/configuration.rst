Configuration et paramétrage
============================

Codes comptables par défaut
---------------------------

Ce module est intimement lié au module de gestion comptable, un certain nombre de codes comptables par défaut sont nécessaires.

Pour pouvoir générer les écritures comptables correspondants aux factures saisies avec des articles non référencés, vous devez préciser le code comptable de vente (classe 7) lié a ce type de d'article. Par défaut, le code comptable de vente de service est défini.

Pour réaliser une réduction sur un article, vous devez préciser le code comptable de vente à imputer de cette réduction.
Dans le cas de règlement en liquide, il vous faut préciser le code comptable de banque associé à votre caisse.

La configuration de la TVA
--------------------------

Depuis le menu *administration/Modules (conf.)/Configuration du facturier*, vous pouvez complètement configurer la gestion de votre soumission à la TVA.

.. image:: vat.png

Pour commencer, vous devez définir les modalités de soumission en sélectionnant votre mode d'application:

 - TVA non applicable
	Vous n'êtes pas soumis à la TVA. L'ensemble de vos factures sont réalisées hors-taxe.
 - Prix HT
    Vous êtes soumis à la TVA. Vous faites le choix d'éditer vos factures avec les montants des articles en hors-taxe.
 - Prix TTC
    Vous êtes soumis à la TVA. Vous faites le choix d'éditer vos factures avec les montants des articles toutes taxes comprises. 

Précisez également le compte comptable d'imputation de ces taxes.

Définissez l'ensemble des taux de taxes auxquels vos ventes sont soumises. La taxe par défaut sera celle appliquée à l'article libre (sans référence).

La facture avec TVA
-------------------

Si vous êtes soumis à la TVA, l'édition de la facture change un peu

En plus de préciser si les articles sont en montant HT ou TTC, vous avez en bas de l'écran le total de la facture hors-taxe, taxes comprises ainsi que le montant total des taxes.

.. image:: bill_vat.png

De plus, dans l'impression de la facture, un sous-détail des taxes apparait par taux de TVA.