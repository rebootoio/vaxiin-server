from http import HTTPStatus
from flask import abort
from flask import current_app as app
from flask_restplus import Resource, Namespace

import helpers.logging as logging_helper
import helpers.matcher as matcher_helper
import helpers.validation as validation_helper
import helpers.req_parser as req_parser_helper

import services.rule as rule_service

from exceptions.base import RuleAlreadyExist, RuleNameNotFound, ActionNotFound, StateNotFound, RegexIsInvalid

ns = Namespace('Rule', description='Handle rule')
req_parser = req_parser_helper.get_rule_request_parser()
update_req_parser = req_parser_helper.get_rule_update_request_parser()
name_parser = req_parser_helper.get_name_parser()


@ns.route('/')
class Rule(Resource):

    @ns.doc('Create rule')
    @ns.expect(req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.CONFLICT, 'Rule already exist')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Unprocessable entity')
    def post(self):
        args = req_parser.parse_args()

        req_data = {
            'name': args.get('name'),
            'state_id': args.get('state_id'),
            'regex': args.get('regex'),
            'actions': args.get('actions'),
            'ignore_case': args.get('ignore_case'),
            'enabled': args.get('enabled'),
            'after_rule': args.get('after_rule'),
            'before_rule': args.get('before_rule')
        }

        app.logger.debug(f"Got rule creation request - {logging_helper.dict_to_log_string(req_data)}")

        if req_data['after_rule'] is not None and req_data['before_rule'] is not None:
            abort(HTTPStatus.CONFLICT, f"Please set either 'before_rule' OR 'after_rule'")

        try:
            validation_helper.validate_regex(regex_string=req_data['regex'])
            validation_helper.validate_rule_actions(action_name_list=req_data['actions'])
            validation_helper.validate_rule_state_id(state_id=req_data['state_id'])
            rule = rule_service.create(**req_data)
            matcher_helper.match_all_open_states()
        except RuleAlreadyExist as err:
            abort(HTTPStatus.CONFLICT, f"Rule with name '{err.name}' already exist")
        except ActionNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Action with name '{err.name}' was not found")
        except StateNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"State with id '{err.id}' was not found")
        except RuleNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Rule with name '{err.name}' was not found")
        except RegexIsInvalid as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Regex '{err.regex_string}' is invalid, error is: '{err.error}'")

        return {"rule": rule.to_dict()}, HTTPStatus.OK

    @ns.doc('Update rule')
    @ns.expect(update_req_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Unprocessable entity')
    @ns.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def put(self):
        args = update_req_parser.parse_args()

        req_data = {
            'name': args.get('name'),
            'state_id': args.get('state_id'),
            'regex': args.get('regex'),
            'actions': args.get('actions'),
            'ignore_case': args.get('ignore_case'),
            'enabled': args.get('enabled'),
            'after_rule': args.get('after_rule'),
            'before_rule': args.get('before_rule')
        }

        app.logger.debug(f"Got rule update request - {logging_helper.dict_to_log_string(req_data)}")

        if req_data['after_rule'] is not None and req_data['before_rule'] is not None:
            abort(HTTPStatus.CONFLICT, f"Please set either 'before_rule' OR 'after_rule'")

        try:
            if req_data.get('actions') is not None:
                validation_helper.validate_rule_actions(action_name_list=req_data['actions'])
            if req_data.get('state_id') is not None:
                validation_helper.validate_rule_state_id(state_id=req_data['state_id'])
            if req_data.get('regex') is not None:
                validation_helper.validate_regex(regex_string=req_data['regex'])

            rule = rule_service.update(**{k: v for k, v in req_data.items() if v is not None})
            matcher_helper.match_all_open_states()
        except RuleNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Rule with name '{err.name}' was not found")
        except ActionNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Action with name '{err.name}' was not found")
        except StateNotFound as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"State with id '{err.id}' was not found")
        except RegexIsInvalid as err:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, f"Regex '{err.regex_string}' is invalid, error is: '{err.error}'")

        return {"rule": rule.to_dict()}, HTTPStatus.OK

    @ns.doc('delete rule')
    @ns.expect(name_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Rule not found')
    def delete(self):
        args = name_parser.parse_args()

        req_data = {
            'name': args.get('name')
        }

        app.logger.debug(f"Got rule delete request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            rule = rule_service.delete_by_name(req_data['name'])
            matcher_helper.match_all_open_states()
        except RuleNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Rule with name '{err.name}' was not found")

        return rule.to_dict(), HTTPStatus.OK

    @ns.doc('get rule')
    @ns.expect(name_parser)
    @ns.response(HTTPStatus.OK, 'Success')
    @ns.response(HTTPStatus.BAD_REQUEST, 'Input Validation Error')
    @ns.response(HTTPStatus.NOT_FOUND, 'Rule not found')
    def get(self):
        args = name_parser.parse_args()

        req_data = {
            'name': args.get('name')
        }

        app.logger.debug(f"Got rule get request - {logging_helper.dict_to_log_string(req_data)}")

        try:
            rule = rule_service.get_by_name(req_data['name'])
        except RuleNameNotFound as err:
            abort(HTTPStatus.NOT_FOUND, f"Rule with name '{err.name}' was not found")

        return {"rules": [rule.to_dict()]}, HTTPStatus.OK


@ns.route('/all')
class Rules(Resource):

    @ns.doc('Get all rules')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        rule_list = rule_service.get_all()
        return {"rules": [rule.to_dict() for rule in rule_list]}, HTTPStatus.OK


@ns.route('/ordered')
class OrderedRules(Resource):

    @ns.doc('Get all rules in order')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        rule_list = rule_service.get_all_ordered()
        return {"rules": [rule.to_dict() for rule in rule_list]}, HTTPStatus.OK


@ns.route('/ordered-enabled')
class OrderedEnabledRules(Resource):

    @ns.doc('Get all enabled rules in order')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        rule_list = rule_service.get_all_enabled_ordered()
        return {"rules": [rule.to_dict() for rule in rule_list]}, HTTPStatus.OK
