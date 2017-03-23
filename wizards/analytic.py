# -*- coding: utf-8 -*-

import itertools

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
            'name': False,
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
        line_vals['name'] = name
        return line_vals

    def _prepare_invoice_line_vals(self, invoice, product, lines, merge=False):
        self.env['account.invoice.line']

        if merge:
            qty = sum(lines.mapped('unit_amount'))
            lines.write({'is_invoiced': True})
            return [(lines, self._prepare_single_line_vals(
                product.name_get()[0][1], qty, product, invoice)
            )]
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
            raise ValidationError(
                _('Please set Customer for %s go to Project --> Projects')
                % (partner.name)) #  % (line.project_id.name))
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
            partner_key = lambda x: x.project_id.partner_id
            grouped_lines = itertools.groupby(
                record.line_ids.sorted(partner_key), key=partner_key)
            for partner, group in grouped_lines:
                lines = self.env['account.analytic.line']
                for line in group:
                    lines += line
                # lines = map(lambda l: m+l, group)
                invoice_vals = self._prepare_invoice_vals(partner, lines)
                invoice = invoice_obj.create(invoice_vals)
                results = self._prepare_invoice_line_vals(
                        invoice,
                        record.product_id,
                        lines,
                        merge=record.merge_timesheets)
                for aal_lines, line_vals in results:
                    inv_line = line_obj.create(line_vals)
                    # for aal_line in aal_lines:
                    #     aal_line.invoice_line_id = inv_line
                    #    aal_line.is_invoiced = True
                    aal_lines.write({
                        'is_invoiced': True,
                        'invoice_line_id': inv_line.id,
                    })
                self.state = "finished"
                self.invoices += invoice
                self.invoices.compute_taxes()
            return {
                'name': _('Created new invoice'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree', # tree
                # 'res_model': 'analytic.line.invoice.wizard',
                'res_model': 'account.invoice',
                'res_ids': self.invoices.ids,
                # 'target': 'new',
                'target': 'current',
                'domain': [['id', 'in', self.invoices.ids]],
            }
