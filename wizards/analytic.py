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
        import pdb; pdb.set_trace()
        account_lines = self.env['account.analytic.line']
        account_invoice = self.env['account.invoice']
        account_invoice_lines = self.env['account.invoice.line']

        if is_invoiced is False:
            lines = self._context.get('active_ids')
            for active in lines:
                create_invoice = {
                    'account_lines.name':
                        account_invoice_lines.name,
                    'self.product_id':
                        account_invoice_lines.product_id,
                    'account_lines.project_id.partner_id':
                        account_invoice.partner_id,
                    'account_lines.unit_amount':
                        account_invoice_lines.quantity,
                }

            new_invoice = account_invoice.create(create_invoice)
            return new_invoice
        # return line's
