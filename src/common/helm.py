# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from subprocess import CalledProcessError
from typing import Dict, Iterable
from yaml import load_all, FullLoader

from .cmd import call_command, log_called_process_output
from .exceptions import TemplateError
from .logger import Logger


def render_manifests(helm_binary: str, chart_location: str, values_yaml_location='', namespace='',
                     release_name='') -> str:
    logger = Logger.get_instance()

    command = f'{helm_binary} template {release_name} {chart_location}'
    if values_yaml_location:
        command += ' -f ' + values_yaml_location
    if namespace:
        command += ' -n ' + namespace
    logger.debug(command)

    try:
        process_result = call_command(command)
        return process_result.stdout.decode() if process_result.stdout else ''
    except CalledProcessError as e:
        log_called_process_output(Logger.get_instance().error, e)
        raise TemplateError('Rendering chart failed.')


def parse_manifests(manifests: str) -> Iterable[Dict]:
    manifests = tuple(
        manifest
        for manifest in load_all(manifests, Loader=FullLoader)
        if manifest is not None
    )
    validate(manifests)

    return manifests


def validate(manifests: Iterable[Dict]):
    for manifest in manifests:
        if type(manifest) != dict:
            raise TemplateError('Encountered manifest that does not represent yaml dict: ' + str(manifest))
