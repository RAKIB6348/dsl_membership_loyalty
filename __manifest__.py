# -*- coding: utf-8 -*-
{
    'name': "DSL Membership Loyalty",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'portal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/membership_dashboard_views.xml',
        'views/menu_views.xml',
        'views/res_partner_views.xml',
        'views/loyalty_point_wizard_views.xml',
        'views/membership_portal_templates.xml',
        'views/agent_portal_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

