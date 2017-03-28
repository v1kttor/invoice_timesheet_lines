# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import common
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class TestAnalyticLineInvoiceWizard(common.TransactionCase):

    def setUp(self):
        super(TestAnalyticLineInvoiceWizard, self).setUp()
        self.invoice_obj = self.env['account.invoice']
        self.wizard_obj = self.env['analytic.line.invoice.wizard']
        self.aal_obj = self.env['account.analytic.line']
        self.product_obj = self.env['product.product']
        self.account = self.env.ref('analytic.analytic_absences')
        self.project1 = self.env.ref('project.project_project_1')
        self.project2 = self.env.ref('project.project_project_2')
        self.project1.partner_id = self.env.ref('base.res_partner_1')
        self.project2.partner_id = self.env.ref('base.res_partner_2')
        self.project_no_partner = self.env.ref('project.project_project_4')
        self.product = self.product_obj.create({
            'name': 'Table',
            'lst_price': 50.0,
        })

    def assertFloatEqual(self, a, b, invoice_line):
        rounding = invoice_line.currency_id.rounding
        comp = float_compare(a, b, precision_rounding=rounding)
        if comp != 0.0:
            return self.fail('%s != %s') % a, b

    def test_invoiced_lines(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 1.0,
            'project_id': self.project1.id,
            'is_invoiced': True,
        })
        wizard = self.wizard_obj.create({
            'product_id': self.product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        with self.assertRaises(ValidationError):
            wizard.create_lines()

    def test_invoice_line_partners(self):
        aal1 = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 1.0,
            'project_id': self.project1.id,
        })
        aal2 = self.aal_obj.create({
            'name': 'Line2',
            'account_id': self.account.id,
            'date': date(2017, 3, 16),
            'unit_amount': 2.0,
            'project_id': self.project2.id,
        })
        aal_list = [aal1.id, aal2.id]
        wizard = self.wizard_obj.create({
            'product_id': self.product.id,
            'line_ids': [(6, 0, aal_list)],
        })
        action = wizard.create_lines()
        invoices = self.invoice_obj.search(action['domain'])

        self.assertEqual(len(invoices), 2)
        invoice1 = invoices[0]
        invoice2 = invoices[1]

        invoice_line1 = invoice1.invoice_line_ids[0]
        invoice_line2 = invoice2.invoice_line_ids[0]
        self.assertEqual(invoice_line1.quantity, 2.0)
        self.assertEqual(invoice_line2.quantity, 1.0)

        self.assertEqual(invoice1.partner_id.id, aal2.project_id.partner_id.id)
        self.assertEqual(invoice2.partner_id.id, aal1.project_id.partner_id.id)

    def test_invoice_invoice(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2.0,
            'project_id': self.project1.id,
        })
        wizard = self.wizard_obj.create({
            'product_id': self.product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        action = wizard.create_lines()
        invoices = self.invoice_obj.search(action['domain'])

        self.assertEqual(len(invoices), 1)
        invoice = invoices[0]

        self.assertEqual(len(invoice.invoice_line_ids), 1)
        invoice_line = invoice.invoice_line_ids[0]
        self.assertFloatEqual(invoice_line.price_unit, 50.0, invoice_line)

        self.assertEqual(len(invoice_line.invoice_line_tax_ids), 1)
        invoice_line_tax = invoice_line.invoice_line_tax_ids[0]
        product_taxes = self.product.taxes_id[0]
        self.assertEqual(invoice_line_tax, product_taxes)

        self.assertFloatEqual(invoice_line.price_subtotal, 100.0, invoice_line)
        self.assertFloatEqual(invoice_line.quantity, 2.0, invoice_line)

        self.assertEqual(invoice_line.partner_id.id,
                         aal.project_id.partner_id.id)
        self.assertEqual(invoice_line.product_id.name, wizard.product_id.name)

    def test_merge_lines(self):
        aal1 = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 5, 15),
            'unit_amount': 1.0,
            'project_id': self.project1.id,
        })
        aal2 = self.aal_obj.create({
            'name': 'Line2',
            'account_id': self.account.id,
            'date': date(2017, 4, 15),
            'unit_amount': 2.0,
            'project_id': self.project1.id,
        })
        aal3 = self.aal_obj.create({
            'name': 'Line3',
            'account_id': self.account.id,
            'date': date(2017, 6, 15),
            'unit_amount': 3.0,
            'project_id': self.project2.id,
        })
        aal4 = self.aal_obj.create({
            'name': 'Line4',
            'account_id': self.account.id,
            'date': date(2017, 4, 15),
            'unit_amount': 5.0,
            'project_id': self.project2.id,
        })
        aal_list = [aal1.id, aal2.id, aal3.id, aal4.id]
        wizard = self.wizard_obj.create({
            'product_id': self.product.id,
            'line_ids': [(6, 0, aal_list)],
            'merge_timesheets': True,
        })
        action = wizard.create_lines()
        invoices = self.invoice_obj.search(action['domain'])

        self.assertEqual(len(invoices), 2)
        invoice1 = invoices[0]
        invoice2 = invoices[1]

        self.assertEqual(len(invoice1.invoice_line_ids), 1)
        self.assertEqual(len(invoice2.invoice_line_ids), 1)
        invoice_line1 = invoice1.invoice_line_ids[0]
        invoice_line2 = invoice2.invoice_line_ids[0]

        qty_list = [8.0, 3.0]
        self.assertIn(invoice_line1.quantity, qty_list)
        self.assertIn(invoice_line2.quantity, qty_list)

        quantity = invoice_line1.quantity + invoice_line2.quantity
        self.assertFloatEqual(quantity, 11.0, invoice_line1)

        self.assertEqual(invoice_line1.product_id.name, wizard.product_id.name)
        self.assertEqual(invoice_line2.product_id.name, wizard.product_id.name)

    def test_merge_two_lines(self):
        aal1 = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2.0,
            'project_id': self.project1.id,
        })
        aal2 = self.aal_obj.create({
            'name': 'Line2',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 4.0,
            'project_id': self.project1.id,
        })
        aal_list = [aal1.id, aal2.id]
        wizard = self.wizard_obj.create({
            'product_id': self.product.id,
            'line_ids': [(6, 0, aal_list)],
            'merge_timesheets': True,
        })
        action = wizard.create_lines()
        invoices = self.invoice_obj.search(action['domain'])

        self.assertEqual(len(invoices), 1)
        invoice = invoices[0]

        self.assertEqual(len(invoice.invoice_line_ids), 1)
        invoice_line = invoice.invoice_line_ids[0]

        self.assertFloatEqual(invoice_line.quantity, 6.0, invoice_line)
        self.assertEqual(invoice_line.product_id.name, wizard.product_id.name)

    def test_no_customer(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 17),
            'unit_amount': 2.0,
            'project_id': self.project_no_partner.id,
        })
        wizard = self.wizard_obj.create({
            'product_id': self.product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        with self.assertRaises(ValidationError):
            wizard.create_lines()
