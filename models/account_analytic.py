# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    invoice_line_id = fields.Many2one('account.invoice.line')
    is_invoiced = fields.Boolean(string='Is Invoiced')
