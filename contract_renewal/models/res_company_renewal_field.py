from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    generated_time = fields.Integer(
        string="New contract generated before"
    )
    hr_approver = fields.Many2one('hr.employee',
        string='HR Approver'
    )