# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AnalyticLineInvoiceWizard(models.TransientModel):
    _name = 'analytic.line.invoice.wizard'

    def _default_line_ids(self):
        line_ids = self._context.get(
            'active_model') == 'account.analytic.line' and self._context.get(
                'active_ids') or []
        return [
            (6, 0, line_ids)
        ]

    product_id = fields.Many2one(
        'product.product', required=True, string="Product")
    merge_timesheets = fields.Boolean(
        default=False, string="Merge timesheet entries")
    line_ids = fields.Many2many(
        'account.analytic.line', default=_default_line_ids)

    @api.multi
    def create_lines(self):
        account_lines = self.env['account.analytic.line']
        account_invoice = self.env['account.invoice']
        account_invoice_lines = self.env['account.invoice.line']
        
