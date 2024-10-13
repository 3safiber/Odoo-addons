from odoo import models, fields


class LibrarySettings(models.TransientModel):
    _inherit = 'res.config.settings'
    note = fields.Char()
