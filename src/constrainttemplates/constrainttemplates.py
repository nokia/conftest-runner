# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from re import search, MULTILINE
from typing import Dict, Iterable

from common.exceptions import InvalidManifestError
from common.files import write_to_file, read_file_to_str
from common.logger import Logger
from common.helm import render_manifests, parse_manifests

from .policy import Policy


def generate_policies(constraint_templates: str, output_dir: str
) -> Dict[str, Policy]:

    logger = Logger.get_instance()

    validate(constraint_templates)

    logger.debug('Extracting policies from constraint templates.')
    policies = extract_policies(constraint_templates)

    logger.debug('Saving policies into files.')
    for policy in policies.values():
        write_to_file(output_dir, policy.namespace + '.rego', policy.policy)

    return policies


def validate(constraint_templates: Iterable[Dict]):
    for constraint_template in constraint_templates:
        if 'spec' not in constraint_template or 'targets' not in constraint_template['spec']:
            raise InvalidManifestError(
                'Encountered constraint template without targets defined: ' + str(constraint_template)
            )
        for target in constraint_template['spec']['targets']:
            if 'target' not in target:
                raise InvalidManifestError(
                    'Encountered constraint template target without target key defined: ' + str(constraint_template)
                )


def extract_policies(constraint_templates: Iterable[Dict]) -> Dict[str, Policy]:
    policies = (
        (
            constraint_template['spec']['crd']['spec']['names']['kind'],
            search(r'^\s*package\s+(\w+)\s*$', target['rego'], MULTILINE),
            target['rego'],
        )
        for constraint_template in constraint_templates
        for target in constraint_template['spec']['targets']
        if target['target'] == 'admission.k8s.gatekeeper.sh'
    )

    return {
        kind: Policy(namespace_match.groups()[0], policy)
        for kind, namespace_match, policy in policies
        if namespace_match is not None
    }

def get_constraint_templates(args) -> Iterable[Dict]:
    logger = Logger.get_instance()

    if args.policy_constraint_templates_file:
        logger.debug('Read constraint templates.')
        constraint_templates_str = read_file_to_str(args.policy_constraint_templates_file)
    else:
        logger.debug('Rendering constraint templates.')
        constraint_templates_str = render_manifests(
            args.helm_binary,
            args.policy_chart_constraint_templates,
            args.policy_chart_constraint_templates_values
        )
    logger.debug('Parsing constraint templates.')
    return parse_manifests(constraint_templates_str)