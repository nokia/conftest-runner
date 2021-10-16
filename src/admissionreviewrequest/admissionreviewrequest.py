# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, Dict

from .apiversion import Kind, Resource, parse_api_version
from .options import Options
from .userinfo import UserInfo


class AdmissionReviewRequest(object):
    def __init__(self, obj: dict):
        api_version = parse_api_version(obj['apiVersion'])

        # Random uid uniquely identifying this admission call
        self.uid = ('705ab4f5-6393-11e8-b7cc-42010a800002',)

        # Fully-qualified group/version/kind of the incoming object
        self.kind = Kind(api_version.group, api_version.version, obj['kind'])

        # Fully-qualified group/version/kind of the resource being modified
        self.resource = Resource(api_version.group, api_version.version, obj['kind'])

        # subresource, if the request is to a subresource
        self.sub_resource = None

        # Fully-qualified group/version/kind of the incoming object in the original request to the API server.
        # This only differs from `kind` if the webhook specified `matchPolicy: Equivalent` and the
        # original request to the API server was converted to a version the webhook registered for.
        self.request_kind = self.kind

        # Fully-qualified group/version/kind of the resource being modified in the original request to the API server.
        # This only differs from `resource` if the webhook specified `matchPolicy: Equivalent` and the
        # original request to the API server was converted to a version the webhook registered for.
        self.request_resource = self.resource

        # subresource, if the request is to a subresource
        # This only differs from `subResource` if the webhook specified `matchPolicy: Equivalent` and the
        # original request to the API server was converted to a version the webhook registered for.
        self.request_sub_resource = self.sub_resource

        # Name of the resource being modified
        self.name = obj['metadata']['name']

        # Namespace of the resource being modified, if the resource is namespaced (or is a Namespace object)
        self.namespace = obj['metadata'].get('namespace', '')

        # operation can be CREATE, UPDATE, DELETE, or CONNECT
        self.operation = 'CREATE'

        self.user_info = UserInfo()

        # object is the new object being admitted.
        # It is null for DELETE operations.
        self.object = obj

        # oldObject is the existing object.
        # It is null for CREATE and CONNECT operations.
        self.oldObject = None

        # options contains the options for the operation being admitted, like meta.k8s.io/v1 CreateOptions, UpdateOptions, or DeleteOptions.
        # It is null for CONNECT operations.
        self.options = Options()

        # dryRun indicates the API request is running in dry run mode and will not be persisted.
        # Webhooks with side effects should avoid actuating those side effects when dryRun is true.
        # See http://k8s.io/docs/reference/using-api/api-concepts/#make-a-dry-run-request for more details.
        self.dryRun = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "kind": vars(self.kind),
            "resource": vars(self.resource),
            "subResource": self.sub_resource,
            "requestKind": vars(self.request_kind),
            "requestResource": vars(self.request_resource),
            "requestSubResource": self.request_sub_resource,
            "name": self.name,
            "namespace": self.namespace,
            "operation": self.operation,
            "userInfo": vars(self.user_info),
            "object": self.object,
            "oldObject": self.oldObject,
            "options": vars(self.options),
            "dryRun": self.dryRun,
        }

    def __repr__(self):
        return str(self.as_dict())