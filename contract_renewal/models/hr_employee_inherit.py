from odoo import models, fields, api
from datetime import date


class HrContract(models.Model):
    _inherit = 'hr.employee'

    need_another_approval = fields.Boolean(
        string="Need Another Approval" , default=1
    )

    second_manager = fields.Many2one("hr.employee", string="Second Manager")
