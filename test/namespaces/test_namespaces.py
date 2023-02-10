from admissionreviewrequest import AdmissionReviewRequest
from namespaces import get_namespaces, convert_namespaces_to_admission_reviews


class TestNamespaces:
    def test_should_get_namespaces_and_convert_to_admission_reviews(self):
        # given
        args = ArgsFromFileMock('test/namespaces/namespaces.yaml')

        # when
        namespaces = get_namespaces(args)

        # then
        assert isinstance(namespaces, tuple)
        assert len(namespaces) == 2
        for namespace in namespaces:
            assert isinstance(namespace, dict)
            assert 'kind' in namespace
            assert namespace['kind'] == 'Namespace'

        # when
        admission_reviews = convert_namespaces_to_admission_reviews(namespaces)

        # then
        assert isinstance(admission_reviews, tuple)
        assert len(admission_reviews) == 2
        for admission_review in admission_reviews:
            assert isinstance(admission_review, AdmissionReviewRequest)


class ArgsFromFileMock:
    def __init__(self, input_namespaces_file):
        self.input_namespaces_file = input_namespaces_file
