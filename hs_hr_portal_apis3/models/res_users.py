from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.constrains('groups_id')
    def _check_one_user_type(self):
        return