from common.helm import render_manifests, parse_manifests


class TestHelm:
    def test_render_manifests_with_defaults(self):
        # given
        helm_binary = 'helm'
        helm_options = ''
        chart_location = 'test/charts/simple-chart'

        # when
        manifests = render_manifests(helm_binary, helm_options, chart_location)

        # then
        with open('test/common/expected_manifests_default.yaml') as f:
            expected_manifests = f.read()

        assert manifests == expected_manifests

    def test_render_manifests_with_values(self):
        # given
        helm_binary = 'helm'
        helm_options = ''
        chart_location = 'test/charts/simple-chart'
        values_location = 'test/common/values.yaml'

        # when
        manifests = render_manifests(helm_binary, helm_options, chart_location, values_yaml_location=values_location)

        # then
        with open('test/common/expected_manifests_with_values.yaml') as f:
            expected_manifests = f.read()

        assert manifests == expected_manifests

    def test_parse_manifests(self):
        # given
        with open('test/common/expected_manifests_default.yaml') as f:
            manifests_as_yaml = f.read()

        # when
        manifests_as_dicts = parse_manifests(manifests_as_yaml)

        # then
        assert manifests_as_dicts is not None
        assert len(manifests_as_dicts) == 4
        for manifest in manifests_as_dicts:
            assert 'kind' in manifest
