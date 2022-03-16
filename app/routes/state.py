from http import HTTPStatus
from flask import abort
from flask import current_app as app
from flask_restplus import Resource, Namespace

import helpers.logging as logging_helper
import helpers.matcher as matcher_helper
import helpers.req_parser as req_parser_helper

import services.state as state_service

from exceptions.base import StateNotFound, StateNotFoundForDevice, DeviceNotFound


ns = Namespace('State', description='Handle state')
req_parser = req_parser_helper.get_state_request_parser()
file_req_parser = req_parser_helper.get_state_file_request_parser()
id_parser = req_parser_helper.get_id_parser()
uid_parser = req_parser_helper.get_uid_parser()
state_parser = req_parser_helper.get_state_filter_parser()
state_resolved_parser = req_parser_helper.get_state_resolved_parser()


@ns.route('/')
class State(Resource):

    @ns.doc('Create/Update state')
    @ns.expect(req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Unprocessable entity')
    def put(self):
        args = req_parser.parse_args()

        req_data = {
            'device_uid': args.get('device_uid'),
            'screenshot': args.get('screenshot'),
            'resolved': args.get('resolved')
        }

        app.logger.debug(f"Got state update request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            state = state_service.create_or_update(**req_data)
            matcher_helper.match_state(state)
        except DeviceNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Device with uid '{err.uid}' was not found")

        return {"state": state.to_dict()}, HTTPStatus.OK

    @ns.doc('Create/Update state with file')
    @ns.expect(file_req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Unprocessable entity')
    def post(self):
        args = file_req_parser.parse_args()

        req_data = {
            'device_uid': args.get('device_uid'),
            'screenshot': args.get('screenshot'),
            'resolved': args.get('resolved')
        }

        app.logger.debug(f"Got state update request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            state = state_service.create_or_update_from_file(**req_data)
            matcher_helper.match_state(state)
        except DeviceNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Device with uid '{err.uid}' was not found")

        return {"state": state.to_dict()}, HTTPStatus.OK

    @ns.doc('get state')
    @ns.expect(id_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Rule not found')
    def get(self):
        args = id_parser.parse_args()

        req_data = {
            'id': args.get('id')
        }

        app.logger.debug(f"Got state get request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            state = state_service.get_by_id(req_data['id'])
        except StateNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"State with id '{err.id}' was not found")

        return {"states": [state.to_dict()]}, HTTPStatus.OK


@ns.route('/resolve')
class ResolveStateByDevice(Resource):

    @ns.doc('resolve state by device uid')
    @ns.expect(uid_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'State not found')
    def post(self):
        args = uid_parser.parse_args()

        req_data = {
            'uid': args.get('uid')
        }

        app.logger.debug(f"Got state resolve by-device request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            state = state_service.resolve_by_device(req_data['uid'])
        except StateNotFoundForDevice as err:
            abort(HTTPStatus.NOT_FOUND, f"Unresolved state for device with uid '{err.uid}' was not found")

        return {"states": [state.to_dict()]}, HTTPStatus.OK


@ns.route('/update-resolve')
class UpdateResolveState(Resource):

    @ns.doc('update state resolution')
    @ns.expect(uid_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'State not found')
    def post(self):
        args = state_resolved_parser.parse_args()

        req_data = {
            'state_id': args.get('state_id'),
            'resolved': args.get('resolved')
        }

        app.logger.debug(f"Got state update-resolve  request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            state = state_service.update_resolved_by_id(**req_data)
        except StateNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"State with id '{err.id}' was not found")

        return {"states": [state.to_dict()]}, HTTPStatus.OK


@ns.route('/all')
class States(Resource):

    @ns.doc('Get all states')
    @ns.expect(state_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    def get(self):
        args = state_parser.parse_args()

        req_data = {
            'type': args.get('type'),
            'uid': args.get('uid'),
            'regex': args.get('regex')
        }

        app.logger.debug(f"Got state get all request - {logging_helper.dict_to_log_string(req_data)}")

        if req_data['type'] == "open":
            state_list = state_service.get_open(device_uid=req_data['uid'], regex=req_data['regex'])

        elif req_data['type'] == "resolved":
            state_list = state_service.get_resolved(device_uid=req_data['uid'], regex=req_data['regex'])

        elif req_data['type'] == "unknown":
            state_list = state_service.get_unknown(device_uid=req_data['uid'], regex=req_data['regex'])

        else:
            state_list = state_service.get_all(device_uid=req_data['uid'], regex=req_data['regex'])

        return {"states": [state.to_dict() for state in state_list]}, HTTPStatus.OK
