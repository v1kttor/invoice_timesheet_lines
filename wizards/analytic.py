# -*- coding: utf-8 -*-
import itertools
from datetime import date

from odoo import models, fields, api


def by_line_partner(line):
    return line.project_id.partner_id.id


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
        account_invoice_obj = self.env['account.invoice']
        for record in self:
            grouped_lines = itertools.groupby(
                record.line_ids.sorted(by_line_partner), key=by_line_partner)
            for partner_id, lines in grouped_lines:

                for line in lines:

                    import pdb; pdb.set_trace()
                    if record.merge_timesheets is True:
                        pass
                    else:
                        invoice_line_vals = {
                            'name': line.name,
                            # 'account_id': line.account_id.id,
                            'product_id': record.product_id.id,
                            'price_unit': record.product_id.price,
                            'quantity': line.unit_amount,
                        }
                        line.is_invoiced = True
                        # invoice_line_list = [record.line_ids]
                        invoice_line_list = [invoice_line_vals]
                invoice_vals = {
                    'partner_id': line.project_id.partner_id.id,
                    'date_invoice': date.today(),
                    'type': 'out_invoice',
                    'invoice_line_ids': [(0, 0, invoice_line_list)],
                    # 'invoice_line_ids': [(0, 0, invoice_line_vals)],
                }
                account_invoice_obj.create(invoice_vals)

        """If "Merge timesheet entries" is checked, all the account.analytic.line
        should be summed into one and only one invoice line should be created.
        If during creation of the wizard the selected account.analytic.line
        lines contain different partners,
        the multiple invoices should be created. After invoices are created,
         a list of created invoices should be displayed."""
