from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    book_id = fields.Many2one(
        'library.book',
        string='book',
    )

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        print("inside action_confirm")
        return res
