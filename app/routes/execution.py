from http import HTTPStatus
from flask import abort
from flask import current_app as app
from flask_restplus import Resource, Namespace

import helpers.logging as logging_helper
import helpers.validation as validation_helper
import helpers.req_parser as req_parser_helper

import services.execution as execution_service

from exceptions.base import WorkNotFound, StateNotFound

ns = Namespace('Execution', description='Handle execution')
req_parser = req_parser_helper.get_execution_request_parser()
id_parser = req_parser_helper.get_id_parser()


@ns.route('/')
class Execution(Resource):

    @ns.doc('Report execution')
    @ns.expect(req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Unprocessable entity')
    def post(self):
        args = req_parser.parse_args()

        req_data = {
            'work_id': args.get('work_id'),
            'state_id': args.get('state_id'),
            'action_name': args.get('action_name'),
            'trigger': args.get('trigger'),
            'status': args.get('status'),
            'run_data': args.get('run_data'),
            'elapsed_time': args.get('elapsed_time')
        }

        app.logger.debug(f"Got execution creation request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            validation_helper.validate_execution(work_id=req_data['work_id'], state_id=req_data['state_id'])
            execution = execution_service.create(**req_data)
        except WorkNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Work with id '{err.id}' was not found")
        except StateNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"State with id '{err.id}' was not found")

        return {'execution': execution.to_dict()}, HTTPStatus.OK


@ns.route('/all/by-work-id')
class ExecutionsByWorkId(Resource):

    @ns.doc('Get all executions by work id')
    @ns.expect(id_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    def get(self):
        args = id_parser.parse_args()

        req_data = {
            'id': args.get('id')
        }

        app.logger.debug(f"Got all executions get by-work-id request - {logging_helper.dict_to_log_string(req_data)}")

        execution_list = execution_service.get_by_work_id(req_data['id'])
        return {"executions": [execution.to_dict() for execution in execution_list]}, HTTPStatus.OK
