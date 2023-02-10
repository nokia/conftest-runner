from admissionreviewrequest.apiversion import parse_api_version, ApiVersion


class TestApiVersion:
    def test_should_parse_api_version_without_group(self):
        # given AdmissionReviewRequest
        version = 'v1'

        # when
        api_version = parse_api_version(version)

        # then
        assert isinstance(api_version, ApiVersion)

        assert api_version.group == ''
        assert api_version.version == version

    def test_should_parse_api_version_with_group(self):
        # given AdmissionReviewRequest
        group = 'test'
        version = 'v1'

        # when
        api_version = parse_api_version(f'{group}/{version}')

        # then
        assert isinstance(api_version, ApiVersion)

        assert api_version.group == group
        assert api_version.version == version
