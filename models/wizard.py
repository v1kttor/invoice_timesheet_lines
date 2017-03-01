# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Wizard(models.TransientModel):
    _name = 'analytic.line.invoice.wizard'

    product = fields.Many2one(
        'product.product', required=True, string="Product")
    checkbox = fields.Boolean(default=False, string="Merge timesheet entries")

    @api.multi
    def create(self):
        pass
        # sukurti invoica
