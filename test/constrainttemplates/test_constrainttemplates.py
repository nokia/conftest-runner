from os import path
from os.path import isfile

from common.files import create_temp_dir
from constrainttemplates import get_constraint_templates, validate, generate_policies


class TestConstraints:
    def test_should_get_constraint_templates_from_file_and_extract_policies(self):
        # given
        args = ArgsFromFileMock('test/charts/constraint-templates-chart/templates/constraint-template.yaml')
        output_dir = create_temp_dir(cleanup=True)
        output_file = path.join(output_dir, 'k8srequiredlabels.rego')

        # when
        manifests = get_constraint_templates(args)

        # then
        validate(manifests)

        # when
        policies = generate_policies(manifests, output_dir)

        # then
        TestConstraints.verify_policies(policies)
        TestConstraints.verify_output_file(output_file)

    def test_should_get_constraint_templates_from_chart_and_extract_policies(self):
        # given
        args = ArgsFromChartMock('test/charts/constraint-templates-chart')
        output_dir = create_temp_dir(cleanup=True)
        output_file = path.join(output_dir, 'k8srequiredlabels.rego')

        # when
        manifests = get_constraint_templates(args) 

        # then
        validate(manifests)

        # when
        policies = generate_policies(manifests, output_dir)

        # then
        TestConstraints.verify_policies(policies)
        TestConstraints.verify_output_file(output_file)

    @staticmethod
    def verify_policies(policies):
        assert isinstance(policies, dict)
        assert len(policies) == 1
        assert 'K8sRequiredLabels' in policies

    @staticmethod
    def verify_output_file(output_file):
        assert isfile(output_file)
        with open(output_file) as f:
            output_file_content = f.read()
        assert not output_file_content == ''

        with open('test/policy/k8srequiredlabels.rego') as f:
            expected_output_file_content = f.read()

        assert output_file_content == expected_output_file_content


class ArgsFromFileMock:
    def __init__(self, policy_constraint_templates_file):
        self.policy_constraint_templates_file = policy_constraint_templates_file


class ArgsFromChartMock:
    def __init__(self, chart_location):
        self.policy_constraint_templates_file = ''
        self.helm_binary = 'helm'
        self.helm_options = ''
        self.policy_chart_constraint_templates = chart_location
        self.policy_chart_constraint_templates_values = None
