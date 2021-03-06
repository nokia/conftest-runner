# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from typing import Dict, Iterable

from admissionreviewrequest import AdmissionReviewRequest
from common.exceptions import InvalidManifestError
from common.helm import parse_manifests
from common.logger import Logger
from common.files import read_file_to_str

def validate(objects: Iterable[Dict]):
    for obj in objects:
        if (
                'apiVersion' not in obj
                or 'kind' not in obj
                or 'metadata' not in obj
                or 'name' not in obj['metadata']
                or type(obj['apiVersion']) != str
                or type(obj['kind']) != str
                or type(obj['metadata']) != dict
                or type(obj['metadata']['name']) != str
        ):
            raise InvalidManifestError('Encountered invalid obj: ' + str(obj))

def get_namespaces(args) -> Iterable[Dict]:
    logger = Logger.get_instance()

    if args.input_namespaces_file is None:
        logger.info(f'No input namespaces file passed, use {args.input_default_namespace} namespace with no labels.')
        return [{'apiVersion': 'v1', 'kind': 'Namespace', 'metadata': {'name': args.input_default_namespace, 'labels': {}}}]

    logger.debug('Read namespaces.')
    namespaces_str = read_file_to_str(args.input_namespaces_file)
    logger.debug('Parsing namespaces.')
    return parse_manifests(namespaces_str)

def convert_namespaces_to_admission_reviews(namespaces):
    logger = Logger.get_instance()

    logger.debug('Convert namespaces to admission reviews.')
    logger.debug(f'namespaces: {namespaces}')
    objects = tuple(namespaces)
    validate(objects)

    return tuple(AdmissionReviewRequest(obj) for obj in objects)