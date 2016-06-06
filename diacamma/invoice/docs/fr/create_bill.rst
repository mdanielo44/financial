Création de facture
===================

Création
--------

Depuis le menu *Finance/Facturier/Les factures* vous pouvez éditer ou ajouter une nouvelle facture.

Commencez par définir le type de document (devis, facture, reçu ou avoir) que vous souhaitez créer ainsi que la date d'émission et un commentaire qui figurera dessus.

Dans cette facture, vous devez préciser le client associé, c'est à dire le tiers comptable imputable de l'opération.

.. image:: bill_edit.png

Ensuite ajoutez ou enlevez autant d'articles que vous le désirez.

.. image:: add_article.png

Par défaut, vous obtenez la désignation et le prix par défaut de l'article sélectionné, mais l'ensemble est modifiable. Vous pouvez choisir aussi l'article divers: aucune information par défaut n'est alors proposé.

Changement d'état
-----------------

Depuis le menu *Finance/Facturier/Les factures* vous pouvez consulter les factures en cours, validé ou fini.

Un devis, une facture, un reçu ou un avoir dans l'état « en cours » est un document en cours de conception et il n'est pas encore envoyé au client.

Depuis la fiche du document, vous pouvez le valider: il devient alors imprimable et non modifiable.

Dans ces deux cas, une écriture comptable est alors automatiquement générée.

Un devis validé peut facilement être transformé en facture dans le cas de son acceptation par votre client. La facture ainsi créé se retrouve alors dans l'état « en cours » pour vous permettre de la réajuster.

Une fois qu'une facture (ou un avoir) est considéré comme terminée (c'est à dire réglée ou définie comme pertes et profits), vous pouvez définir son état à «fini».

Depuis une facture « fini », il vous est possible de créer un avoir correspondant à l'état « en cours ». Cette fonctionnalité vous sera utile si vous êtes amené à rembourser un client d'un bien ou un service précédemment facturé.

Impression
----------

Depuis la fiche d'un document (devis, facture, reçu ou avoir) vous pouvez à tout moment imprimer ou ré-impriment celui-ci s'il n'est pas à l'état «en cours».

Paiement
--------

Si ceux-ci sont configurés (menu "Administration/Configuration du règlement"), vous pouvez consulter les moyens de paiement d'une facture, d'un reçu ou d'un devis.
Si vous l'envoyez par courriel, vous pouvez également les faire apparaitre dans votre message.

Dans le cas d'un paiement via PayPal, si votre _Diacamma_ est accessible par internet, le logiciel sera automatiquement notifié du règlement.
Dans le cas d'un devis, celui-ci sera automatiquement archivé et une facture équivalente sera générée.
Un nouveau réglement sera ajouté dans votre facture.

Dans l'écran "Financier/Transactions bancaires", vous pouvez consulté précisement la notification reçu de PayPal.
En cas d'état "échec", la raison est alors précisé: il vous faudra manuellement vérifier votre compte PayPal et rétablir l'éventuellement paiment erroné manuellement.

 
 