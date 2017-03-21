# -*- coding: utf-8 -*-

import itertools

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


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
    invoices = fields.Many2many(
        'account.invoice', string="Invoices")
    state = fields.Selection([
            ('initial', 'Initial'),
            ('finished', 'Finished'),
        ], string='Status', default='initial')

    def _prepare_single_line_vals(self, name, qty, product, invoice):
        ivl_obj = self.env['account.invoice.line']
        line_vals = {
            'product_id': product.id,
            'invoice_id': invoice.id,
            'quantity': qty,
            'name': name,
            'account_id': False,
            'price_unit': False,
            'uom_id': False,
            'price_subtotal': False,
            'invoice_line_tax_ids': False,
        }
        specs = ivl_obj._onchange_spec()
        updates = ivl_obj.onchange(line_vals, ['product_id'], specs)
        value = updates.get('value', {})
        value = ivl_obj._convert_to_write(value)
        line_vals.update(value)
        return line_vals

    def _prepare_invoice_line_vals(self, invoice, product, lines, merge=False):
        self.env['account.invoice.line']

        if merge:
            qty = 0.0
            for line in lines:
                qty += line.unit_amount
            line_name = line.name
            return [(lines, self._prepare_single_line_vals(
                line_name, qty, product, invoice))]
        else:
            result = []
            for line in lines:
                result.append(
                    (
                        line,
                        self._prepare_single_line_vals(
                            line.name, line.unit_amount, product, invoice))
                )
            return result

    def _prepare_invoice_vals(self, partner, lines):
        if not partner.id:
            raise UserError(
                _('Please set Customer for %s go to Project --> Projects')
                % (partner.name))
        else:
            return {
                'partner_id': partner.id,
                'date_invoice': fields.Date.context_today(self),
                'type': 'out_invoice',
            }

    @api.multi
    def create_lines(self):
        invoice_obj = self.env['account.invoice']
        line_obj = self.env['account.invoice.line']
        for record in self:
            if record.line_ids.filtered('is_invoiced'):
                raise ValidationError(
                    _('One or more lines are already invoiced'))
            grouped_lines = itertools.groupby(
                record.line_ids.sorted(
                    by_line_partner), key=by_line_partner)
            for partner, lines in grouped_lines:
                invoice_vals = self._prepare_invoice_vals(partner, lines)
                invoice = invoice_obj.create(invoice_vals)
                results = self._prepare_invoice_line_vals(
                        invoice,
                        record.product_id,
                        lines,
                        merge=record.merge_timesheets)
                for aal_lines, line_vals in results:
                    inv_line = line_obj.create(line_vals)
                    for aal_line in aal_lines:
                        aal_line.invoice_line_id = inv_line
                        aal_line.is_invoiced = True
                invoice.compute_taxes()
                self.state = "finished"
                self.invoices += invoice
            return {
                'name': _('Created new invoice'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'analytic.line.invoice.wizard',
                'res_id': self.id,
                'target': 'new',
            }
