from os import path

from yaml import load_all, SafeLoader

from admissionreviewrequest import AdmissionReviewRequest
from common.files import create_temp_dir
from conftest.conftest import extract_summary, run_conftest
from constrainttemplates.policy import Policy


class TestSummary:
    def test_should_extract_empty_summary(self):
        # given
        result = ResultMock('')
        output_format = 'stdout'

        # when
        summary = extract_summary(result, output_format)

        # then
        expected_summary = {
            'tests': 0,
            'passed': 0,
            'warnings': 0,
            'failures': 0,
            'exceptions': 0
        }
        TestSummary.check_summary(summary, expected_summary)

    def test_should_extract_stdout_summary(self):
        # given
        with open('test/conftest/summary.txt') as f:
            result = ResultMock(f.read())

        output_format = 'stdout'

        # when
        summary = extract_summary(result, output_format)

        # then
        expected_summary = {
            'tests': 5,
            'passed': 1,
            'warnings': 0,
            'failures': 4,
            'exceptions': 0
        }
        TestSummary.check_summary(summary, expected_summary)

    def test_should_extract_json_summary(self):
        # given
        with open('test/conftest/summary.json') as f:
            result = ResultMock(f.read())

        output_format = 'json'

        # when
        summary = extract_summary(result, output_format)

        # then
        expected_summary = {
            'tests': 5,
            'passed': 1,
            'warnings': 0,
            'failures': 4,
            'exceptions': 0
        }
        TestSummary.check_summary(summary, expected_summary)

    def test_should_extract_tap_summary(self):
        # given
        with open('test/conftest/summary.tap') as f:
            result = ResultMock(f.read())

        output_format = 'tap'

        # when
        summary = extract_summary(result, output_format)

        # then
        expected_summary = {
            'tests': 5,
            'passed': 1,
            'warnings': 0,
            'failures': 4,
            'exceptions': 0
        }
        TestSummary.check_summary(summary, expected_summary)

    def test_should_extract_table_summary(self):
        # given
        with open('test/conftest/summary.table') as f:
            result = ResultMock(f.read())

        output_format = 'table'

        # when
        summary = extract_summary(result, output_format)

        # then
        expected_summary = {
            'tests': 5,
            'passed': 4,
            'warnings': 1,
            'failures': 0,
            'exceptions': 0
        }
        TestSummary.check_summary(summary, expected_summary)

    def test_should_extract_junit_summary(self):
        # given
        with open('test/conftest/summary.xml') as f:
            result = ResultMock(f.read())

        output_format = 'junit'

        # when
        summary = extract_summary(result, output_format)

        # then
        expected_summary = {
            'tests': 5,
            'passed': 1,
            'warnings': 0,
            'failures': 4,
            'exceptions': 0
        }
        TestSummary.check_summary(summary, expected_summary)

    def test_should_extract_github_summary(self):
        # given
        with open('test/conftest/summary.github') as f:
            result = ResultMock(f.read())

        output_format = 'github'

        # when
        summary = extract_summary(result, output_format)

        # then
        expected_summary = {
            'tests': 5,
            'passed': 1,
            'warnings': 0,
            'failures': 4,
            'exceptions': 0
        }
        TestSummary.check_summary(summary, expected_summary)

    @staticmethod
    def check_summary(summary, expected_summary):
        assert isinstance(summary, dict)
        assert len(summary) == len(expected_summary)

        for key, value in expected_summary.items():
            assert key in summary
            assert summary[key] == expected_summary[key]


class ResultMock:
    def __init__(self, stdout):
        self.stdout = stdout


class TestConftest:
    def test_should_run_conftest(self):
        # given
        policies_dir = 'test/policy'
        policies = {'K8sRequiredLabels': Policy('k8srequiredlabels', '')}

        with open('test/charts/constraints-chart/templates/constraint.yaml') as f:
            constraints = load_all(f.read(), Loader=SafeLoader)

        with open('test/namespaces/namespaces.yaml') as f:
            admission_review_namespaces = tuple(
                AdmissionReviewRequest(namespace) for namespace in load_all(f.read(), Loader=SafeLoader))

        admission_review_requests = admission_review_namespaces
        output_format = 'json'

        output_file = path.join(create_temp_dir(cleanup=False), 'result.json')
        warning_mode = False
        fail_fast = False

        # when
        run_conftest(
            policies_dir,
            policies,
            constraints,
            admission_review_namespaces,
            admission_review_requests,
            output_format,
            output_file,
            warning_mode,
            fail_fast)

        # then
        with open(output_file) as f:
            output = tuple(result for result in load_all(f.read().replace('\t', ''), Loader=SafeLoader))

        assert len(output) == 1
        output_first_item = output[0][0]

        assert 'successes' in output_first_item
        assert 'failures' in output_first_item

        assert output_first_item['successes'] == 1
        assert len(output_first_item['failures']) == 1
