# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Wizard(models.TransientModel):
    _name = 'analytic.line.invoice.wizard'

    product = fields.Many2one(
        'product.product', required=True, string="Product")
    merge_timesheet = fields.Boolean(
        default=False, string="Merge timesheet entries")

    @api.multi
    def create(self):
        account_lines = self.env['account.analytic.line']
        account_invoice = self.env['account.invoice']
        account_invoice_line = self.env['account.invoice.line']
        if account_lines.is_invoiced is False:
            #   invoice_vals = self.create({
                #   'account_id':
                #   'company_id':
                #   'currency_id':

                #   })
                pass
                # invoice = account_invoice.create(invoice_vals)
        # sukurti invoica
