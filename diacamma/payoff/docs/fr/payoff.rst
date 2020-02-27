Règlement des factures
======================

Depuis le module du facturier, si vous l'avez installé, il vous est possible de gérer le règlement des factures validées.

     *Menu Facturier/Facture*

Dans la fenêtre ouverte, filtrez vos factures afin de n'afficher que celles qui sont validées.
Sélectionnez la ou les factures réglées par le tiers et cliquez sur le bouton "Règlement"

    .. image:: payoff.png

Dans la boîte de dialogue, saisissez le détail du règlement reçu du tiers en précisant le mode de paiement ainsi que le  compte bancaire sur lequel imputer ce mouvement financier.

Dans la facture, maintenant figurent le net-à-payer  et le ou les règlements correspondants ainsi que le reste dû.

Chaque règlement génère automatiquement une écriture comptable au journal.

    .. image:: multi-payoff.png

Suivant le type de document sur lequel ce paiement est associé, vous pouvez avoir plusieurs modes de répartition :

 - Par date : le paiement est d'abord ventilé sur la facture la plus ancienne, puis la suivante, etc.
 - Par prorata : le paiement est automatiquement ventilé sur toutes les factures sélectionnées, au prorata de leurs montants. 

Quelque soit le mode de répartition, une seule écriture comptable d'encaissement sera alors passée.
