# -*- coding: utf-8 -*-

from datetime import date

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
        account_invoice = self.env['account.invoice']
        for rec in self:
            for line in rec.line_ids:
                if rec.merge_timesheets is True:
                    pass
                else:
                    line_vals = {
                        'name': line.name,
                        'account_id': line.account_id.id,
                        'product_id': rec.product_id.id,
                        'partner_id': line.project_id.partner_id.id,
                        'price_unit': rec.product_id.price,
                        'quantity': line.unit_amount,
                    }
                    invoice_vals = {
                        'partner_id': line.project_id.partner_id.id,
                        'date_invoice': date.today(),
                        'invoice_line_ids': [(0, 0, line_vals)],
                    }
                    line.is_invoiced = True
                    account_invoice.create(invoice_vals)

        """If "Merge timesheet entries" is checked, all the account.analytic.line
        should be summed into one and only one invoice line should be created.
        If during creation of the wizard the selected account.analytic.line
        lines contain different partners,
        the multiple invoices should be created. After invoices are created,
         a list of created invoices should be displayed."""
