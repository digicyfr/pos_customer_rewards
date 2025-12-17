# Copyright 2024 Digicyfr Polska
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'POS Customer Rewards',
    'version': '17.0.1.2.0',
    'category': 'Point of Sale',
    'summary': 'Simple loyalty program for Point of Sale',
    'description': """
POS Loyalty
===========

A simple, focused loyalty module for Odoo Point of Sale.

Features
--------
* Points Earning - Customers earn points based on purchase amount
* Points Redemption - Multiple reward options (fixed or percentage discount)
* View Balance - Display points balance in POS customer screen
* Points History - Track all earn/redeem transactions
* Point Expiration - Simple expiration after X days (configurable)
* Minimum Order - Require minimum purchase to earn points

Configuration
-------------
1. Go to Point of Sale > Configuration > Loyalty Programs
2. Create a loyalty program with earning rate and expiration settings
3. Add rewards to the program
4. Enable the program in your POS configuration

Note: The loyalty discount product is automatically created and managed by the module.
No manual product configuration is required.

Usage
-----
1. Select a customer in POS
2. Complete a purchase to earn points
3. Click "Use Points" to redeem rewards
4. Points are automatically updated after order validation

Support
-------
* Website: https://digicyfr.com
* Email: info@digicyfr.com
* Phone: +48 695 021 633
    """,
    'author': 'Digicyfr Polska',
    'website': 'https://digicyfr.com',
    'support': 'info@digicyfr.com',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'views/loyalty_program_views.xml',
        'views/loyalty_reward_views.xml',
        'views/loyalty_transaction_views.xml',
        'views/res_partner_views.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
        'views/menu_views.xml',
        'wizard/redeem_points_wizard_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_customer_rewards/static/src/**/*.js',
            'pos_customer_rewards/static/src/**/*.xml',
            'pos_customer_rewards/static/src/css/*.css',
        ],
    },
    'images': [
        'static/description/images/main_screenshot.png',
        'static/description/images/LR-2.png',
        'static/description/images/LR-3.png',
        'static/description/images/LR-4.png',
        'static/description/images/LR-5.png',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
