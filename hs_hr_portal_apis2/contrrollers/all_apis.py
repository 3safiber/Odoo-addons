import odoo
from odoo import http, api, fields
from odoo.http import request, Response, route
from datetime import datetime
from datetime import date

import functools
import json
import base64
import logging
from odoo import SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError
_logger = logging.getLogger(__name__)


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    return {
        "code": status,
        "message": "Successful Request",
        "data": data
    }


def invalid_response(typ, message=None, status=401):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    return {
        "code": status,
        "message": str(message) if str(message) else "wrong arguments (missing validation)",
        "data": {}
    }


def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get('Authorization')
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = request.env["api.access.token"].sudo().search([("token", "=", access_token)],
                                                                          order="id DESC", limit=1)
        if access_token_data.find_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        # request.uid = access_token_data.user_id.id
        request.update_env(user=access_token_data.user_id.id)
        return func(self, *args, **kwargs)

    return wrap


class BusinessTripController(http.Controller):
    @http.route("/v1/api/login", methods=["POST"], type='json', auth="none", csrf=False, cors='*')
    def api_login(self):

        # Parse the request body as JSON
        data = json.loads(request.httprequest.data)

        # Get the necessary parameters from the body
        db = data.get("db")
        username = data.get("login")
        password = data.get("password")

        # Check if all required parameters are present
        if not all([db, username, password]):
            return invalid_response(
                "missing error",
                "either of the following are missing [db, username, password]",
                403
            )

        # Attempt to authenticate the user
        try:
            request.session.authenticate(db, username, password)
        except AccessError as aee:
            return invalid_response("Access error", "Error: %s" % aee.name)
        except AccessDenied as ade:
            return invalid_response("Access denied", "Login, password or db invalid")
        except Exception as e:
            # Invalid database error
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response("wrong database name", error, 403)

        # Get the user ID after successful authentication
        uid = request.session.uid
        user_obj = request.env['res.users'].browse(uid)
        # If authentication fails
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        # Generate access token for the authenticated user
        access_token = request.env["api.access.token"].find_or_create_token(
            user_id=uid, create=True)

        # Return successful response with access token
        return {
            "code": 200,
            "message": "Active Access Token",
            "data": {
                "uid": uid,
                "access_token": access_token,
                "name": user_obj.name,
                "login": user_obj.login,
                "employee_id": user_obj.employee_id.id,
            }
        }

    @validate_token
    @http.route('/v1/api/approve_trip', auth="none", type='http', methods=['POST'], csrf=False, cors='*')
    def api_approve_trip(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env
            data = json.loads(request.httprequest.data)
            trip_obj = env['approval.request']
            trip_id = trip_obj.with_user(user_obj).browse(int(data['trip_id']))
            if trip_id:
                line_id = trip_id.approver_ids.filtered(
                    lambda x: x.user_id == user_obj)
                if line_id:
                    if line_id.status != 'approved':
                        trip_id.with_user(user_obj).action_approve()
                        res = {
                            'msg': 'Approved successfully'
                        }
                    else:
                        res = {
                            'msg': 'This is user already approved before'
                        }
                else:
                    res = {
                        'msg': 'This user can not approve this trip'
                    }
            else:
                res = {
                    'msg': 'There is no trip with this ID'
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
    @http.route('/v1/api/refuse_trip', auth="none", type='http', methods=['POST'], csrf=False, cors='*')
    def api_refuse_trip(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env
            data = json.loads(request.httprequest.data)
            trip_obj = env['approval.request']
            trip_id = trip_obj.with_user(user_obj).browse(int(data['trip_id']))
            if trip_id:
                line_id = trip_id.approver_ids.filtered(
                    lambda x: x.user_id == user_obj)
                if line_id:
                    if line_id.status == 'approved':
                        res = {
                            'msg': 'This is user already approved before'
                        }
                    else:
                        trip_id.with_user(user_obj).action_refuse()
                        res = {
                            'msg': 'Refused successfully'
                        }
                else:
                    res = {
                        'msg': 'This user can not refuse this trip'
                    }
            else:
                res = {
                    'msg': 'There is no trip with this ID'
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
    @http.route('/v1/api/get_approve_line_status/<int:trip_id>', auth="none", type='http', methods=['GET'], csrf=False, cors='*')
    def api_get_approve_line_status(self, trip_id):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env

            approval_line_obj = env['approval.approver']
            approval_line_ids = approval_line_obj.with_user(user_obj).search(
                [('request_id', '=', trip_id)])

            if approval_line_ids:
                status_line = []
                for approve in approval_line_ids:
                    status_line.append({
                        'user_id': approve.user_id.id,
                        'user_name': approve.user_id.name,
                        'status': approve.status
                    })

                # Adding request status
                request_status = approval_line_ids[0].request_id.request_status if approval_line_ids else ''

                res = {
                    'msg': 'successfully',
                    'status line': status_line,
                    'request status': request_status
                }
            else:
                res = {
                    'msg': 'There is no lines for this request'
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
    @http.route('/v1/api/create_trip_lookup', auth="none", type='http', methods=['GET'], csrf=False, cors='*')
    def api_get_all_projects_and_approval_types(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env
            projects = env['project.project'].with_user(user_obj).search([])
            project_data = []
            for project in projects:
                project_data.append({
                    'id': project.id,
                    'name': project.name,
                })

            approval_types = env['approval.category'].with_user(
                user_obj).search([])
            approval_data = []
            for approval in approval_types:
                approval_data.append({
                    'id': approval.id,
                    'name': approval.name
                })

            trip_types = [
                {'key': 'business_trip_foreigners_ksa',
                    'value': 'Business Trip for foreigners to KSA'},
                {'key': 'visit_clients', 'value': 'Visit Clients'},
                {'key': 'short_term', 'value': 'Short-term Business Trip'},
                {'key': 'medium_term', 'value': 'Medium-term Business Trip'},
                {'key': 'long_term', 'value': 'Long-term Business Trip'},

            ]

            return Response(
                json.dumps({
                    'projects': project_data,
                    'approval_categories': approval_data,
                    'other_trip_types': trip_types,
                }, sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=200
            )

        except Exception as e:
            return Response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                content_type='application/json;charset=utf-8', status=500
            )

    @validate_token
    @http.route('/v1/api/approval_request', auth="none", type='http', methods=['POST'], csrf=False, cors='*')
    def api_create_approval_request(self, **kwargs):
        """Create an approval request with project_id validation when approval_cycle_type is 'project'."""
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)

            data = json.loads(request.httprequest.data)

            employee_id = data.get('employee_id')
            # name = data.get('name')
            location_of_the_trip = data.get('location_of_the_trip')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            distance = data.get('distance')
            approval_cycle_type = data.get('approval_cycle_type')
            accommodation_paid_by_company = data.get(
                'accommodation_paid_by_company')
            international_trip = data.get('international_trip')
            car_provided = data.get('car_provided')
            tickets_allowance = data.get('tickets_allowance')
            category_id = data.get('category_id')
            request_owner_id = data.get('request_owner_id')
            project_id = data.get('project_id')
            number_of_trips = data.get('number_of_trips')
            trip_type = data.get('trip_type')

            if not all([start_date, end_date]):
                return request.make_response(
                    json.dumps(
                        {'error': 'Missing required fields: start_date and end_date are mandatory',
                            'status_code': 400},
                        sort_keys=True, indent=4),
                    headers={'Content-Type': 'application/json;charset=utf-8'},
                    status=400
                )

            if approval_cycle_type == 'project' and not project_id:
                return request.make_response(
                    json.dumps(
                        {'error': 'Missing project_id: project_id is mandatory when approval_cycle_type is "project"',
                         'status_code': 400},
                        sort_keys=True, indent=4),
                    headers={'Content-Type': 'application/json;charset=utf-8'},
                    status=400
                )

            approval_request = request.env['approval.request'].with_user(user_obj).sudo().create({
                'name': "Business Trip",
                'employee_id': employee_id,
                'request_owner_id': request_owner_id,
                'category_id': category_id,
                'date_start': start_date,
                'date_end': end_date,
                'location': location_of_the_trip,
                'distance': distance,
                'approval_cycle_type': approval_cycle_type,
                'accommodation_paid_by_company': accommodation_paid_by_company,
                'international_trip': international_trip,
                'car_provided': car_provided,
                'tickets_allowance': tickets_allowance,
                'number_of_trips': number_of_trips,
                'trip_type': trip_type,

                'project_id': project_id if approval_cycle_type == 'project' else False,
            })
            approval_request._compute_daily_allowance()
            res = {
                'msg': "Approval request created successfully",
                'status': "success",
                'approval_request_id': approval_request.id,
                'created_by': user_obj.name
            }

            return request.make_response(
                json.dumps(res, sort_keys=True, indent=4),
                headers={'Content-Type': 'application/json;charset=utf-8'},
                status=201
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e), 'status_code': 500},
                           sort_keys=True, indent=4),
                headers={'Content-Type': 'application/json;charset=utf-8'},
                status=500
            )

    @validate_token
    @http.route('/v1/api/api_get_all_trips_by_employee_id/<int:employee_id>', auth="none", type='http', methods=['GET'],
                csrf=False, cors='*')
    def api_get_all_trips_by_employee_id(self, employee_id):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)

            if not employee_id:
                res = {
                    'msg': 'Employee ID not found!'
                }
                return Response(
                    json.dumps(res, sort_keys=True, indent=4),
                    content_type='application/json;charset=utf-8', status=400
                )

            trip_obj = request.env['approval.request']
            trip_ids = trip_obj.with_user(user_obj).search(
                [('employee_id', '=', int(employee_id))])

            if trip_ids:
                list_trips = []
                for trip in trip_ids:
                    list_trips.append({
                        'id': trip.id,
                        'employee': trip.employee_id.name,
                        'date_start': trip.date_start.strftime('%Y-%m-%d'),
                        'date_end': trip.date_end.strftime('%Y-%m-%d'),
                        'status': trip.request_status,
                        'total_compensation': trip.total_compensation,
                        'employee_grade': trip.employee_id.grade_id.name,
                        'trip_type': trip.trip_type,
                        'request_manager': trip.request_manager_id.name
                    })
                res = {
                    'msg': 'Trips found successfully',
                    'trips': list_trips
                }
            else:
                res = {
                    'msg': 'There are no trips for this employee!'
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
    @http.route('/v1/api/api_get_trips_to_approves_by_user_id', auth="none", type='http', methods=['GET'], csrf=False,
                cors="*")
    def api_get_trips_to_approves_by_user_id(self):
        try:
            user_id = request.uid
            user_obj = request.env['res.users'].browse(user_id)
            env = request.env
            trip_obj = env['approval.request']
            trip_ids = trip_obj.with_user(user_obj).search([
                ('approver_ids.user_id', '=', user_id)
            ])
            print(trip_ids)
            if not trip_ids:
                res = {
                    'msg': 'There are no trips for approved!'
                }
            else:
                list_trips = [{
                    'id': trip.id,
                    'date_start': trip.date_start.strftime('%Y-%m-%d'),
                    'date_end': trip.date_end.strftime('%Y-%m-%d'),
                    'employee': trip.employee_id.name,
                    'location_trip': trip.location_trip,
                    'trip_type': trip.trip_type,
                    'approval_cycle_type': trip.approval_cycle_type,
                    'employee_grade': trip.employee_grade.name,
                    'total_days': trip.total_days,
                    'total_compensation': trip.total_compensation,
                    'status': trip.request_status,
                    'approver_status': trip.approver_ids.user_id.status,
                } for trip in trip_ids]
                res = {
                    'msg': 'Fetching successfully',
                    'trips': list_trips
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
            request_date_from = data.get('request_date_from')
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
                    request_date_to = data.get('request_date_to')
                    if not request_date_to:
                        errors.append(
                            'The field request_date_to is required')
                    else:
                        time_off_data['request_date_to'] = request_date_to
                case 'hour':
                    request_hour_from = data.get('request_hour_from')
                    request_hour_to = data.get('request_hour_to')
                    if not request_hour_from or not request_hour_to:
                        errors.append(
                            'The fields request_hour_from and request_hour_to is required')
                    else:
                        time_off_data.update({
                            'request_unit_hours': True,
                            'request_hour_from': request_hour_from,
                            'request_hour_to': request_hour_to
                        })
                case _:
                    errors.append(
                        "The field request_unit is required and must be 'day' or 'hour'!")
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
            print(time_off_data)
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
