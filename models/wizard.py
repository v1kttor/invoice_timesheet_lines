# -*- coding: utf-8 -*-

from odoo import models, fields


class Wizard(models.TransientModel):
    _name = 'analytic.line.invoice.wizard'

    product = fields.Many2one(
        'product.product', required=True, string="Product")
    # checkbox =
