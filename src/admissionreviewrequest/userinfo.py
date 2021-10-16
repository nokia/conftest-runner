# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

class UserInfo(object):
    def __init__(self):
        # Username of the authenticated user making the request to the API server
        self.username = 'admin'

        # UID of the authenticated user making the request to the API server
        self.uid = '014fbff9a07c'

        # Group memberships of the authenticated user making the request to the API server
        self.groups = ['system:authenticated', 'my-admin-group']

        # Arbitrary extra info associated with the user making the request to the API server.
        # This is populated by the API server authentication layer and should be included
        # if any SubjectAccessReview checks are performed by the webhook.
        self.extra = {'some-key': ['some-value1', 'some-value2']}
