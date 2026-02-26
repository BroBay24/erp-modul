# -*- coding: utf-8 -*-
# from odoo import http


# class ContactWai(http.Controller):
#     @http.route('/contact_wai/contact_wai', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_wai/contact_wai/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_wai.listing', {
#             'root': '/contact_wai/contact_wai',
#             'objects': http.request.env['contact_wai.contact_wai'].search([]),
#         })

#     @http.route('/contact_wai/contact_wai/objects/<model("contact_wai.contact_wai"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_wai.object', {
#             'object': obj
#         })

