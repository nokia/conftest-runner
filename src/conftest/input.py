# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, Dict

from admissionreviewrequest import AdmissionReviewRequest


class Input(object):
    def __init__(self, review: AdmissionReviewRequest, parameters: dict):
        self.review = review
        self.parameters = parameters

    def as_dict(self) -> Dict[str, Any]:
        return {"review": self.review.as_dict(), "parameters": self.parameters}
