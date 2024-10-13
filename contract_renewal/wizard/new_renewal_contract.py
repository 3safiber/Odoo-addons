from odoo import models, fields, api,_
from odoo.exceptions import UserError


class HrContractCreateWizard(models.TransientModel):
    _name = 'hr.contract.create.wizard'
    _description = 'Create New Contract Wizard'

    name = fields.Char(string='Contract Reference')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    wage = fields.Integer(string='Wage')

    def create_contract(self):
        # Create the contract
        contract_vals = {
            'employee_id': self.employee_id.id,
            'date_start': self.start_date,
            'date_end': self.end_date,
            'name': self.name,
            'wage': self.wage
        }
        new_contract = self.env['hr.contract'].create(contract_vals)

        # Get the manager of the employee
        manager = self.employee_id.parent_id.user_id

        # Prepare the message body for the manager
        message_body = f"A new contract has been created for {self.employee_id.name}."

        # Check if manager exists
        if manager and manager.partner_id:
            # Post the message to the manager
            new_contract.message_post(
                body=message_body,
                subject="New Contract Created",
                message_type="comment",
                subtype_id=self.env.ref("mail.mt_comment").id,
                partner_ids=[manager.partner_id.id]  # Send notification to the manager
            )

            # Display danger notification to the manager
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',  # Type of notification for error
                    'title': _('New Contract Alert'),  # Title of the notification
                    'message': _('A new contract has been created for %s.' % self.employee_id.name),
                    'sticky': False,  # Not sticky, will disappear automatically
                }
            }

        return {'type': 'ir.actions.act_window_close'}