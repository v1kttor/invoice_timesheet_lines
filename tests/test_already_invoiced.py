# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestAlreadyInvoicedLine(common.TransactionCase):

    def test_invoiced_lines(self):
        wz = self.env['analytic.line.invoice.wizard']
        account = self.env.ref('analytic.analytic_absences')
        project = self.env.ref('project.project_project_1')
        project.partner_id = self.env.ref('base.res_partner_2')
        aal = self.env['account.analytic.line'].create({
            'name': "Line",
            'account_id': account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2,
            'project_id': project.id,
            'is_invoiced': True,
        })
        product = self.env['product.product'].create({
            'name': "Table",
            'lst_price': 50,
        })
        wizard = wz.create({
            'product_id': product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        with self.assertRaises(ValidationError):
            wizard.create_lines()
