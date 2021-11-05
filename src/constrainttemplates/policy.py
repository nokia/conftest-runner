# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional
from common.files import create_temp_dir
from common.logger import Logger

class Policy(object):
    def __init__(self, namespace: Optional[str], policy: str):
        self.namespace = namespace
        self.policy = policy

def create_policies_dir(args) -> str:
    policies_dir = create_temp_dir(not args.no_cleanup)
    Logger.get_instance().debug('Created policies directory: ' + policies_dir)
    return policies_dir