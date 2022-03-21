from http import HTTPStatus
from flask import abort
from flask import current_app as app
from flask_restplus import Resource, Namespace

import helpers.logging as logging_helper
import helpers.req_parser as req_parser_helper
import helpers.convertor as convertor_helper

import services.work as work_service

from exceptions.base import WorkNotFound, WorkNotFoundForDevice, WorkIsNotPending, ActionNotFound, RuleNameNotFound, DeviceNotFound, WorkAlreadyExistForDevice, ManualWorkMustHaveRuleOrActions


ns = Namespace('Work', description='Handle work')
work_parser = req_parser_helper.get_work_request_parser()
id_parser = req_parser_helper.get_id_parser()
uid_parser = req_parser_helper.get_uid_parser()
work_complete_parser = req_parser_helper.get_work_complete_parser()


@ns.route('/')
class Work(Resource):

    @ns.doc('Create work')
    @ns.expect(work_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Unprocessable entity')
    @ns.response(HTTPStatus.CONFLICT, 'Work already exist for device')
    def post(self):
        args = work_parser.parse_args()

        req_data = {
            'device_uid': args.get('device_uid'),
            'actions': args.get('actions'),
            'rule': args.get('rule')
        }

        try:
            work_data = convertor_helper.create_manual_work_for_device(**req_data)
            work = work_service.create(work_data)

        except WorkAlreadyExistForDevice as err:
            abort(HTTPStatus.CONFLICT, f"Device '{err.device_uid}' already has pending work")
        except DeviceNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Device with uid '{err.uid}' was not found")
        except ActionNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Action with name '{err.name}' was not found")
        except RuleNameNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Rule with name '{err.name}' was not found")
        except ManualWorkMustHaveRuleOrActions:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, "Either 'rule' or 'actions' must be set for work")

        return {"work": work.to_dict()}, HTTPStatus.OK


@ns.route('/assign')
class AssignWork(Resource):

    @ns.doc('get work assignment')
    @ns.response(HTTPStatus.OK, 'Success')
    def post(self):

        assignment = work_service.get_assignment()

        return {"assignment": assignment}, HTTPStatus.OK


@ns.route('/by-id')
class WorkById(Resource):

    @ns.doc('get work by id')
    @ns.expect(id_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Work not found')
    def get(self):
        args = id_parser.parse_args()

        req_data = {
            'work_id': args.get('id')
        }

        app.logger.debug(f"Got work get by-id request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            work = work_service.get_by_id(req_data['work_id'])
        except WorkNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Work with id '{err.id}' was not found")

        return {"works": [work.to_dict()]}, HTTPStatus.OK

    @ns.doc('complete work by id')
    @ns.expect(work_complete_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Work not found')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Unprocessable entity')
    def post(self):
        args = work_complete_parser.parse_args()

        req_data = {
            'work_id': args.get('work_id'),
            'status': args.get('status')
        }

        app.logger.debug(f"Got work complete by-id request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            work = work_service.complete_by_id(work_id=req_data['work_id'], status=req_data['status'])
        except WorkNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Work with id '{err.id}' was not found")
        except WorkIsNotPending as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Work with id '{err.id}' is not pending")

        return {"work": work.to_dict()}, HTTPStatus.OK


@ns.route('/by-device')
class WorkByDevice(Resource):

    @ns.doc('get work by device uid')
    @ns.expect(uid_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Work not found')
    def get(self):
        args = uid_parser.parse_args()

        req_data = {
            'uid': args.get('uid')
        }

        app.logger.debug(f"Got work get by-device request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            work = work_service.get_by_device(req_data['uid'])
        except WorkNotFoundForDevice as err:
            abort(HTTPStatus.NOT_FOUND, f"Work for device with uid '{err.uid}' was not found")

        return {"works": [work.to_dict()]}, HTTPStatus.OK


@ns.route('/all')
class Works(Resource):

    @ns.doc('Get all works')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        work_list = work_service.get_all()
        return {"works": [work.to_dict() for work in work_list]}, HTTPStatus.OK


@ns.route('/all/by-device')
class WorksByDevice(Resource):

    @ns.doc('Get all works by device')
    @ns.expect(uid_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    def get(self):
        args = uid_parser.parse_args()

        req_data = {
            'uid': args.get('uid')
        }

        app.logger.debug(f"Got all works get by-device request - {logging_helper.dict_to_log_string(req_data)}")

        work_list = work_service.get_all_by_device(req_data['uid'])
        return {"works": [work.to_dict() for work in work_list]}, HTTPStatus.OK


@ns.route('/pending')
class PendingWorks(Resource):

    @ns.doc('Get all pending works')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        work_list = work_service.get_pending()
        return {"works": [work.to_dict() for work in work_list]}, HTTPStatus.OK


@ns.route('/completed')
class CompletedWorks(Resource):

    @ns.doc('Get all completed works')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        work_list = work_service.get_completed()
        return {"works": [work.to_dict() for work in work_list]}, HTTPStatus.OK
