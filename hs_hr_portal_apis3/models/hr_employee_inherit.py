from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    user_id = fields.Many2one(
        'res.users',
        string='Related User'
    )