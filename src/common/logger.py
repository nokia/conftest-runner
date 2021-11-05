# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from logging import getLogger, StreamHandler, INFO, Formatter, FileHandler
from sys import stdout


class Logger():
    _instance = None
    _handler = None

    @staticmethod
    def get_instance():
        if Logger._instance is None:
            Logger()
        return Logger._instance

    def __init__(self, output_file=None):
        if Logger._instance is not None:
            raise Exception('This class is a singleton!')
        else:
            if output_file:
                Logger._handler = FileHandler(filename=output_file, mode='a', encoding='utf-8')
            else:
                Logger._handler = StreamHandler(stdout)

            Logger._handler.setLevel(INFO)
            Logger._handler.setFormatter(Formatter('%(levelname)s - %(message)s'))
            logger = getLogger('conftest')
            logger.setLevel(INFO)
            logger.addHandler(Logger._handler)

            Logger._instance = logger

def set_log_level(level):
    Logger.get_instance().setLevel(level)
    for handler in Logger.get_instance().handlers:
        handler.setLevel(level)

def info_passed(logger, formatted_output):
    logger.info("\x1b[32mPASSED " + formatted_output + "\033[0m")

def info_failed(logger, formatted_output):
    logger.info("\x1b[31mFAILURE " + formatted_output + "\033[0m")
