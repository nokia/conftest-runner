import os
from os.path import isdir

from common.files import create_temp_dir, remove_dir, write_to_file, read_file_to_str


class TestFiles:
    def test_should_create_temp_dir_and_remove_it(self):
        # when
        dir_path = create_temp_dir(cleanup=False)

        # then
        assert isdir(dir_path)

        # when
        remove_dir(dir_path)

        # then
        assert not isdir(dir_path)

    def test_should_write_to_file_and_read_it(self):
        # given
        dir_path = create_temp_dir(cleanup=True)
        file_path = os.path.join(dir_path, 'test.txt')
        file_content = 'test'

        # when
        write_to_file(file_path, file_content)
        read_string = read_file_to_str(file_path)

        # then
        assert read_string == file_content
