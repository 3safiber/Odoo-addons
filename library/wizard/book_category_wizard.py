from odoo import fields, models


class BookCategoryWizard(models.TransientModel):
    _name = "book.category.wizard"
    category_id = fields.Many2one('library.category', string='Category')
    book_id = fields.Many2one('library.book', string='Book')

    def action_add_book(self):
        self.category_id.write({
            'book_ids': [(4, self.book_id.id)]
        })
