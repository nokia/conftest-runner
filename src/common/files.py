# Copyright 2021 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from atexit import register
from os import path
from shutil import rmtree
from tempfile import mkdtemp

from common.exceptions import FileError


def create_temp_dir(no_cleanup: bool) -> str:
    try:
        dir_path = mkdtemp()
    except OSError as e:
        raise FileError('Creating directory failed: ' + str(e))
    if not no_cleanup:
        register(remove_dir, dir_path)
    return dir_path


def remove_dir(dir_path: str):
    try:
        rmtree(dir_path)
    except OSError as e:
        raise FileError('Removing dir failed: ' + str(e))


def write_to_file(directory: str, file_name: str, content: str):
    try:
        with open(path.join(directory, file_name), 'w') as f:
            f.write(content)
    except IOError as e:
        raise FileError('Creating file failed: ' + str(e))

def read_file_to_str(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except OSError as e:
        raise FileError('Reading file failed: ' + str(e))