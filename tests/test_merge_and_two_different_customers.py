# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import common


class TestMergeLines(common.TransactionCase):

    def test_merge_lines(self):
        wz = self.env['analytic.line.invoice.wizard']
        account = self.env.ref('analytic.analytic_absences')
        project = self.env.ref('project.project_project_1')
        project1 = self.env.ref('project.project_project_2')
        project.partner_id = self.env.ref('base.res_partner_1')
        project1.partner_id = self.env.ref('base.res_partner_2')
        aals = self.env['account.analytic.line']
        aal = aals.create({
            'name': "Line",
            'account_id': account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2,
            'project_id': project.id,
        })
        aal1 = aals.create({
            'name': "Line2",
            'account_id': account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 4,
            'project_id': project.id,
        })
        aal2 = aals.create({
            'name': "Line3",
            'account_id': account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2,
            'project_id': project1.id,
        })
        aal3 = aals.create({
            'name': "Line4",
            'account_id': account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 4,
            'project_id': project1.id,
        })
        product = self.env['product.product'].create({
            'name': "Table",
            'lst_price': 100,
        })
        aal_list = [aal.id, aal1.id, aal2.id, aal3.id]
        wizard = wz.create({
            'product_id': product.id,
            'line_ids': [(6, 0, aal_list)],
            'merge_timesheets': True,
        })
        wizard.create_lines()
        self.assertEqual(len(wizard.invoices), 2)
        invoices = wizard.invoices
        invoice = invoices[0]
        invoice1 = invoices[1]
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(len(invoice1.invoice_line_ids), 1)
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line1 = invoice1.invoice_line_ids[0]
        self.assertEqual(invoice_line.quantity, 6)
        self.assertEqual(invoice_line1.quantity, 6)
        self.assertEqual(
            invoice_line.product_id.name, wizard.product_id.name)
        self.assertEqual(
            invoice_line1.product_id.name, wizard.product_id.name)
