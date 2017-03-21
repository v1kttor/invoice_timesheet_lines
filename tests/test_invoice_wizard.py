# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import common
from odoo.tools import float_compare
from odoo.exceptions import ValidationError, UserError


class TestAnalyticLineInvoiceWizard(common.TransactionCase):

    def setUp(self):
        super(TestAnalyticLineInvoiceWizard, self).setUp()
        self.wizard_obj = self.env['analytic.line.invoice.wizard']
        self.aal_obj = self.env['account.analytic.line']
        self.product_obj = self.env['product.product']
        self.account = self.env.ref('analytic.analytic_absences')
        self.project = self.env.ref('project.project_project_1')
        self.project2 = self.env.ref('project.project_project_2')
        self.project.partner_id = self.env.ref('base.res_partner_1')
        self.project2.partner_id = self.env.ref('base.res_partner_2')
        self.project_no_partner = self.env.ref('project.project_project_3')

    def assertFloatEqual(self, a, b):
        compare = float_compare(a, b)
        return compare

    def test_invoiced_lines(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 1,
            'project_id': self.project.id,
            'is_invoiced': True,
        })
        product = self.product_obj.create({
            'name': 'Table',
            'lst_price': 50,
        })
        wizard = self.wizard_obj.create({
            'product_id': product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        with self.assertRaises(ValidationError):
            wizard.create_lines()

    def test_invoice_line_partners(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 1,
            'project_id': self.project.id,
        })
        aal1 = self.aal_obj.create({
            'name': 'Line2',
            'account_id': self.account.id,
            'date': date(2017, 3, 16),
            'unit_amount': 2,
            'project_id': self.project2.id,
        })
        product = self.product_obj.create({
            'name': 'Table',
            'lst_price': 50,
        })
        aal_list = [aal1.id, aal.id]
        wizard = self.wizard_obj.create({
            'product_id': product.id,
            'line_ids': [(6, 0, aal_list)],
        })
        wizard.create_lines()
        self.assertEqual(len(wizard.invoices), 2)
        invoice = wizard.invoices[0]
        invoice1 = wizard.invoices[1]
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line1 = invoice1.invoice_line_ids[0]
        self.assertEqual(invoice_line.quantity, 2.0)
        self.assertEqual(invoice_line1.quantity, 1.0)
        self.assertEqual(
            invoice.partner_id.name, aal1.project_id.partner_id.name)
        self.assertEqual(
            invoice1.partner_id.name, aal.project_id.partner_id.name)

    def test_invoice_invoice(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2,
            'project_id': self.project.id,
        })
        product = self.product_obj.create({
            'name': 'Table',
            'lst_price': 50,
        })
        wizard = self.wizard_obj.create({
            'product_id': product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        wizard.create_lines()
        self.assertEqual(len(wizard.invoices), 1)
        invoice = wizard.invoices[0]
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(invoice_line.price_unit, 50)
        # self.assertFloatEqual(invoice_line.price_unit, 50)
        self.assertEqual(len(invoice_line.invoice_line_tax_ids), 1)
        invoice_line_tax = invoice_line.invoice_line_tax_ids[0]
        product_taxes = product.taxes_id[0]
        self.assertEqual(invoice_line_tax, product_taxes)
        self.assertEqual(invoice_line.price_subtotal, 100)
        self.assertEqual(invoice_line.quantity, 2.0)
        self.assertEqual(invoice_line.product_id.name, wizard.product_id.name)
        self.assertEqual(
            invoice_line.partner_id.name, aal.project_id.partner_id.name)

    def test_merge_lines(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 1,
            'project_id': self.project.id,
        })
        aal1 = self.aal_obj.create({
            'name': 'Line2',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2,
            'project_id': self.project.id,
        })
        aal2 = self.aal_obj.create({
            'name': 'Line3',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 3,
            'project_id': self.project2.id,
        })
        aal3 = self.aal_obj.create({
            'name': 'Line4',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 5,
            'project_id': self.project2.id,
        })
        product = self.product_obj.create({
            'name': 'Table',
            'lst_price': 100,
        })
        aal_list = [aal.id, aal1.id, aal2.id, aal3.id]
        wizard = self.wizard_obj.create({
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
        self.assertEqual(invoice_line.quantity, 3)
        self.assertEqual(invoice_line1.quantity, 8)
        self.assertEqual(
            invoice_line.product_id.name, wizard.product_id.name)
        self.assertEqual(
            invoice_line1.product_id.name, wizard.product_id.name)

    def test_merge_two_lines(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 2,
            'project_id': self.project.id,
        })
        aal1 = self.aal_obj.create({
            'name': 'Line2',
            'account_id': self.account.id,
            'date': date(2017, 3, 15),
            'unit_amount': 4,
            'project_id': self.project.id,
        })
        product = self.product_obj.create({
            'name': 'Table',
            'lst_price': 100,
        })
        aal_list = [aal.id, aal1.id]
        wizard = self.wizard_obj.create({
            'product_id': product.id,
            'line_ids': [(6, 0, aal_list)],
            'merge_timesheets': True,
        })
        wizard.create_lines()
        self.assertEqual(len(wizard.invoices), 1)
        invoice = wizard.invoices[0]
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        invoice_line = invoice.invoice_line_ids[0]
        self.assertEqual(invoice_line.quantity, 6)
        self.assertEqual(invoice_line.product_id.name, wizard.product_id.name)

    def test_no_customer_lines(self):
        aal = self.aal_obj.create({
            'name': 'Line',
            'account_id': self.account.id,
            'date': date(2017, 3, 17),
            'unit_amount': 2,
            'project_id': self.project_no_partner.id,
        })
        product = self.product_obj.create({
            'name': 'Table',
            'lst_price': 50,
        })
        wizard = self.wizard_obj.create({
            'product_id': product.id,
            'line_ids': [(6, 0, [aal.id])],
        })
        with self.assertRaises(UserError):
            wizard.create_lines()
