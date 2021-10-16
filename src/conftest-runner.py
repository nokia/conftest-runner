#!/usr/bin/env python3
# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from cli.parser import parse_and_validate_args
from common.exceptions import ConftestError, FileError, InvalidManifestError, InvalidParametersError, TemplateError
from common.logger import Logger
from conftest import run_conftest
from constraints import generate_constraints, get_constraints
from constrainttemplates import generate_policies, get_constraint_templates
from constrainttemplates.policy import create_policies_dir
from inputobjects import convert_kubernetes_objects_to_admission_reviews, get_kubernetes_objects
from namespaces import get_namespaces, convert_namespaces_to_admission_reviews

def main():
    args = parse_and_validate_args()

    kubernetes_objects = get_kubernetes_objects(args)
    admission_review_requests = convert_kubernetes_objects_to_admission_reviews(
        kubernetes_objects, args.input_chart_namespace)

    policies_dir = create_policies_dir(args)

    constraint_templates_obj = get_constraint_templates(args)
    policies = generate_policies(constraint_templates_obj, policies_dir)

    constraints_obj = get_constraints(args)
    constraints = generate_constraints(constraints_obj)

    namespaces = get_namespaces(args)
    #conversion is not necessary but it simplifies the code - see usage of filter_matching_constraint
    admission_review_namespaces = convert_namespaces_to_admission_reviews(namespaces)

    run_conftest(policies_dir, policies, constraints,
                 admission_review_namespaces, admission_review_requests,
                 args.output_format, args.output_file, args.warning_mode, args.fail_fast)

if __name__ == '__main__':
    try:
        main()
    except (TemplateError, FileError, ConftestError, InvalidManifestError, InvalidParametersError) as e:
        Logger.get_instance().error(e)
        exit(1)
