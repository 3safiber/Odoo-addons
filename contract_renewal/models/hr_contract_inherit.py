from odoo import models, fields, api
from datetime import date

class HrContract(models.Model):
    _inherit = 'hr.contract'

    generated_time = fields.Integer(
        string="New contract generated before"
    )

    manager_notes = fields.Text(string="Manager Nots")
    hr_notes = fields.Text(string="HR Notes")

    @api.model
    def update_contract_status(self):
        today = date.today()

        contracts = self.search([('state', '=', 'draft'), ('date_start', '=', today)])
        for contract in contracts:
            contract.write({'state': 'open'})
