# -*- coding: utf-8 -*-
# from odoo import http


# class CategoryApi(http.Controller):
#     @http.route('/library', type='http', auth='none', csrf='false')
#     def index(self, **kw):
#         return "Hello, From odoo library project"

#     @http.route('/library/books', type='http', auth='public', csrf='false')
#     def list(self, **kw):
#         print('hello')
#         return http.request.render('library.listing', {
#             'root': '/library',
#             'objects': http.request.env['library.model_library_book'].search([]),
#         })

#     @http.route('/library/books/<model("library.books"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library.book', {
#             'object': obj
#         })
