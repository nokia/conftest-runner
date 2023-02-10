from constraints import get_constraints, validate


class TestConstraints:
    def test_should_get_constraints_from_file(self):
        # given
        args = ArgsFromFileMock('test/charts/constraints-chart/templates/constraint.yaml')

        # when
        manifests = get_constraints(args)

        # then
        validate(manifests)

    def test_should_get_constraints_from_chart(self):
        # given
        args = ArgsFromChartMock('test/charts/constraints-chart')

        # when
        manifests = get_constraints(args)

        # then
        validate(manifests)


class ArgsFromFileMock:
    def __init__(self, policy_constraints_file):
        self.policy_constraints_file = policy_constraints_file


class ArgsFromChartMock:
    def __init__(self, chart_location):
        self.policy_constraints_file = ''
        self.helm_binary = 'helm'
        self.helm_options = ''
        self.policy_chart_constraints = chart_location
        self.policy_chart_constraints_values = None