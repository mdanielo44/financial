Create invoice
==============

Creation
--------

From the menu *Financial/invoice/Bill* you can edit or add a new invoice.

Start by defining the type of document (estimate, invoice, receipt or have) that you want to create and the date of issuance and a comment that will appear on it.

In this bill, you must specify the associated client, ie the accounting thirds attributable to the operation.

.. Image :: bill_edit.png

Then add or remove as many items as you wish.

.. Image :: add_article.png

By default, you get the name and price of default of the selected item, but the whole is changed. You can also choose various article: no default information is then proposed.

Change of state
---------------

From the menu *Financial/invoice/Bill* you can view open invoices validated or over.

A quote, invoice, receipt, or have in the "Now" state is a document under development and it is not sent to the client.

Since the document card, you can validate it: it becomes printable and non-modifiable.

In both cases, an accounting entry is then automatically generated.

A validated quote can easily be turned into invoice in the event of acceptance by your customer. The invoice thus created is then in the state "in progress" to allow you to readjust.

Once an invoice (or credit) is considered complete (ie regulated or defined as profit and loss), you can set its status to "finished".

Since an invoice "finished", it is possible to create an asset corresponding to the state "in progress". This feature is useful if you are required to repay a customer of a good or a previously charged service.

Printing
--------

Since the profile of a document (estimate, invoice, receipt or have) you can at any time print or re-print it if it is not in the state "in progress".

Payoff
------

If they are configured ("Administration/Payoff configuration"), you can view the payment of an invoice, a receipt or a quotation.
If you send it by email, you can also make them appear in your message.

In the case of a payment via PayPal, if your _Diacamma_ is accessible via the Internet, the software will be automatically notified of the regulation.
For a quotation, it will be automatically archived and a similar bill will be generated.
A new regulation will be added to your bill.

In the "Financial / Banking Transactions" screen, you can consulted precisely the notification received from PayPal.
If state "failure", the reason is then clear: you have to manually check your PayPal account and restore possibly erroneous payment manually.
