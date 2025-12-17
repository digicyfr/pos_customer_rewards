
POS Loyalty
===========

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1| |badge2|

A simple, focused loyalty program for Odoo Point of Sale.

**Features**

* Customers earn points based on purchase amount
* Redeem points for discounts (fixed, percentage) or free products
* View points balance in POS customer screen
* Complete transaction history and audit trail
* Configurable point expiration
* Minimum order amount for earning points
* Automatic discount product management

**Table of contents**

.. contents::
   :local:

Configuration
=============

Create Loyalty Program
-----------------------

1. Go to **Point of Sale > Configuration > Loyalty Programs**
2. Click **Create**
3. Configure:
   
   * **Program Name**: Name of your loyalty program
   * **Points per Currency Unit**: How many points per dollar/euro (e.g., 1.0 = 1 point per $1)
   * **Minimum Order Amount**: Minimum purchase to earn points (0 = no minimum)
   * **Points Expire After**: Days until points expire (0 = never expire)

4. Click **Save**

Create Rewards
--------------

1. From the Loyalty Program form, click the **Rewards** smart button
2. Click **Create**
3. Configure:

   * **Reward Name**: Name shown to customers (e.g., "$5 Off")
   * **Points Required**: Points needed to redeem
   * **Reward Type**:

     * Fixed Discount: Specific amount off (e.g., $5)
     * Percentage Discount: Percentage off (e.g., 10%)
     * Free Product: Give a product for free

   * **Discount Amount** or **Discount Percentage** or **Free Product**: Based on reward type

4. Click **Save**
5. Repeat to create multiple rewards (e.g., $5 off for 100 pts, Free Coffee for 50 pts)

Enable in POS
-------------

1. Go to **Point of Sale > Configuration > Point of Sale**
2. Select your POS configuration
3. In the **Loyalty** section, select your **Loyalty Program**
4. Click **Save**
5. Restart your POS session

Usage
=====

Earning Points
--------------

1. Open POS and select a customer
2. Add products to the order
3. Complete the payment
4. Points are automatically awarded based on the purchase amount
5. Customer's points balance is updated

Redeeming Points
----------------

1. Open POS and select a customer with loyalty points
2. Add products to the order
3. On the product screen, click the **Use Points** button
4. A popup shows available rewards and current points balance
5. Select a reward and click **Redeem**
6. The discount or free product is applied to the order
7. Complete the payment
8. Points are automatically deducted

**Important**: Only ONE reward can be redeemed per order

Viewing Points Balance
-----------------------

* **In POS**: Points are displayed next to the customer name in the customer list
* **Backend**: 
  
  * Go to **Contacts**
  * Open a customer
  * View **Loyalty Points** field
  * Click **Loyalty Transactions** smart button to see history

Transaction History
-------------------

1. Go to **Point of Sale > Reporting > Loyalty Transactions**
2. View all point earn/redeem/expire transactions
3. Filter by customer, date range, or transaction type
4. Transactions are immutable (audit trail)

Point Expiration
----------------

If configured, points will expire after the specified number of days.

**Note**: Point expiration is not automatic. You need to:

* Manually call the expiration method on customers
* Or set up a scheduled action to run periodically
* An "expire" transaction is created for the audit trail

Example:

.. code-block:: python

   partner.expire_old_points(program)

Troubleshooting
===============

Common Issues
-------------

**"Use Points" button not appearing**

* Hard refresh browser (Ctrl + Shift + R)
* Check that loyalty program is enabled in POS configuration

**Free Product field not appearing in reward form**

* Update the module: ``odoo -d your_db -u pos_customer_rewards --stop-after-init``
* Restart Odoo service
* Hard refresh browser

**Points not showing for customer**

* Hard refresh browser
* Check that customer has made a validated order
* Verify POS configuration has loyalty program enabled

**"Please select a customer first"**

* Select a customer before clicking "Use Points" button

Bug Tracker
===========

Bugs are tracked on GitHub Issues. In case of trouble, please check there
if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* Digicyfr Polska

Contributors
~~~~~~~~~~~~

* Digicyfr Polska <info@digicyfr.com>

Maintainers
~~~~~~~~~~~

This module is maintained by Digicyfr Polska.

Support
~~~~~~~

* **Website**: https://digicyfr.com
* **Email**: info@digicyfr.com
* **Phone**: +48 695 021 633

