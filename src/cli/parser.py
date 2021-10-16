# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from common.cmd import exit_if_command_not_found
from logging import DEBUG
from common.logger import Logger, set_log_level

def parse_and_validate_args() -> Namespace:
    parser = ArgumentParser(
        description="""Tools is a glue between conftest and the Gatekeeper.
It allows verifying Kubernetes objects against Gatekeeper constraints.
The Kubernetes objects and the Gatekeeper constraints can be in a Helm chart form. 
Verification can be run in Continuous Integration (CI/CD) pipelines without the Kubernetes cluster access or even the Gatekeeper.

conftest-runner performs the following steps:
- templates input Helm chart, to get Kubernetes objects manifests
- convert Kubernetes objects to AdmissionReview objects (form consumed by the Gatekeeper constraints)
- extract Rego code from the Gatekeeper constraint templates
- transform extracted Rego code into conftest tests
- run conftest

Required dependencies: 
- installed helm3
- installed conftest

Example run:

python3 conftest-runner.py \


""",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        '--input-kubernetes-objects',
        '-iko',
        dest='input_kubernetes_objects',
        action='store',
        help='local location of file with the kubernetes objects',
        metavar='<location>',
    )

    parser.add_argument(
        '--input-chart',
        '-ic',
        dest='input_chart',
        action='store',
        help='URL or local chart location',
        metavar='<location>',
    )

    parser.add_argument(
        '--input-chart-values',
        '-icv',
        dest='input_chart_values',
        action='store',
        help='user supplied values.yaml file used for chart rendering',
        metavar='<path>',
    )

    parser.add_argument(
        '--input-chart-namespace',
        '-icn',
        dest='input_chart_namespace',
        action='store',
        help='namespace used for chart rendering',
        metavar='<name>',
        default='default',
    )

    parser.add_argument(
        '--input-chart-release-name',
        '-icrn',
        dest='input_chart_release_name',
        action='store',
        help='release name used for chart rendering',
        metavar='<name>',
        default='release',
    )

    parser.add_argument(
        '--policy-constraint-templates-file',
        '-pctf',
        dest='policy_constraint_templates_file',
        action='store',
        help='local chart location',
        metavar='<location>',
    )

    parser.add_argument(
        '--policy-chart-constraint-templates',
        '-pcct',
        dest='policy_chart_constraint_templates',
        action='store',
        help='URL or local chart location',
        metavar='<location>',
    )

    parser.add_argument(
        '--policy-chart-constraint-templates-values',
        '-pcctv',
        dest='policy_chart_constraint_templates_values',
        action='store',
        help='user supplied values.yaml file used for chart rendering',
        metavar='<path>',
    )

    parser.add_argument(
        '--policy-constraints-file',
        '-pcf',
        dest='policy_constraints_file',
        action='store',
        help='local chart location',
        metavar='<location>',
    )

    parser.add_argument(
        '--policy-chart-constraints',
        '-pcc',
        dest='policy_chart_constraints',
        action='store',
        help='URL or local chart location',
        metavar='<location>',
    )

    parser.add_argument(
        '--policy-chart-constraints-values',
        '-pccv',
        dest='policy_chart_constraints_values',
        action='store',
        help='user supplied values.yaml file used for chart rendering',
        metavar='<path>',
    )

    parser.add_argument(
        '--input-namespaces-file',
        '-inf',
        dest='input_namespaces_file',
        action='store',
        help='file path that contains Kubernetes namespaces yaml. Namespace labels will be read from this files. '
        + '(necessary if constraints have namespaceSelector settings)',
        metavar='<path>',
    )

    parser.add_argument(
        '--output-format',
        '-o',
        dest='output_format',
        action='store',
        help='conftest command output format',
        metavar='<output>',
        choices=('stdout', 'json', 'tap', 'table', 'junit'),
    )

    parser.add_argument(
        '--output-file',
        '-of',
        dest='output_file',
        action='store',
        help='path to file where output will be saved',
        metavar='<output>',
    )

    parser.add_argument(
        '--verbose',
        '-v',
        dest='verbose',
        action='store_true',
        help='use verbose output',
    )

    parser.add_argument(
        '--warning-mode',
        '-w',
        dest='warning_mode',
        action='store_true',
        help='run conftest in warning mode',
    )

    parser.add_argument(
        '--no-cleanup',
        '-nc',
        dest='no_cleanup',
        action='store_true',
        help='disable cleanup temporary files',
    )

    parser.add_argument(
        '--fail-fast',
        '-ff',
        dest='fail_fast',
        action='store_true',
        help='exit on first failed test',
    )

    parser.add_argument(
        '--helm-binary',
        '-hb',
        dest='helm_binary',
        action='store',
        default="helm3",
        help='path to helm 3 binary',
        metavar='<binary path>',
    )

    args = parser.parse_args()
    if (args.input_kubernetes_objects and args.input_chart):
        parser.error("Options --input-kubernetes-objects and --input-chart are mutually exclusive!")
    if (not args.input_kubernetes_objects and not args.input_chart):
        parser.error("One of --input-kubernetes-objects/--input-chart options must be set!")

    if (args.policy_constraint_templates_file and args.policy_chart_constraint_templates):
        parser.error("Options --policy-constraint-templates-file and --policy-chart-constraint-templates are mutually exclusive!")
    if (not args.policy_constraint_templates_file and not args.policy_chart_constraint_templates):
        parser.error("One of --policy-constraint-templates-file/--policy-chart-constraint-templates options must be set!")

    if (args.policy_constraints_file and args.policy_chart_constraints):
        parser.error("Options --policy-constraints-file and --policy-chart-constraints are mutually exclusive!")
    if (not args.policy_constraints_file and not args.policy_chart_constraints):
        parser.error("One of --policy-constraints-file/--policy-chart-constraints options must be set!")

    if args.output_file is not None:
        Logger(args.output_file)
    if args.verbose:
        set_log_level(DEBUG)

    if (args.input_chart or args.policy_chart_constraint_templates or args.policy_chart_constraints):
        exit_if_command_not_found(f"{args.helm_binary} version -c", args.verbose)

    exit_if_command_not_found("conftest --version", args.verbose)

    return args
