# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from typing import Dict, Iterable
from common.exceptions import InvalidManifestError
from common.files import read_file_to_str
from common.logger import Logger
from common.helm import render_manifests, parse_manifests

def generate_constraints(constraints_obj) -> Iterable[Dict]:
    constraints = tuple(constraints_obj)
    validate(constraints)

    return constraints


def validate(constraints: Iterable[Dict]):
    for constraint in constraints:
        if (
            type(constraint) != dict
            or 'spec' not in constraint
            or type(constraint['spec']) != dict
            or 'match' not in constraint['spec']
            or type(constraint['spec']['match']) != dict
        ):
            raise InvalidManifestError('Encountered invalid constraint: ' + str(constraint))

        match = constraint['spec']['match']
        if 'kinds' in match:
            validate_kinds(match['kinds'])
        if 'namespaces' in match:
            validate_namespaces(match['namespaces'])
        if 'excludedNamespaces' in match:
            validate_namespaces(match['excludedNamespaces'])
        if 'namespaceSelector' in match:
            validate_label_selector(match['namespaceSelector'])
        if 'labelSelector' in match:
            validate_label_selector(match['labelSelector'])


def validate_kinds(kinds: list):
    if type(kinds) != list:
        raise InvalidManifestError('Encountered invalid kinds specification: ' + str(kinds))

    if any(is_invalid_kind_specification(kind_specification) for kind_specification in kinds):
        raise InvalidManifestError('Encountered invalid kinds specification: ' + str(kinds))


def validate_namespaces(namespaces: list):
    if type(namespaces) != list or any(type(namespace) != str for namespace in namespaces):
        raise InvalidManifestError('Encountered invalid namespaces list: ' + str(namespaces))


def validate_label_selector(selector: dict):
    if 'matchLabels' in selector:
        if type(selector['matchLabels']) != dict or any(
            type(key) != str or type(value) != str for key, value in selector['matchLabels'].items()
        ):
            raise InvalidManifestError('Encountered invalid matchLabels in: ' + str(selector))

    if 'matchExpressions' in selector:
        for expression in selector['matchExpressions']:
            if (
                'key' not in expression
                or 'operator' not in expression
                or type(expression['key']) != str
                or type(expression['operator']) != str
                or expression['operator'] not in ('In', 'NotIn', 'Exists')
                or (
                    expression['operator'] != 'Exists'
                    and (
                        'values' not in expression
                        or type(expression['values']) != list
                        or any(type(value) != str for value in expression['values'])
                    )
                )
            ):
                raise InvalidManifestError('Encountered invalid matchExpressions in: ' + str(selector))


def is_invalid_kind_specification(kind_specification: dict) -> bool:
    return (
        type(kind_specification) != dict
        or 'apiGroups' not in kind_specification
        or type(kind_specification['apiGroups']) != list
        or 'kinds' not in kind_specification
        or type(kind_specification['kinds']) != list
        or any(type(api_group) != str for api_group in kind_specification['apiGroups'])
        or any(type(k) != str for k in kind_specification['kinds'])
    )

def get_constraints(args) -> Iterable[Dict]:
    logger = Logger.get_instance()

    if args.policy_constraint_templates_file:
        logger.debug('Read constraints.')
        constraint_templates_str = read_file_to_str(args.policy_constraints_file)
    else:
        logger.debug('Rendering constraints.')
        constraint_templates_str = render_manifests(
            args.helm_binary,
            args.policy_chart_constraints,
            args.policy_chart_constraints_values
        )
    logger.debug('Parsing constraints.')
    return parse_manifests(constraint_templates_str)
