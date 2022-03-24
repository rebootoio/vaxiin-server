from http import HTTPStatus
from flask import abort
from flask import current_app as app
from flask_restplus import Resource, Namespace

from helpers.special_keys import SPECIAL_KEYS
import helpers.logging as logging_helper
import helpers.validation as validation_helper
import helpers.req_parser as req_parser_helper

import services.action as action_service

from exceptions.base import ActionAlreadyExist, ActionNotFound, ActionInUse, UnknownActionParamKey, UnknownActionParamValue

ns = Namespace('Action', description='Handle action')
req_parser = req_parser_helper.get_action_request_parser()
name_parser = req_parser_helper.get_name_parser()


@ns.route('/')
class Action(Resource):

    @ns.doc('Create action')
    @ns.expect(req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.CONFLICT, 'Action already exist')
    def post(self):
        args = req_parser.parse_args()

        req_data = {
            'name': args.get('name'),
            'action_type': args.get('action_type'),
            'action_data': args.get('action_data')
        }

        app.logger.debug(f"Got action creation request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_action_data_params(action_data=req_data['action_data'])
            action = action_service.create(**req_data)
        except ActionAlreadyExist as err:
            abort(HTTPStatus.CONFLICT, f"Action with name '{err.name}' already exist")
        except UnknownActionParamKey as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"The param key '{err.key}' is invalid. Allowed keys: [{', '.join(validation_helper.VALID_PARAMS.keys())}]")
        except UnknownActionParamValue as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"The param value '{err.value}' is invalid for '{err.key}'. Allowed values: [{', '.join(validation_helper.VALID_PARAMS[err.key])}]")

        return {"action": action.to_dict()}, HTTPStatus.OK

    @ns.doc('Update action')
    @ns.expect(req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def put(self):
        args = req_parser.parse_args()

        req_data = {
            'name': args.get('name'),
            'action_type': args.get('action_type'),
            'action_data': args.get('action_data')
        }

        app.logger.debug(f"Got action update request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_action_data_params(action_data=req_data['action_data'])
            action = action_service.update(**req_data)
        except ActionNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Action with name '{err.name}' was not found")
        except UnknownActionParamKey as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"The param key '{err.key}' is invalid. Allowed keys: [{', '.join(validation_helper.VALID_PARAMS.keys())}]")
        except UnknownActionParamValue as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"The param value '{err.value}' is invalid for '{err.key}'. Allowed values: [{', '.join(validation_helper.VALID_PARAMS[err.key])}]")

        return {"action": action.to_dict()}, HTTPStatus.OK

    @ns.doc('delete action')
    @ns.expect(name_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Action not found')
    def delete(self):
        args = name_parser.parse_args()

        req_data = {
            'name': args.get('name')
        }

        app.logger.debug(f"Got action delete request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_action_not_in_use(action_name=req_data['name'])
            action = action_service.delete_by_name(req_data['name'])
        except ActionNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Action with name '{err.name}' was not found")
        except ActionInUse as err:
            abort(HTTPStatus.CONFLICT, f"Action with name '{err.name}' was found in rules '{', '.join(err.rules)}'")

        return action.to_dict(), HTTPStatus.OK

    @ns.doc('get action')
    @ns.expect(name_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Action not found')
    def get(self):
        args = name_parser.parse_args()

        req_data = {
            'name': args.get('name')
        }

        app.logger.debug(f"Got action get request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            action = action_service.get_by_name(req_data['name'])
        except ActionNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Action with name '{err.name}' was not found")

        return {"actions": [action.to_dict()]}, HTTPStatus.OK


@ns.route('/all')
class Actions(Resource):

    @ns.doc('Get all actions')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        action_list = action_service.get_all()
        return {"actions": [action.to_dict() for action in action_list]}, HTTPStatus.OK


@ns.route('/list-types')
class ActionTypes(Resource):

    @ns.doc('Get all actions types')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        action_type_list = ['keystroke', 'ipmitool', 'power', 'sleep']
        return {"action_types": action_type_list}, HTTPStatus.OK


@ns.route('/list-power-options')
class ListPowerOptions(Resource):

    @ns.doc('Get all power options (for power action type)')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        power_options_list = ['on', 'off', 'reset', 'graceful', 'status']
        return {"power_options": power_options_list}, HTTPStatus.OK


@ns.route('/list-special-keys')
class ListSpecialKeys(Resource):

    @ns.doc('Get all special keys (for keystroke action type)')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        return {"special_keys": SPECIAL_KEYS}, HTTPStatus.OK
