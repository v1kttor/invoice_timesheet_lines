# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceTimeSheetLines(http.Controller):
#     @http.route('/invoice_time_sheet_lines/invoice_time_sheet_lines/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_time_sheet_lines/invoice_time_sheet_lines/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_time_sheet_lines.listing', {
#             'root': '/invoice_time_sheet_lines/invoice_time_sheet_lines',
#             'objects': http.request.env['invoice_time_sheet_lines.invoice_time_sheet_lines'].search([]),
#         })

#     @http.route('/invoice_time_sheet_lines/invoice_time_sheet_lines/objects/<model("invoice_time_sheet_lines.invoice_time_sheet_lines"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_time_sheet_lines.object', {
#             'object': obj
#         })