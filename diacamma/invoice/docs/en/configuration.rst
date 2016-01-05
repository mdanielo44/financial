Setup and configuration
=======================

Default Account Codes
---------------------

This module is closely related to the accounting module, a number of default account codes are required.

To generate the corresponding accounting entries for invoices entered with unreferenced items, you must specify the account code of Sale (Class 7) linked to this type of article. By default, the account code sales service is defined.

To achieve a discount on an item, you must specify the account code charge of sale of that reduction.
In the case of cash settlement, you must specify the bank account code associated with your case.

The VAT configuration
---------------------

From the menu *Management/Modules (conf.)/Invoice configuration*, you can completely configure the management of your submission to VAT.

.. Image :: vat.png

To begin, you must define how to bid by selecting your mode of application:

 - VAT not applicable
	You are not subject to VAT. All your invoices are made duty free.
 - Priced
    You are subject to VAT. You make the choice to edit your bills with the amounts of duty free items.
 - All taxes included price
    You are subject to VAT. You make the choice to edit your bills with the amounts of items including tax.

Also specify the accounting account imputation of these taxes.

Set all the tax rates at which sales are subject. The default tax will be applied to the free article (without reference).

The VAT invoice
---------------

If you are subject to VAT, the issue of the invoice changes slightly

In addition to state whether the items are in net amount or VAT, you have the bottom of the invoice total tax-screen, inclusive of tax and the total amount of taxes.

.. Image :: bill_vat.png

Moreover, in printing the invoice, a detailed breakdown of taxes appears in VAT rates.
