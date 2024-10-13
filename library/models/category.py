from odoo import models, fields


class LibraryCategory(models.Model):

    _name = "library.category"
    _description = "Category"
    name = fields.Char(string="Name")
    description = fields.Text(tracking=1)
    book_ids = fields.One2many('library.book', 'category_id', string='Books')
    _sql_constraints = [('unique_name', 'unique("name")', 'This name is exist!')]

    def open_action_book_category(self):
        action = self.env['ir.actions.actions']._for_xml_id('library.action_book_category')
        action['context'] = {'default_category_id': self.id}
        return action
