import pytest

from common.cmd import call_command, exit_if_command_not_found


class TestCmd:
    def test_should_call_command(self):
        # given
        stdin = b'test'
        command = 'echo ' + stdin.decode()

        # when
        completed_process = call_command(command)

        # then
        assert completed_process.returncode == 0
        assert completed_process.stdout.strip() == stdin
        assert completed_process.stderr == b''

    def test_should_not_exit_if_command_found(self):
        # given
        command = 'echo'

        # when
        exit_if_command_not_found(command, verbose=False)

    def test_should_exit_if_command_found(self):
        # given
        command = 'unknown'

        # when
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            exit_if_command_not_found(command, verbose=False)

        # then
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
