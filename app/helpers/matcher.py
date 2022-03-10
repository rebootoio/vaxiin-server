import re
from flask import current_app as app

import services.rule as rule_service
import services.state as state_service


def find_matching_rule(text):
    rule_list = rule_service.get_all_enabled_ordered()
    for rule in rule_list:
        if rule.ignore_case:
            compiled_regex = re.compile(rule.regex, re.IGNORECASE)
        else:
            compiled_regex = re.compile(rule.regex)

        match = compiled_regex.search(text)
        if match:
            return rule


def match_all_open_states():
    open_state_list = state_service.get_open()

    for state in open_state_list:
        matching_rule = find_matching_rule(state.ocr_text)
        state.matched_rule = matching_rule.name if matching_rule else None

    app.session.commit()


def match_state(state):
    matching_rule = find_matching_rule(state.ocr_text)
    state.matched_rule = matching_rule.name if matching_rule else None
    app.session.commit()
