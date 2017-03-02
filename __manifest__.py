# -*- coding: utf-8 -*-
{
    'name': "Invoice Timesheet Lines",
    'summary': '',
    'description': '',
    'author': "Viktoras",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '10.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/invoice_timesheet.xml'
    ],
}
