from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    # Existing fields
    trip_type = fields.Selection(
        [('short_term', 'Short-term Business Trip'),
         ('medium_term', 'Medium-term Business Trip'),
         ('long_term', 'Long-term Business Trip'),
         ('business_trip_foreigners_ksa', 'Business Trip for foreigners to KSA'),
         ('visit_clients', 'Visit Clients')
         ],
        string="Trip Type",
        compute="_compute_trip_type",
        store=True,
        readonly=False
    )

    distance = fields.Selection([
        ('below_70', 'Below 70km'),
        ('70_199', 'Between 70km and below 200km'),
        ('200_above', 'Above 200km')
    ], string="Distance")

    employee_grade = fields.Many2one(
        related='employee_id.grade_id',
        string="Employee Grade",
        readonly=True
    )

    daily_allowance = fields.Float(
        string="Daily Allowance", compute="_compute_daily_allowance")
    tickets_allowance = fields.Boolean(string="Tickets Allowance")
    tickets_allowance_value = fields.Float(
        string='Ticket Allowance Value', readonly=1)
    accommodation_paid_by_company = fields.Boolean(
        string="Accommodation Paid by Company")
    international_trip = fields.Boolean(string="outside ksa")
    car_provided = fields.Boolean(string="Car Provided by Company")
    total_days = fields.Integer(
        string="Total Days", compute="_compute_total_days", store=True)

    additional_allowance = fields.Float(string="Additional Allowance for Medium/Long-term",
                                        compute="_compute_additional_allowance")
    relocation_allowance = fields.Float(
        string="Relocation Allowance", compute="_compute_relocation_allowance")
    total_compensation = fields.Float(
        string="Total Compensation", compute="_compute_total_compensation")
    location_trip = fields.Char(string="Location of the trip")
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        help="Employee associated with this record",
        default=lambda self: self.env.user.employee_id
    )
    request_manager_id = fields.Many2one('hr.employee', string="Request Owner",
                                         help="The manager of the selected employee")

    approval_type = fields.Selection(
        related='category_id.approval_type',
        string='Approval Type',
        readonly=True,
    )
    number_of_trips = fields.Integer(string='Number of Trips')
    approval_cycle_type = fields.Selection(
        [('project', 'Project'),
         ('administrator', 'Administrator')],
        string='Approval Type',

    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        help="Project Task associated with this request"
    )

    @api.onchange('approval_cycle_type')
    def _onchange_approval_cycle_type(self):
        """
        This method is triggered when 'approval_cycle_type' is changed.
        Clears the project_id if the type is not 'project'.
        """
        if self.approval_cycle_type != 'project':
            self.project_id = False

    @api.depends("project_id", "approval_cycle_type")
    def _compute_approver_ids(self):
        for rec in self:
            if rec.approval_type == 'business_trip':
                if rec.project_id and rec.approval_cycle_type == 'project':
                    users_to_approver = {}
                    for approver in rec.approver_ids:
                        users_to_approver[approver.user_id.id] = approver

                    user_ids = set()
                    approver_id_vals = []

                    if rec.employee_id:
                        user_ids.add(rec.employee_id.coach_id.user_id.id)
                    if rec.project_id:
                        user_ids.add(rec.project_id.user_id.id)
                    if rec.employee_id:
                        user_ids.add(rec.employee_id.parent_id.user_id.id)

                    if user_ids:
                        for user in user_ids:
                            rec._create_or_update_approver(user, users_to_approver, approver_id_vals, True,
                                                           list(user_ids).index(user))

                    # Get the hr_employee from the approval.category model dynamically
                    employee_to_add = rec.category_id.hr_employee
                    if employee_to_add and employee_to_add.user_id:
                        rec._create_or_update_approver(employee_to_add.user_id.id, users_to_approver, approver_id_vals,
                                                       True, len(approver_id_vals))

                    rec.update({'approver_ids': approver_id_vals})

                elif rec.approval_cycle_type == 'administrator':
                    self.approver_ids = [(5, 0, 0)]
                    users_to_approver = {}
                    for approver in rec.approver_ids:
                        users_to_approver[approver.user_id.id] = approver

                    user_ids = set()
                    approver_id_vals = []

                    if rec.employee_id:
                        user_ids.add(rec.employee_id.coach_id.user_id.id)
                    if rec.employee_id:
                        user_ids.add(rec.employee_id.parent_id.user_id.id)

                    if user_ids:
                        for user in user_ids:
                            rec._create_or_update_approver(user, users_to_approver, approver_id_vals, True,
                                                           list(user_ids).index(user))

                    # Get the hr_employee from the approval.category model dynamically
                    employee_to_add = rec.category_id.hr_employee
                    if employee_to_add and employee_to_add.user_id:
                        rec._create_or_update_approver(employee_to_add.user_id.id, users_to_approver, approver_id_vals,
                                                       True, len(approver_id_vals))

                    rec.update({'approver_ids': approver_id_vals})
                else:
                    rec.update({'approver_ids': [(5, 0, 0)]})
            else:
                super(ApprovalRequest, rec)._compute_approver_ids()

    # def action_confirm(self):
    #     res = super(ApprovalRequest, self).action_confirm()
    #     if self.approval_type == 'business_trip':
    #         if self.employee_id and self.location_trip:
    #             self.employee_id.work_location_id.name = self.location_trip.name
    #     return res

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for request in self:
            if request.employee_id and request.employee_id.parent_id:
                request.request_manager_id = request.employee_id.parent_id
            else:
                request.request_owner_id = False

    @api.depends('date_start', 'date_end')
    def _compute_total_days(self):
        for record in self:
            if record.date_start and record.date_end:
                start_date = fields.Date.from_string(record.date_start)
                end_date = fields.Date.from_string(record.date_end)
                record.total_days = (end_date - start_date).days + 1
            else:
                record.total_days = 0

    @api.depends('date_start', 'date_end')
    def _compute_trip_type(self):
        for request in self:
            if request.date_start and request.date_end:
                try:
                    date_start = fields.Date.from_string(request.date_start)
                    date_end = fields.Date.from_string(request.date_end)
                    duration = (date_end - date_start).days

                    if duration <= 14:
                        request.trip_type = 'short_term'
                    elif 15 <= duration < 90:
                        request.trip_type = 'medium_term'
                    else:
                        request.trip_type = 'long_term'
                except ValueError:
                    request.trip_type = False
            else:
                request.trip_type = False

    @api.depends('trip_type', 'distance', 'employee_grade', 'accommodation_paid_by_company', 'international_trip',
                 'car_provided', 'total_days', 'location_trip', 'tickets_allowance')
    def _compute_daily_allowance(self):
        for request in self:
            daily_allowance = 0
            tickets_allowance_value = 0
            if request.trip_type == 'business_trip_foreigners_ksa':
                daily_allowance = 250
                tickets_allowance_value = 0
            elif request.distance == "below_70":
                daily_allowance = 0
            elif request.distance == '70_199':
                daily_allowance = 150
            elif request.trip_type == 'long_term':
                daily_allowance = 0
            else:
                if request.international_trip:
                    if request.accommodation_paid_by_company:
                        if request.employee_grade.name == 'HoD':
                            daily_allowance = 600
                            if request.tickets_allowance:
                                tickets_allowance_value = 500
                        elif request.employee_grade.name == 'Professional':
                            daily_allowance = 350
                            if request.tickets_allowance:
                                tickets_allowance_value = 400
                        elif request.employee_grade.name == 'Staff':
                            daily_allowance = 300
                            if request.tickets_allowance:
                                tickets_allowance_value = 360
                    else:  # Hotel paid by the employee
                        if request.employee_grade.name == 'HoD':
                            daily_allowance = 800
                            if request.tickets_allowance:
                                tickets_allowance_value = 500
                        elif request.employee_grade.name == 'Professional':
                            daily_allowance = 600
                            if request.tickets_allowance:
                                tickets_allowance_value = 400
                        elif request.employee_grade.name == 'Staff':
                            daily_allowance = 550
                            if request.tickets_allowance:
                                tickets_allowance_value = 360

                else:  # Domestic Trip (Within KSA)
                    if request.accommodation_paid_by_company:
                        if request.employee_grade.name == 'HoD':
                            daily_allowance = 450
                            if request.tickets_allowance:
                                tickets_allowance_value = 500
                        elif request.employee_grade.name == 'Professional':
                            daily_allowance = 300
                            if request.tickets_allowance:
                                tickets_allowance_value = 400
                        elif request.employee_grade.name == 'Staff':
                            daily_allowance = 220
                            if request.tickets_allowance:
                                tickets_allowance_value = 360
                    else:  # Hotel paid by the employee
                        if request.employee_grade.name == 'HoD':
                            daily_allowance = 600
                            if request.tickets_allowance:
                                tickets_allowance_value = 500
                        elif request.employee_grade.name == 'Professional':
                            daily_allowance = 450
                            if request.tickets_allowance:
                                tickets_allowance_value = 400
                        elif request.employee_grade.name == 'Staff':
                            daily_allowance = 370
                            if request.tickets_allowance:
                                tickets_allowance_value = 360

            # Adjust daily allowance if a car is provided by the company
            if request.car_provided:
                request.tickets_allowance = False
                if request.employee_grade.name == 'HoD':
                    daily_allowance -= 150
                elif request.employee_grade.name == 'Professional':
                    daily_allowance -= 150
                elif request.employee_grade.name == 'Staff':
                    daily_allowance -= 120

            daily_allowance = max(daily_allowance, 0)

            request.daily_allowance = daily_allowance
            request.tickets_allowance_value = tickets_allowance_value

    @api.depends('total_days')
    def _compute_additional_allowance(self):
        for request in self:
            if 14 < request.total_days < 90:
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', request.employee_id.id)], limit=1)
                wage = contract.wage if contract else 0.0
                request.additional_allowance = (
                    wage * 0.25) * (request.total_days / 30)
            else:
                request.additional_allowance = 0.0

    @api.depends('trip_type')
    def _compute_relocation_allowance(self):
        for request in self:
            relocation_allowance = 0.0
            if request.trip_type == 'long_term':
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', request.employee_id.id)], limit=1)
                wage = contract.wage if contract else 0.0
                relocation_allowance = wage
            request.relocation_allowance = relocation_allowance

    @api.depends('daily_allowance', 'total_days', 'additional_allowance', 'relocation_allowance',
                 'tickets_allowance_value', 'trip_type')
    def _compute_total_compensation(self):
        for request in self:
            if request.trip_type == 'visit_clients':
                request.total_compensation = 25 * self.number_of_trips
            elif request.trip_type == 'long_term':
                request.total_compensation = self.relocation_allowance
            elif request.trip_type == 'medium_trip':
                request.total_compensation = request.additional_allowance
            elif request.trip_type == 'short_term' and request.distance == 'below_70':
                request.total_compensation = 0

            else:
                request.total_compensation = (
                    request.daily_allowance * request.total_days) + request.additional_allowance + request.relocation_allowance + request.tickets_allowance_value


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[
        ('business_trip', 'Business Trip'),
    ])
    hr_employee = fields.Many2one('hr.employee',
                                  string='HR Employee')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    temporary_location = fields.Char(string="Temporary Location")
    grade_id = fields.Many2one('x_grade', string='Grade')
    employee_grade = fields.Selection([
        ('hod', 'Head of Department (HoD)'),
        ('professional', 'Professional'),
        ('staff', 'Staff')
    ], string="Employee Grade")


class Grade(models.Model):
    _name = 'x_grade'
    _description = 'Grade'

    name = fields.Char(string='Grade Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
