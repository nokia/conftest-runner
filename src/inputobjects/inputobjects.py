# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from itertools import chain, product
from typing import Dict, Iterable

from common.helm import render_manifests, parse_manifests
from common.exceptions import InvalidManifestError
from common.logger import Logger
from common.files import read_file_to_str
from admissionreviewrequest import AdmissionReviewRequest

def convert_kubernetes_objects_to_admission_reviews(kubernetes_objects: dict, namespace: str) -> tuple:
    objects = tuple(kubernetes_objects)
    validate(objects)

    for obj in objects:
        if 'namespace' not in obj['metadata']:
            obj['metadata']['namespace'] = namespace

    return tuple(AdmissionReviewRequest(obj) for obj in objects)


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


def filter_matching_constraint(
    admission_reviews: Iterable[AdmissionReviewRequest],
    constraint_match_filter: dict,
    namespaces_labels: Iterable[AdmissionReviewRequest],
) -> Iterable[AdmissionReviewRequest]:

    if 'kinds' in constraint_match_filter:
        admission_reviews = tuple(filter_by_kinds(admission_reviews, constraint_match_filter['kinds']))
    if 'namespaces' in constraint_match_filter:
        admission_reviews = filter_by_namespaces(admission_reviews, constraint_match_filter['namespaces'])
    if 'excludedNamespaces' in constraint_match_filter:
        admission_reviews = filter_by_excluded_namespaces(
            admission_reviews, constraint_match_filter['excludedNamespaces']
        )
    if 'namespaceSelector' in constraint_match_filter:
        admission_reviews = filter_by_namespaces(
            admission_reviews,
            (
                admission_review.name
                for admission_review in filter_by_label_selector(
                    namespaces_labels, constraint_match_filter['namespaceSelector']
                )
            ),
        )
    if 'labelSelector' in constraint_match_filter:
        admission_reviews = filter_by_label_selector(admission_reviews, constraint_match_filter['labelSelector'])
    if 'scope' in constraint_match_filter:
        Logger.get_instance().warn('Scope filtering is not supported')

    return admission_reviews


def filter_by_kinds(
    admission_reviews: Iterable[AdmissionReviewRequest], kinds_filter: Iterable[Dict]
) -> Iterable[AdmissionReviewRequest]:

    kinds = set(
        chain.from_iterable(
            tuple(product(kind_specification['apiGroups'], kind_specification['kinds']))
            for kind_specification in kinds_filter
        )
    )

    return (obj for obj in admission_reviews if (obj.resource.group, obj.resource.resource) in kinds)


def filter_by_namespaces(
    objects: Iterable[AdmissionReviewRequest], namespaces: Iterable[str]
) -> Iterable[AdmissionReviewRequest]:
    return (obj for obj in objects if obj.namespace in namespaces)


def filter_by_excluded_namespaces(
    objects: Iterable[AdmissionReviewRequest], namespaces: Iterable[str]
) -> Iterable[AdmissionReviewRequest]:
    return (object for object in objects if object.namespace not in namespaces)


def filter_by_label_selector(
    objects: Iterable[AdmissionReviewRequest], selector: dict
) -> Iterable[AdmissionReviewRequest]:
    set_based_selector = ()
    if 'matchLabels' in selector:
        set_based_selector = (
            {'key': key, 'operator': 'In', 'values': (value,)} for key, value in selector['matchLabels'].iteritems()
        )
    elif 'matchExpressions' in selector:
        set_based_selector = selector['matchExpressions']

    for requirement in set_based_selector:
        if requirement['operator'] == 'Exists':
            objects = tuple(obj for obj in objects if exists_label_with_key(obj, requirement['key']))
        elif requirement['operator'] == 'In':
            objects = tuple(
                obj for obj in objects if label_has_value_from_list(obj, requirement['key'], requirement['values'])
            )
        elif requirement['operator'] == 'NotIn':
            objects = tuple(
                obj for obj in objects if not label_has_value_from_list(obj, requirement['key'], requirement['values'])
            )
    return objects


def exists_label_with_key(obj: AdmissionReviewRequest, key: str) -> bool:
    return 'labels' in obj.object['metadata'] and \
        obj.object['metadata']['labels'] is not None and \
        key in obj.object['metadata']['labels']


def label_has_value_from_list(obj: AdmissionReviewRequest, key: str, values: list) -> bool:
    return exists_label_with_key(obj, key) and obj.object['metadata']['labels'][key] in values

def get_kubernetes_objects(args) -> Iterable[Dict]:
    logger = Logger.get_instance()

    if args.input_kubernetes_objects:
        kubernetes_objects_str = read_file_to_str(args.input_kubernetes_objects)
    else:
        logger.debug('Rendering Kubernetes objects to test.')
        kubernetes_objects_str = render_manifests(
            args.helm_binary,
            args.input_chart,
            args.input_chart_values,
            args.input_chart_namespace,
            args.input_chart_release_name
        )
    logger.debug('Parsing objects to test.')
    return parse_manifests(kubernetes_objects_str)