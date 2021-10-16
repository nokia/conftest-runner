# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from subprocess import CompletedProcess, CalledProcessError, PIPE, run

from common.logger import Logger


def call_command(command: str, stdin='', stdout=PIPE, stderr=PIPE) -> CompletedProcess:
    if stdin:
        return run(command, shell=True, check=True, stdout=stdout, stderr=stderr, universal_newlines=True, input=stdin)
    return run(command, shell=True, check=True, stdout=stdout, stderr=stderr)


def log_called_process_output(logger_func, process_result):
    error_output_str = process_result.stderr if process_result.stderr else ''
    output_str = process_result.stdout if process_result.stdout else ''
    for line in error_output_str.strip().splitlines():
        logger_func('[stderr]: ' + str(line))
    for line in output_str.strip().splitlines():
        logger_func(line)


def exit_if_command_not_found(command: str, verbose: bool):
    logger = Logger.get_instance()
    try:
        if verbose:
            logger.debug(command.split()[0] + " " + call_command(command).stdout.decode('UTF-8'))
        else:
            call_command(command)
    except CalledProcessError as err:
        if err.returncode != 0:
            if verbose:
                logger.debug(err)
                logger.debug(err.stdout)
                logger.debug(err.stderr)
            logger.error(f'{command.split()[0]} not found, check README in order to install')
        else:
            logger.error(err)
        exit(1)
