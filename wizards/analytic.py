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
        #import pdb; pdb.set_trace()
        account_invoice = self.env['account.invoice']
        for rec in self:
            for line in rec.line_ids:

                line_vals = {
                    'name': line.name,
                    'product_id': rec.product_id,
                    'account_invoice.partner_id': line.project_id.partner_id,
                    'quantity': line.unit_amount,
                }
                invoice_vals = {
                    'invoice_line_ids': (0, _, line_vals),
                }
        account_invoice.create(invoice_vals)
