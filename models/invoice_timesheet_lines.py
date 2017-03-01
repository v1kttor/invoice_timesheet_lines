# -*- coding: utf-8 -*-

from odoo import models, fields


class InvoiceTimesheet(models.Model):
    _inherit = 'account.analytic.line'

    invoice_line_id = fields.Many2one('account.analytic.line')
    is_invoiced = fields.Boolean(string="Is Invoiced")
