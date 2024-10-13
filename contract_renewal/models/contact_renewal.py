from odoo import models, fields, api
from datetime import date, timedelta
from odoo.exceptions import AccessError


class ContractRenewal(models.Model):
    _name = 'contract.renewal'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = 'Contract Renewal'

    name = fields.Many2one(
        'hr.employee', string='Employee Name', required=True)

    contract_start_date = fields.Date(
        string='Contract Start Date', required=True)
    contract_end_date = fields.Date(string='Contract End Date', required=True)
    new_end_date = fields.Date(string='New End Date')
    department = fields.Many2one(
        related='name.department_id', string='department')
    job_position = fields.Many2one(
        related='name.job_id', string="Job position")
    contract_type = fields.Many2one(
        related='name.contract_id.contract_type_id', string="Contract Type")
    req_date = fields.Date(
        string='Req Date', default=fields.Date.today, readonly=True)

    related_hr = fields.Many2one('hr.employee', string='Related HR',
                                 default=lambda self: self._get_default_hr_approver())
    manager_approved = fields.Boolean(string="Manager Approved", default=False)
    hr_approved = fields.Boolean(string="HR Approved", default=False)

    status = fields.Selection([
        ('manager_approval', 'Manager Approval'),
        ('approved_by_manager', 'Approved by Manager'),
        ('approved_by_hr', 'Approved by HR'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ], string='Status', default='manager_approval')

    def _get_default_hr_approver(self):
        return self.env.user.company_id.hr_approver.id if self.env.user.company_id.hr_approver else False

    def action_confirm(self):
        """Approve by Manager first, then HR."""
        manager_user = self.name.parent_id.user_id
        related_hr_user = self.related_hr.user_id

        if self.env.user == manager_user and not self.manager_approved:
            self.manager_approved = True
            self.status = 'approved_by_manager'
            self.activity_schedule(
                activity_type_id=self.env.ref(
                    'mail.mail_activity_data_todo').id,
                summary="Approval Required: New Contract",
                user_id=self.related_hr.user_id.id,
                note="A new contract has been added and requires your approval.",
            )

        elif self.env.user == related_hr_user and self.manager_approved and not self.hr_approved:
            self.hr_approved = True
            self.status = 'approved_by_hr'

        if self.manager_approved and self.hr_approved:
            self.status = 'confirmed'

            return {
                'type': 'ir.actions.act_window',
                'name': 'Create New Contract',
                'res_model': 'hr.contract.create.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {
                    'default_employee_id': self.name.id,
                    'default_start_date': self.contract_start_date,
                    'default_end_date': self.new_end_date,
                },
            }

    def action_reject(self):
        """Reject by Manager or HR."""
        manager_user = self.name.parent_id.user_id
        related_hr_user = self.related_hr.user_id

        # Check if the current user is either the manager or the HR
        if self.env.user not in [manager_user, related_hr_user]:
            raise AccessError(
                "Only the employee's manager or the related HR can reject this request.")

        self.status = 'rejected'
        self.manager_approved = False
        self.hr_approved = False

    def _check_contract_expiry(self):
        """Check for contracts that are expiring within the specified duration."""
        today = date.today()

        # Fetch contracts from 'hr.contract'
        contracts = self.env['hr.contract'].search([
            ('date_end', '>=', today),
            # Set a reasonable upper limit for search
            ('date_end', '<=', today + timedelta(days=365))
        ])

        for contract in contracts:
            # Use generated_time from the contract
            duration_days = contract.generated_time or 30  # Default to 30 if not set

            # Check if the contract is expiring within the specified duration
            if contract.date_end <= today + timedelta(days=duration_days):
                existing_renewal = self.search(
                    [('name', '=', contract.employee_id.id)], limit=1)

                if not existing_renewal:
                    renewal = self.create({
                        'name': contract.employee_id.id,
                        'contract_start_date': contract.date_start,
                        'contract_end_date': contract.date_end,
                        'new_end_date': contract.date_end + timedelta(days=365),
                        'status': 'manager_approval',
                    })

                    renewal.activity_schedule(
                        activity_type_id=self.env.ref(
                            'mail.mail_activity_data_todo'
                        ).id,
                        summary="Approval Required: New Contract",
                        user_id=contract.employee_id.parent_id.user_id.id,
                        note="A new contract renewal has been created for employee " +
                        {contract.employee_id.name} +
                        "and requires your approval.",
                    )
