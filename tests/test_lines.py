# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import common


class TestInvoiceLine(common.TransactionCase):

    def test_invoice_invoice(self):
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
        })
        product = self.env['product.product'].create({
            'name': "Table",
            'lst_price': 50,
        })
        wizard = wz.create({
            'product_id': product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        wizard.create_lines()
        self.assertEqual(len(wizard.invoices), 1)
        invoice = wizard.invoices[0]
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(invoice_line.price_unit, 50)
        self.assertEqual(len(invoice_line.invoice_line_tax_ids), 1)
        invoice_line_tax = invoice_line.invoice_line_tax_ids[0]
        product_taxes = product.taxes_id[0]
        self.assertEqual(invoice_line_tax, product_taxes)
        self.assertEqual(invoice_line.price_subtotal, 100)
        self.assertEqual(invoice_line.quantity, 2.0)
        self.assertEqual(invoice_line.product_id.name, wizard.product_id.name)
        self.assertEqual(
            invoice_line.partner_id.name, aal.project_id.partner_id.name)
