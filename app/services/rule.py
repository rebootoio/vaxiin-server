from flask import current_app as app

from models.rule import Rule, RuleOrder
from exceptions.base import RuleNameNotFound, RuleAlreadyExist


def get_by_name(name):
    rule = app.session.query(Rule).filter(Rule.name == name).first()
    if rule is None:
        app.logger.debug(f"Rule not found! name: '{name}'")
        raise RuleNameNotFound(name)
    else:
        return rule


def create(**kwargs):
    name = kwargs['name']
    try:
        rule = get_by_name(name)
    except RuleNameNotFound:
        app.logger.debug(f"Creating Rule {name}...")
    else:
        raise RuleAlreadyExist(name)

    rule_order = app.session.query(RuleOrder).get(1)

    update_position = False
    before_rule = kwargs.pop('before_rule')
    after_rule = kwargs.pop('after_rule')
    if before_rule is not None:
        new_position = get_by_name(before_rule).position - 1
        update_position = True

    elif after_rule is not None:
        new_position = get_by_name(after_rule).position
        update_position = True

    rule = Rule(**kwargs)

    if update_position:
        rule_order.rules.insert(new_position, rule)
    else:
        rule_order.rules.append(rule)

    app.logger.debug(f"Updating Rule in DB - {rule}")
    app.session.commit()

    return rule


def update(**kwargs):
    name = kwargs['name']
    rule = get_by_name(name)

    update_position = False
    if kwargs.get('before_rule') is not None:
        before_rule = kwargs.pop('before_rule')
        new_position = get_by_name(before_rule).position - 1
        update_position = True

    elif kwargs.get('after_rule') is not None:
        after_rule = kwargs.pop('after_rule')
        new_position = get_by_name(after_rule).position
        update_position = True

    if update_position:
        if rule.position != new_position + 1:
            rule_order = app.session.query(RuleOrder).get(1)
            rule_order.rules.remove(rule)
            if rule.position <= new_position:
                new_position -= 1
            rule_order.rules.insert(new_position, rule)

    for key, val in kwargs.items():
        setattr(rule, key, val)

    app.logger.debug(f"Updating Rule in DB - {rule}")
    app.session.commit()

    return rule


def get_all():
    rule_list = app.session.query(Rule).all()
    return rule_list


def get_all_ordered():
    rule_order = app.session.query(RuleOrder).get(1)
    return rule_order.rules


def get_all_enabled_ordered():
    rules = app.session.query(Rule).filter(Rule.enabled.is_(True)).order_by(Rule.position).all()
    return rules


def delete_by_name(name):
    rule = get_by_name(name)
    rule_order = app.session.query(RuleOrder).get(1)
    app.logger.debug(f"Deleting rule from DB - {rule}")
    app.session.delete(rule)
    rule_order.rules.reorder()
    app.session.commit()
    return rule


def get_rules_with_action(action_name):
    rules = app.session.query(Rule).filter(Rule.actions.contains(f'"{action_name}"')).all()
    return rules
