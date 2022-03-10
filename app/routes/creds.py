from flask import abort
from flask import current_app as app
from http import HTTPStatus
from flask_restplus import Resource, Namespace

import services.creds as creds_service

import helpers.logging as logging_helper
import helpers.validation as validation_helper
import helpers.req_parser as req_parser_helper

from exceptions.base import CredsNameNotFound, CredsAreSetAsDefault, CredsAlreadyExist, CredsInUse, CredsNameIsReserved

ns = Namespace('Creds', description='Handle credentials')
name_parser = req_parser_helper.get_name_parser()
creds_parser = req_parser_helper.get_creds_parser()


@ns.route('/')
class Creds(Resource):
    @ns.doc(description='get creds')
    @ns.expect(name_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Creds not found')
    def get(self):
        args = name_parser.parse_args()

        req_data = {
            'name': args.get('name')
        }

        app.logger.debug(f"Got get creds request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            creds = creds_service.get_by_name(req_data['name'])
        except CredsNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Creds with name '{err.name}' was not found")

        return {"creds": [creds.to_dict()]}, HTTPStatus.OK

    @ns.doc('create creds')
    @ns.expect(creds_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.CONFLICT, 'Creds Already Exist')
    def post(self):
        args = creds_parser.parse_args()

        req_data = {
            'name': args.get('name'),
            'username': args.get('username'),
            'password': args.get('password')
        }

        app.logger.debug(f"Got create creds request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_creds_name(creds_name=req_data['name'])
            creds = creds_service.create(**req_data)
        except CredsAlreadyExist as err:
            abort(HTTPStatus.CONFLICT, f"Creds with name '{err.name}' already exist")
        except CredsNameIsReserved as err:
            abort(HTTPStatus.CONFLICT, f"The name '{err.name}' is reserved")

        return {"creds": creds.to_dict()}, HTTPStatus.OK

    @ns.doc('update creds')
    @ns.expect(creds_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    def put(self):
        args = creds_parser.parse_args()

        req_data = {
            'name': args.get('name'),
            'username': args.get('username'),
            'password': args.get('password')
        }

        app.logger.debug(f"Got update creds request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_creds_name(creds_name=req_data['name'])
            creds = creds_service.update(**{k: v for k, v in req_data.items() if v is not None})
        except CredsNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Creds with name '{err.name}' was not found")
        except CredsNameIsReserved as err:
            abort(HTTPStatus.CONFLICT, f"The name '{err.name}' is reserved")

        return {"creds": creds.to_dict()}, HTTPStatus.OK

    @ns.doc(description='delete creds')
    @ns.expect(name_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.CONFLICT, 'Creds are set as default')
    def delete(self):
        args = name_parser.parse_args()

        req_data = {
            'name': args.get('name')
        }

        app.logger.debug(f"Got delete creds request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_creds_not_in_use(creds_name=req_data['name'])
            creds = creds_service.delete(req_data['name'])
        except CredsAreSetAsDefault as err:
            abort(HTTPStatus.CONFLICT, f"Creds with name '{err.name}' are set as the default")
        except CredsInUse as err:
            abort(HTTPStatus.CONFLICT, f"Creds with name '{err.name}' are used in devices '{', '.join(err.devices)}'")

        return creds.to_dict(), HTTPStatus.OK


@ns.route('/all')
class AllCreds(Resource):

    @ns.doc('Get all creds')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        creds_list = creds_service.get_all()
        return {"creds": [creds.to_dict() for creds in creds_list]}, HTTPStatus.OK


@ns.route('/default')
class DefaultCreds(Resource):

    @ns.doc('Set creds as default')
    @ns.expect(name_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Creds not found')
    def put(self):
        args = name_parser.parse_args()

        req_data = {
            'name': args.get('name')
        }

        app.logger.debug(f"Got set creds as default request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            creds = creds_service.set_as_default(req_data['name'])
        except CredsNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Creds with name '{err.name}' was not found")

        return {"creds": creds.to_dict()}, HTTPStatus.OK
