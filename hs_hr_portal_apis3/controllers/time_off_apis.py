
from odoo import http
from odoo.http import request, Response
from datetime import date
import json
import logging
from odoo.exceptions import UserError
from odoo import http
from odoo.addons.hs_hr_portal_apis3.controllers.all_apis import validate_token

_logger = logging.getLogger(__name__)


class TimeOffController(http.Controller):

    @validate_token
    @http.route('/v1/api/create_time_off_lookup', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def create_time_off_lookup(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            employee_id = user_obj.employee_id
            if not employee_id:
                raise UserError('This user has no employee ')
            if (
                allocation_ids := request.env['hr.leave.allocation']
                .with_user(user_obj)
                .search(
                    [
                        ('employee_id', '=', employee_id.id),
                        ('state', '=', 'validate'),
                    ]
                )
            ):
                holiday_status_ids = allocation_ids.mapped('holiday_status_id')
                holiday_status_list = [{
                    'name': holiday.name,
                    'request_unit': holiday.request_unit,
                    'id': holiday.id,
                    'support_document': holiday.support_document,
                } for holiday in holiday_status_ids]
                res = {
                    'time_off_type': holiday_status_list,
                    'custom_hours': [
                        ('0', '12:00 AM'), ('0.5', '12:30 AM'),
                        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
                        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
                        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
                        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
                        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
                        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
                        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
                        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
                        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
                        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
                        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
                        ('12', '12:00 PM'), ('12.5', '12:30 PM'),
                        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
                        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
                        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
                        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
                        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
                        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
                        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
                        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
                        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
                        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
                        ('23', '11:00 PM'), ('23.5', '11:30 PM')
                    ]
                }
            else:
                res = {'msg': 'There is no allocation for this employee'}

            return Response(
                json.dumps(res, sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=200
            )
        except Exception as e:
            return Response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=500
            )

    @validate_token
    @http.route('/v1/api/get_all_time_off_can_approve', auth="none", type='http', methods=['GET'], csrf=False, cors='*')
    def get_all_time_off_can_approve(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env
            time_off_obj = env['hr.leave']
            if time_off_ids := time_off_obj.with_user(user_obj).search(
                [('can_approve', '=', True), ('state', '!=', 'validate')]
            ):
                time_off_list = [
                    {
                        'id': off.id,
                        'employee_name': off.employee_id.name,
                        'time_off_type': off.holiday_status_id.name,
                        'description': off.name,
                        'start_date': off.date_from.strftime('%Y-%m-%d'),
                        'end_date': off.date_to.strftime('%Y-%m-%d'),
                        'duration': off.duration_display,
                        'state': off.state,
                    }
                    for off in time_off_ids
                ]
                res = {
                    'msg': 'Found',
                    'time_off_list': time_off_list
                }
            else:
                res = {
                    'msg': 'There is no timeoff to approve for this employee'
                }
            return Response(
                json.dumps(res, sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=200
            )
        except Exception as e:
            return Response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=500
            )

    @validate_token
    @http.route('/v1/api/get_all_time_off_request', auth="none", type='http', methods=['GET'], csrf=False, cors='*')
    def get_all_time_off_request(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            employee_id = user_obj.employee_id
            if not employee_id:
                raise UserError('This user has no employee ')
            env = request.env
            time_off_obj = env['hr.leave']
            if time_off_ids := time_off_obj.with_user(user_obj).search(
                [('employee_id', '=', employee_id.id)]
            ):
                time_off_list = [
                    {
                        'id': off.id,
                        'employee_name': off.employee_id.name,
                        'time_off_type': off.holiday_status_id.name,
                        'description': off.name,
                        'start_date': off.date_from.strftime('%Y-%m-%d'),
                        'end_date': off.date_to.strftime('%Y-%m-%d'),
                        'duration': off.duration_display,
                        'state': off.state,
                    }
                    for off in time_off_ids
                ]
                res = {
                    'msg': 'Found',
                    'time_off_list': time_off_list
                }
            else:
                res = {
                    'msg': 'There is no timeoff to approve for this employee'
                }
            return Response(
                json.dumps(res, sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=200
            )
        except Exception as e:
            return Response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=500
            )

    @validate_token
    @http.route('/v1/api/approve_time_off_request', auth="none", type='http', methods=['POST'], csrf=False, cors='*')
    def approve_time_off_request(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env
            time_off_obj = env['hr.leave']
            time_off_request_id = json.loads(request.httprequest.data)[
                'time_off_request_id']
            if time_off_id := time_off_obj.with_user(user_obj).browse(
                int(time_off_request_id)
            ):
                if time_off_id.state == 'confirm':
                    time_off_id.action_approve()
                    res = {"msg": "The request approved"}
                elif time_off_id.state == 'validate1':
                    time_off_id.action_validate()
                    res = {"msg": "The request validated"}
                else:
                    res = {
                        'msg': 'This request is already approved or not submitted or refused'}
            else:
                res = {"msg": "There is no time of request"}

            return Response(json.dumps(res, sort_keys=True, indent=4),
                            content_type='application/json;charset=utf-8', status=200
                            )
        except Exception as e:
            return Response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=500
            )

    @validate_token
    @http.route('/v1/api/refuse_time_off_request', auth="none", type='http', methods=['POST'], csrf=False, cors='*')
    def refuse_time_off_request(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env
            time_off_obj = env['hr.leave']
            time_off_request_id = json.loads(request.httprequest.data)[
                'time_off_request_id']
            if time_off_id := time_off_obj.with_user(user_obj).browse(
                int(time_off_request_id)
            ):
                if time_off_id.state in ['confirm', 'validate1', 'validate']:
                    time_off_id.action_refuse()
                    res = {"msg": "The request refused"}
                else:
                    res = {
                        "msg": "The request can not refused, the request not confirmed or refused before"}
            return Response(
                json.dumps(res, sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=200
            )
        except Exception as e:
            return Response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=500
            )

    @validate_token
    @http.route('/v1/api/create_time_off_request', auth="none", type='http', methods=['POST'], csrf=False, cors='*')
    def create_time_off_request(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            employee_id = user_obj.employee_id
            if not employee_id:
                raise UserError('This user has no employee')
            data = json.loads(request.httprequest.data)
            env = request.env
            time_off_obj = env['hr.leave']
            time_off_vals = {
                'holiday_type': 'employee',
                'employee_id': employee_id.id,
                'holiday_status_id': data['holiday_status_id'],
                'name': data.get('description')
            }
            holiday_status_id = env['hr.leave.type'].browse(
                int(data['holiday_status_id']))
            if holiday_status_id.request_unit == 'day':
                date_from = date['date_from'].strftime('%Y-%m-%d')
                date_to = date['date_to'].strftime('%Y-%m-%d')
                time_off_vals.update({
                    'request_date_from': date_from,
                    'request_date_to': date_to,
                })
            elif holiday_status_id.request_unit == 'hour':
                time_off_vals.update({
                    'request_unit_hours': True,
                    'request_hour_from': data['request_hour_from'],
                    'request_hour_to': data['request_hour_to'],
                })
            if holiday_status_id.support_document:
                attachment_id = env['ir.attachment'].create({
                    'data': data['attachment_base64'],
                    'type': 'binary'
                })
                time_off_vals['attachment_ids'] = [(0, 0, attachment_id)]
            time_off_id = time_off_obj.with_user(
                user_obj).create(time_off_vals)
            if time_off_id:
                res = {"msg": "The request created successfully"}
            return Response(
                json.dumps(res, sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=200
            )
        except Exception as e:
            return Response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=500
            )

    @validate_token
    @http.route('/v1/api/time_off', auth="none", type='http', methods=['POST'], csrf=False, cors='*')
    def api_create_time_off(self, **kwargs):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            employee_id = user_obj.employee_id
            data = json.loads(request.httprequest.data)
            name = data.get('description')
            holiday_status_id = data.get('holiday_status_id')
            request_unit = data.get('request_unit')  # 'day' , 'hour'
            request_date_from = data.get(
                'request_date_from').strftime('%m/%d/%Y')
            errors = []
            time_off_data = {}
            if name:
                time_off_data['name'] = name
            # validate data
            if not holiday_status_id:
                errors.append('The field holiday_status_id is required!')
            if not request_date_from:
                errors.append('The field request_date_from is required!')
            if not employee_id:
                errors.append('No employee is associated with this user.')
            if employee_id.company_id != request.env.user.company_id:
                errors.append(
                    'Please make sure you are logged in the correct company.')
            match request_unit:
                case 'day':
                    if request_date_to := data.get('request_date_to').strftime(
                        '%m/%d/%Y'
                    ):
                        time_off_data['request_date_to'] = request_date_to
                    else:
                        errors.append('The field request_date_to is required')
                case 'hour':
                    request_hour_from = data.get('request_hour_from').strftime(
                        '%m/%d/%Y'
                    )
                    request_hour_to = data.get('request_hour_to').strftime(
                        '%m/%d/%Y'
                    )
                    if not request_hour_from or not request_hour_to:
                        errors.append(
                            'The fields request_hour_from and request_hour_to is required'
                        )
                    else:
                        time_off_data.update(
                            {
                                'request_unit_hours': True,
                                'request_hour_from': request_hour_from,
                                'request_hour_to': request_hour_to,
                            }
                        )
                case _:
                    errors.append(
                        "The field request_unit is required and must be 'day' or 'hour'!"
                    )
            if errors:
                return request.make_response(
                    json.dumps(
                        {'errors': errors,
                         'status_code': 400},
                        sort_keys=True, indent=4),
                    headers={'Content-Type': 'application/json;charset=utf-8'},
                    status=400
                )
            # end validation
            time_off_data.update({
                'holiday_type': 'employee',
                'employee_id': employee_id.id,
                'name': name or "",
                'holiday_status_id': holiday_status_id,
                'mode_company_id': employee_id.company_id.id,
                'request_date_from': request_date_from,
            })
            _logger.log(time_off_data)
            time_off = request.env['hr.leave'].with_user(
                user_obj).create(time_off_data)
            return request.make_response(
                json.dumps(
                    {'message': 'Time off request created successfully!',
                     'data': time_off.read(),
                     'status_code': 200},
                    sort_keys=True, indent=4),
                headers={'Content-Type': 'application/json;charset=utf-8'},
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                headers={'Content-Type': 'application/json;charset=utf-8'},
                status=500
            )
