from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    generated_time = fields.Integer(
       string="New contract generated before",
        related='company_id.generated_time', readonly=False
    )
    hr_approver = fields.Many2one(
        related='company_id.hr_approver',
        comodel_name= 'hr.employee',
        string='HR Approver',
         readonly= False
    )
