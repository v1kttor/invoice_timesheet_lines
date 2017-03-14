# -*- coding: utf-8 -*-

from odoo.tests import common


class TestInvoiceLine(common.TransactionCase):

    def test_invoice_line(self):
        anl = self.env['account.analytic.line']
        test_cases = []
        wizard = self.env['analytic.line.invoice.wizard']
        product = self.env['product.product']
        for i in test_cases:
            # account_invoice = self.env['account.invoice'].create({})
            # active_lines = self.env['account.analytic.line'].create({})
