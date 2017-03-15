# -*- coding: utf-8 -*-

from datetime import date

from odoo.tests import common


class TestMergeInvoice(common.TransactionCase):

    def test_merge_invoice(self):
        test_cases = []
        for product, qty, unit_price, taxes in test_cases:
            product = self.env['product.product'].create({
                'name': 'Vaza',
                'type': ['service'],
            })
            wizard = self.env['analytic.line.invoice.wizard'].create({
                'product_id': product,
            })
            # active_lines = self.env['account.analytic.line'].create({
            #     'name': 'Line',
            #     'ammount': '3',
            #     'date': date(2017, 2, 15),
            # })
            # account_invoice = self.env['account.invoice'].create({})
            self.assertEqual()
