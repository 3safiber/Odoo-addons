# -*- coding: utf-8 -*-
import json
import math
from urllib.parse import parse_qs
from odoo import http
from odoo.http import request, Response
from datetime import date
import logging
import secrets
_logger = logging.getLogger(__name__)


def valid_response(message, data, status, pagination_info=None):
    response_body = {
        'message': message,
        'data': data
    }
    if pagination_info:
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(response_body, status=status)


def invalid_response(errorMessage, status, pagination_info=None):
    response_body = {
        'error': errorMessage
    }
    if pagination_info:
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(response_body, status=status)


class BookApi(http.Controller):
    def authenticate_token(self):
        IrHttp = request.env['ir.http'].sudo()
        IrHttp._auth_method_outlook()

    # root route
    @http.route('/library', method=["GET"], website=True, type='http',
                auth='user', csrf=False)
    def index(self):
        if not request.env.user.has_group('library.library_librarian_group'):
            return request.redirect('/web?error=Access Denied')
        try:
            books = request.env['library.book'].sudo().search([])

            return request.render('library.books_view_template', {
                'books': books
            })
        except Exception as e:

            # Log the error to Odoo logs
            _logger.error(
                "Error in LibraryController index method: %s", str(e))
            # Render a 404 page or another error page
            return request.render('website.404')

    # create route
    @http.route(
        '/library/book',
        method=["POST"],
        type='http',
        auth='user',
        csrf=False)
    def create_book(self):

        self.authenticate_token()

        data = request.httprequest.data.decode()
        vals = json.loads(data)

        if not vals.get('name') or not vals.get('author'):
            return invalid_response(
                'The fields (name, author) are required!', 400)

        vals['publication_date'] = date.today()

        try:

            res = request.env['library.book'].sudo().create(vals)

            print(f"ref = {res.ref}")

            if res:
                return valid_response(
                    message='Book has been created successfully!',
                    data={'id': res.id,
                          'ref': res.ref,
                          'name': res.name,
                          'author': res.author,
                          'Selling price': res.selling_price,
                          },
                    status=201,
                )
        except Exception as e:
            return invalid_response(f"There was an error: {str(e)}!", 400)

    # update route
    @http.route('/library/book/<int:book_id>', method=["PUT"], type='http',
                auth='none', csrf=False)
    def update_book(self, book_id):
        try:
            book_id = request.env['library.book'].sudo().search(
                [('id', '=', book_id)])
            if not book_id:
                return invalid_response("Book not found!", 404)
            data = request.httprequest.data.decode()
            vals = json.loads(data)
            book_id.write(vals)
            return valid_response(
                'Book has been updated successfully!',
                {'id': book_id.id,
                 'book_name': book_id.name,
                 "data_updated": vals},
                200)
        except Exception as e:
            return invalid_response(f"There was an error: {str(e)}!", 400)

    # read route get book by id
    @http.route('/library/book/<int:book_id>', method=["GET"], type='http',
                auth='none', csrf=False)
    def read_book(self, book_id):
        try:

            book = request.env['library.book'].sudo().search(
                [('id', '=', book_id)])

            if not book:
                return invalid_response(
                    f"Book with id: ({book_id}), not found!", 404)
            return valid_response(
                'Book was found!',
                {'id': book.id,
                 'ref': book.ref,
                 'name': book.name,
                 'author': book.author,
                 'Selling price': book.selling_price,
                 },
                200)
        except Exception as e:
            return invalid_response(f"There was an error: {str(e)}!", 400)

    # delete route delete book by id
    @http.route(
        '/library/book/<int:book_id>',
        method=["DELETE"],
        type='http',
        auth='none',
        csrf=False)
    def delete_book(self, book_id):
        print("delete method")
        try:
            book = request.env['library.book'].sudo().search(
                [('id', '=', book_id)])
            if not book:
                return invalid_response(
                    f"Book with id: ({book_id}), not found in the library!",
                    404)
            deleted_book = {'id': book.id,
                            'ref': book.ref,
                            'name': book.name,
                            'author': book.author,
                            'Selling price': book.selling_price,
                            }
            book.unlink()
            return valid_response('Book deleted successfully!', deleted_book, 200)
        except Exception as e:
            return invalid_response(f"There was an error: {str(e)}!", 400)

    # Fetch all books
    @http.route('/library/books', method=["GET"], type='http', auth='none', csrf=False)
    def fetch_all_books(self):
        try:
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            page = 1
            limit = 0
            if params:
                if (params.get('limit')):
                    limit = int(params.get('limit')[0])
                if (params.get('page')):
                    page = int(params.get('page')[0])
            offset = (page - 1) * limit
            books_count = request.env['library.book'].sudo().search_count([])
            pages = math.ceil(books_count / limit) if limit else 1
            pagination_info = {
                'page': page if page else 1,
                'limit': limit if limit else 'infinity',
                'pages': pages,
                'count': books_count
            }
            if page > pages:
                return invalid_response(f"There are no page {page}. The maximum page number is {pages} for a limit of {limit}.", 400, pagination_info)

            books = request.env['library.book'].sudo().search(
                [], offset=offset, limit=limit, order='id desc')
            if not books:
                return invalid_response("There are no books in the library!", 404)
            return valid_response(
                f"These are the books on page {page} with a limit of {limit}.",
                [{'id': book.id,
                  'ref': book.ref,
                  'name': book.name,
                  'author': book.author,
                  'Selling price': book.selling_price,
                  }for book in books],
                200,
                pagination_info)
        except Exception as e:
            return invalid_response(f"There was an error: {str(e)}!", 400)

    @http.route("/test", methods=["GET"], type='http', auth="none", csrf=False)
    def test(self):
        print('TEST TEST TEST')
        # Parse the request body as JSON
        return 'True'
