# -*- coding: utf-8 -*-
import itertools
from datetime import date

from odoo import models, fields, api


def by_line_partner(line):
    return line.project_id.partner_id


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

    def _prepare_invoice_line_vals(self, invoice, product, line):
        ivl_obj = self.env['account.invoice.line']
        line_vals = {
            'product_id': product.id,
            'invoice_id': invoice.id,
            'quantity': line.unit_amount,
        }
        tmp_line = ivl_obj.new(line_vals)
        tmp_line._onchange_product_id()
        tmpvals = [(f, tmp_line[f]) for f in tmp_line._fields]
        line_vals.update({
            # Jei merginam eilutes, tai 'name' tures ateiti is tmp_line.name
            'name': line.name,
            'account_id': tmp_line.account_id.id,
            'price_unit': tmp_line.price_unit,
            'uom_id': tmp_line.uom_id.id,
            'invoice_line_tax_ids': [
                (6, 0, tmp_line.invoice_line_tax_ids.ids)
            ],
        })
        return line_vals

    def _prepare_invoice_vals(self, partner, lines):
        vals = {
            'partner_id': partner.id,
            'date_invoice': date.today(),
            'type': 'out_invoice',
        }
        return vals

    @api.multi
    def create_lines(self):
        # Reikia patikrinti ar projektai turi priskirta partner_id (Customer)
        # ant sukurto invoice pakviesti compute_taxes ir paziureti ar taxai yr
        invoice_obj = self.env['account.invoice']
        line_obj = self.env['account.invoice.line']
        for record in self:
            grouped_lines = itertools.groupby(
                record.line_ids.sorted(by_line_partner), key=by_line_partner)
            for partner, lines in grouped_lines:
                invoice_vals = self._prepare_invoice_vals(partner, lines)
                invoice = invoice_obj.create(invoice_vals)

                for line in lines:
                    inv_line = line_obj.create(self._prepare_invoice_line_vals(
                        invoice, record.product_id, line
                    ))
                    # reikia susieti line (account.analytic.line) su sukurta
                    # invoice line (inv_line) ir is_invoiced uzsettinti i True

    """If "Merge timesheet entries" is checked, all the account.analytic.line
    should be summed into one and only one invoice line should be created.
    If during creation of the wizard the selected account.analytic.line
    lines contain different partners,
    the multiple invoices should be created. After invoices are created,
     a list of created invoices should be displayed."""
