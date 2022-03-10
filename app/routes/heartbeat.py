from http import HTTPStatus
from flask import current_app as app
from flask_restplus import Resource, Namespace

import services.device as device_service
import helpers.logging as logging_helper
import helpers.req_parser as req_parser_helper

ns = Namespace('Heartbeart', description='Get heartbeat from device')
req_parser = req_parser_helper.get_agent_heartbeat_request_parser()


@ns.route('/')
class Heartbeat(Resource):

    @ns.doc('send heartbeat')
    @ns.expect(req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    def put(self):
        args = req_parser.parse_args()

        req_data = {
            'uid': args.get('uid'),
            'agent_version': args.get('agent_version'),
            'heartbeat_timestamp': args.get('heartbeat_timestamp'),
            'ipmi_ip': args.get('ipmi_ip'),
            'model': args.get('model'),
            'creds_name': args.get('creds_name')
        }

        app.logger.debug(f"Got heartbeat request - {logging_helper.dict_to_log_string(req_data)}")

        invalid_creds = device_service.heartbeat(**req_data)
        if invalid_creds:
            return {"message": "Provided creds name was not found, omitted it from update"}, 211
        else:
            return {"message": "OK"}, HTTPStatus.OK
