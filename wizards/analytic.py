# -*- coding: utf-8 -*-

import itertools

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        'product.product', required=True, string='Product')
    merge_timesheets = fields.Boolean(
        default=False, string='Merge timesheet entries')
    line_ids = fields.Many2many(
        'account.analytic.line', default=_default_line_ids)

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

    def _prepare_invoice_vals(self, partner_id, lines):
        return {
            'partner_id': partner_id,
            'date_invoice': fields.Date.context_today(self),
            'type': 'out_invoice',
        }

    @api.multi
    def create_lines(self):
        self.ensure_one()
        invoice_obj = self.env['account.invoice']
        line_obj = self.env['account.invoice.line']
        all_invoices = self.env['account.invoice']
        if self.line_ids.filtered('is_invoiced'):
            raise ValidationError(
                _('One or more lines are already invoiced'))
        for partner_line in self.line_ids:
            if not partner_line.project_id.partner_id:
                raise ValidationError(
                    _('Please set Customer for %s ')
                    % self.line_ids.project_id.name)
        grouped_lines = itertools.groupby(
            self.line_ids.sorted(by_line_partner), key=by_line_partner)
        for partner_id, group in grouped_lines:
            lines = self.env['account.analytic.line']
            for line in group:
                lines += line
            invoice_vals = self._prepare_invoice_vals(partner_id, lines)
            invoice = invoice_obj.create(invoice_vals)
            results = self._prepare_invoice_line_vals(
                    invoice,
                    self.product_id,
                    lines,
                    merge=self.merge_timesheets)
            for aal_lines, line_vals in results:
                inv_line = line_obj.create(line_vals)
                aal_lines.write({
                    'is_invoiced': True,
                    'invoice_line_id': inv_line.id,
                })
            all_invoices += invoice
        all_invoices.compute_taxes()
        final_invoice_vals = {
            'name': _('Created new invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'target': 'current',
            'domain': [['id', 'in', all_invoices.ids]],
        }
        if len(all_invoices) != 1:
            return final_invoice_vals
        else:
            final_invoice_vals['view_mode'] = 'form'
            final_invoice_vals['res_id'] = all_invoices.id
            return final_invoice_vals
            # return {
            #     'name': _('Created new invoice'),
            #     'type': 'ir.actions.act_window',
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_id': all_invoices.id,
            #     'res_model': 'account.invoice',
            #     'target': 'current',
            #     'domain': [['id', 'in', all_invoices.ids]],
