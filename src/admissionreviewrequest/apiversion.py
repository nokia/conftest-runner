# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

class ApiVersion(object):
    def __init__(self, group: str, version: str):
        self.group = group
        self.version = version


class Kind(ApiVersion):
    def __init__(self, group: str, version: str, kind: str):
        super().__init__(group, version)
        self.kind = kind


class Resource(ApiVersion):
    def __init__(self, group: str, version: str, kind: str):
        super().__init__(group, version)
        self.resource = kind


def parse_api_version(api_version: str) -> ApiVersion:
    if '/' in api_version:
        return ApiVersion(*api_version.split('/', 1))

    return ApiVersion('', api_version)
