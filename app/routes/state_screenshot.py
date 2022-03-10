from io import BytesIO
from http import HTTPStatus
from flask import abort, send_file
from flask import current_app as app
from flask_restplus import Resource, Namespace

import helpers.logging as logging_helper
import helpers.req_parser as req_parser_helper

import services.state as state_service

from exceptions.base import StateNotFound, StateNotFoundForDevice

ns = Namespace('State-Screenshot', description='Handle state screenshot')
id_parser = req_parser_helper.get_id_parser()
uid_parser = req_parser_helper.get_uid_parser()


@ns.route('/by-id')
class StateScreenshotById(Resource):

    @ns.doc('get state screenshot by id')
    @ns.expect(id_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'State not found')
    def get(self):
        args = id_parser.parse_args()

        req_data = {
            'state_id': args.get('id')
        }

        app.logger.debug(f"Got state screenshot get by-id request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            state = state_service.get_by_id(req_data['state_id'])
        except StateNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"State with id '{err.id}' was not found")

        return send_file(BytesIO(state.screenshot), attachment_filename="screenshot.png")


@ns.route('/by-device')
class StateScreenshotByDevice(Resource):

    @ns.doc('get state screenshot by device uid')
    @ns.expect(uid_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'State not found')
    def get(self):
        args = uid_parser.parse_args()

        req_data = {
            'uid': args.get('uid')
        }

        app.logger.debug(f"Got state screenshot get by-device request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            state = state_service.get_by_device(req_data['uid'])
        except StateNotFoundForDevice as err:
            abort(HTTPStatus.NOT_FOUND, f"State for device with uid '{err.uid}' was not found")

        return send_file(BytesIO(state.screenshot), attachment_filename="screenshot.png")
