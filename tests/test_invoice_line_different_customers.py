# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import common


class TestDifferentCustomers(common.TransactionCase):

    def test_invoice_line_partners(self):
        wz = self.env['analytic.line.invoice.wizard']
        account = self.env.ref('analytic.analytic_absences')
        project = self.env.ref('project.project_project_1')
        project.partner_id = self.env.ref('base.res_partner_2')
        project2 = self.env.ref('project.project_project_2')
        project2.partner_id = self.env.ref('base.res_partner_1')
        aal = self.env['account.analytic.line'].create({
            'name': "Line",
            'account_id': account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2,
            'project_id': project.id,
        })
        aal1 = self.env['account.analytic.line'].create({
            'name': "Line2",
            'account_id': account.id,
            'date': date(2017, 3, 16),
            'unit_amount': 3,
            'project_id': project2.id,
        })
        product = self.env['product.product'].create({
            'name': "Table",
            'lst_price': 50,
        })
        aal_list = [aal1.id, aal.id]
        wizard = wz.create({
            'product_id': product.id,
            'line_ids': [(6, 0, aal_list)],
        })
        wizard.create_lines()
        self.assertEqual(len(wizard.invoices), 2)
        invoice = wizard.invoices[0]
        invoice1 = wizard.invoices[1]
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line1 = invoice1.invoice_line_ids[0]
        self.assertEqual(invoice_line.quantity, 3.0)
        self.assertEqual(invoice_line1.quantity, 2.0)
        self.assertEqual(
            invoice.partner_id.name, aal1.project_id.partner_id.name)
        self.assertEqual(
            invoice1.partner_id.name, aal.project_id.partner_id.name)
