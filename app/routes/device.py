from flask import abort
from flask import current_app as app
from http import HTTPStatus
from flask_restplus import Resource, Namespace

import services.device as device_service

import helpers.logging as logging_helper
import helpers.validation as validation_helper
import helpers.req_parser as req_parser_helper

from exceptions.base import DeviceNotFound, DeviceAlreadyExist, CredsNameNotFound, DeviceInUse

ns = Namespace('Device', description='Handle device')
uid_parser = req_parser_helper.get_uid_parser()
device_parser = req_parser_helper.get_device_parser()


@ns.route('/')
class Device(Resource):
    @ns.doc(description='get device')
    @ns.expect(uid_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Device not found')
    def get(self):
        args = uid_parser.parse_args()

        req_data = {
            'uid': args.get('uid')
        }

        app.logger.debug(f"Got get device request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            device = device_service.get_by_uid(req_data['uid'])
        except DeviceNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Device with uid '{err.uid}' was not found")

        return {"devices": [device.to_dict()]}, HTTPStatus.OK

    @ns.doc('create device')
    @ns.expect(device_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.CONFLICT, 'Device already exist')
    @ns.response(HTTPStatus.NOT_FOUND, 'Credentials were not found')
    def post(self):
        args = device_parser.parse_args()

        req_data = {
            'uid': args.get('uid'),
            'ipmi_ip': args.get('ipmi_ip'),
            'creds_name': args.get('creds_name'),
            'model': args.get('model'),
            'zombie': args.get('zombie')
        }

        app.logger.debug(f"Got create device request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            device = device_service.create(**{k: v for k, v in req_data.items() if v is not None})
        except DeviceAlreadyExist as err:
            abort(HTTPStatus.CONFLICT, f"Device with uid '{err.uid}' already exist")
        except CredsNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Creds with name '{err.name}' was not found")

        return {"device": device.to_dict()}, HTTPStatus.OK

    @ns.doc('update device')
    @ns.expect(device_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Device not found')
    def put(self):
        args = device_parser.parse_args()

        req_data = {
            'uid': args.get('uid'),
            'ipmi_ip': args.get('ipmi_ip'),
            'creds_name': args.get('creds_name'),
            'model': args.get('model'),
            'zombie': args.get('zombie')
        }

        app.logger.debug(f"Got update device request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            device = device_service.update(**{k: v for k, v in req_data.items() if v is not None})
        except DeviceNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Device with uid '{err.uid}' was not found")
        except CredsNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Creds with name '{err.name}' was not found")

        return {"device": device.to_dict()}, HTTPStatus.OK

    @ns.doc(description='delete device')
    @ns.expect(uid_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Device not found')
    def delete(self):
        args = uid_parser.parse_args()

        req_data = {
            'uid': args.get('uid')
        }

        app.logger.debug(f"Got delete device request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_device_not_in_use(device_uid=req_data['uid'])
            device = device_service.delete_by_uid(req_data['uid'])
        except DeviceNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Device with uid '{err.uid}' was not found")
        except DeviceInUse as err:
            abort(HTTPStatus.CONFLICT, f"Device with uid '{err.uid}' has an unresolved state with ID {err.state_id}")

        return device.to_dict(), HTTPStatus.OK


@ns.route('/all')
class Devices(Resource):

    @ns.doc('Get all devices')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        devices_list = device_service.get_all()
        return {"devices": [device.to_dict() for device in devices_list]}, HTTPStatus.OK


@ns.route('/zombies')
class ZombieDevices(Resource):

    @ns.doc('Get all zombie devices')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        devices_list = device_service.get_zombies()
        return {"devices": [device.to_dict() for device in devices_list]}, HTTPStatus.OK
