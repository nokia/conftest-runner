# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from typing import Dict, Iterable
from yaml import safe_dump_all

from admissionreviewrequest import AdmissionReviewRequest
from common.cmd import call_command, log_called_process_output
from common.logger import Logger
from constrainttemplates import Policy
from inputobjects import filter_matching_constraint
import re
from .input import Input
import json
import xml.etree.ElementTree as ET


def strip_ansi(text):
    return re.sub('\033\\[([0-9]+)(;[0-9]+)*m', '', text)


def extract_stdout(output_str, summary):
    result_stripped = strip_ansi(output_str.splitlines()[-1])
    result_summary = re.match(
        r'(?P<tests>\d+) test[s]?, (?P<passed>\d+) passed, (?P<warnings>\d+) warning[s]?,'
        r' (?P<failures>\d+) failure[s]?, (?P<exceptions>\d+) exception[s]?', result_stripped)

    if result_summary is not None:
        for key in summary:
            summary[key] += int(result_summary[key])
    else:
        Logger.get_instance().error(f'Unexpected format of summary output: {result_stripped}')
        exit(1)


def extract_json(output_str, summary):
    results = json.loads(output_str)[0]
    summary['passed'] += results.get('successes', 0)
    summary['failures'] += len(results.get('failures', []))
    summary['warnings'] += len(results.get('warnings', []))
    summary['tests'] = summary['passed'] + summary['warnings'] + summary['failures'] + len(results.get('skipped', []))


def extract_tap(output_str, summary):
    summary['tests'] += int(re.match(r'1..(?P<tests>\d+)', output_str)['tests'])

    summary['failures'] += len(re.findall(r'not ok', output_str[:output_str.find("#")], flags=re.MULTILINE))
    summary['passed'] += len(re.findall(r'^ok', output_str, flags=re.MULTILINE))
    warn_except = output_str[output_str.find("#") - 1: output_str.find("# successes")]
    summary['warnings'] += len(re.findall(r'not ok',
                                          warn_except[:warn_except.find("# exceptions")], flags=re.MULTILINE))
    summary['exceptions'] += len(re.findall(r'not ok',
                                            warn_except[warn_except.find("# exceptions"):], flags=re.MULTILINE))


def extract_table(output_str, summary):
    summary['failures'] += len(re.findall(r'failure', output_str))
    summary['passed'] += len(re.findall(r'success', output_str))
    summary['warnings'] += len(re.findall(r'warning', output_str))
    summary['exceptions'] += len(re.findall(r'exception', output_str))
    summary['tests'] = summary['failures'] + summary['passed'] + summary['warnings'] \
        + summary['exceptions'] + len(re.findall(r'skipped', output_str))


def extract_junit(output_str, summary):
    testsuite = ET.fromstring(output_str).find('testsuite').attrib
    summary['tests'] += int(testsuite.get('tests', 0))
    summary['failures'] += int(testsuite.get('failures', 0))
    summary['passed'] += int(testsuite.get('tests', 0)) - int(testsuite.get('failures', 0))


def extract_summary(result, summary, output):
    output_str = result.stdout if result.stdout else ''
    if output_str:
        if output == 'stdout':
            extract_stdout(output_str, summary)
        elif output == 'json':
            extract_json(output_str, summary)
        elif output == 'tap':
            extract_tap(output_str, summary)
        elif output == 'table':
            extract_table(output_str, summary)
        elif output == 'junit':
            extract_junit(output_str, summary)


def log_overall_summary(summary, logger):
    formatted_output = f'{summary["tests"]} tests, {summary["passed"]} passed, {summary["warnings"]} warnings, ' \
                       f'{summary["failures"]} failures, {summary["exceptions"]} exceptions'
    if summary['tests'] == summary['passed']:
        logger.info("\x1b[32mPASSED " + formatted_output + "\033[0m")
    else:
        logger.info("\x1b[31mFAILURE " + formatted_output + "\033[0m")


def run_conftest(
    policies_dir: str,
    policies: Dict[str, Policy],
    constraints: Iterable[Dict],
    admission_review_namespaces: Iterable[AdmissionReviewRequest],
    admission_review_requests: Iterable[AdmissionReviewRequest],
    output_format: str,
    output_file: str,
    warning_mode: bool,
    fail_fast: bool
):
    logger = Logger.get_instance()

    overall_status_summary = {
        'tests': 0,
        'passed': 0,
        'warnings': 0,
        'failures': 0,
        'exceptions': 0
    }
    output_format = 'stdout' if output_format is None else output_format

    exit_with_fail = False

    for constraint in constraints:
        logger.debug('')
        logger.debug('Filtering admission review requests matching constraint ' + constraint['metadata']['name'])
        admission_review_requests_matching_constraint = filter_matching_constraint(
            admission_review_requests, constraint['spec']['match'], admission_review_namespaces
        )

        parameters = constraint['spec']['parameters'] if 'parameters' in constraint['spec'] else {}
        stdin = safe_dump_all(
            Input(admission_review_request, parameters).as_dict()
            for admission_review_request in admission_review_requests_matching_constraint
        )
        if stdin == '':
            logger.debug('No admission review request matching constraint found. Skipping.')
            continue

        logger.info('')
        logger.info('Calling conftest command for constraint ' + constraint['metadata']['name'])
        if output_file:
            command = f'conftest test - --policy {policies_dir} --namespace {policies[constraint["kind"]].namespace} ' \
                      f'-o {output_format} --no-color || exit 0 '
        else:
            command = f'conftest test - --policy {policies_dir} --namespace {policies[constraint["kind"]].namespace} ' \
                  f'-o {output_format} || exit 0 '
        logger.debug(command)

        result = call_command(command, stdin)
        log_called_process_output(logger.info, result)
        if result.stderr != '' or 'FAIL' in result.stdout:
            logger.error('One or more tests fail to run')
            if fail_fast:
                if warning_mode:
                    exit(0)
                else:
                    exit(1)
            elif not warning_mode:
                exit_with_fail = True
        extract_summary(result, overall_status_summary, output_format)
        logger.info(result.stdout)

    log_overall_summary(overall_status_summary, logger)

    if exit_with_fail:
        exit(1)
