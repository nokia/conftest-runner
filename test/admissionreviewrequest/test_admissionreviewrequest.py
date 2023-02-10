from admissionreviewrequest import AdmissionReviewRequest


class TestAdmissionReviewRequest:
    def test_should_convert_to_dict(self):
        # given AdmissionReviewRequest
        admission_review_request = AdmissionReviewRequest({
            'apiVersion': 'group/v1',
            'kind': 'Pod',
            'metadata': {
                'name': 'test'}})

        # when
        dict_representation = admission_review_request.as_dict()

        # then
        assert isinstance(dict_representation, dict)

        assert 'uid' in dict_representation
        assert 'kind' in dict_representation
        assert 'resource' in dict_representation
        assert 'subResource' in dict_representation
        assert 'requestKind' in dict_representation
        assert 'requestResource' in dict_representation
        assert 'requestSubResource' in dict_representation
        assert 'name' in dict_representation
        assert 'namespace' in dict_representation
        assert 'operation' in dict_representation
        assert 'userInfo' in dict_representation
        assert 'object' in dict_representation
        assert 'oldObject' in dict_representation
        assert 'options' in dict_representation
        assert 'dryRun' in dict_representation

        assert dict_representation['kind']['group'] == admission_review_request.kind.group
        assert dict_representation['kind']['version'] == admission_review_request.kind.version
        assert dict_representation['kind']['kind'] == admission_review_request.kind.kind
        assert dict_representation['name'] == admission_review_request.name
