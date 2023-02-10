from admissionreviewrequest import AdmissionReviewRequest
from common.helm import render_manifests, parse_manifests
from inputobjects import convert_kubernetes_objects_to_admission_reviews, get_kubernetes_objects


class TestInputobjects:
    def test_should_get_kubernetes_objects_from_file_and_convert_to_admission_reviews(self):
        # given
        args = ArgsFromFileMock('test/charts/constraint-templates-chart/templates/constraint-template.yaml')

        # when
        kubernetes_objects = tuple(get_kubernetes_objects(args))

        # then
        assert len(kubernetes_objects) == 1
        assert isinstance(kubernetes_objects[0], dict)
        assert 'kind' in kubernetes_objects[0]

        # when
        admission_reviews = convert_kubernetes_objects_to_admission_reviews(kubernetes_objects, 'test')

        # then
        assert isinstance(admission_reviews, tuple)
        assert len(admission_reviews) == 1
        assert isinstance(admission_reviews[0], AdmissionReviewRequest)

    def test_should_get_kubernetes_objects_from_chart_and_convert_to_admission_reviews(self):
        # given
        args = ArgsFromChartMock('test/charts/simple-chart')

        # when
        kubernetes_objects = tuple(get_kubernetes_objects(args))

        # then
        assert len(kubernetes_objects) == 4
        for kubernetes_object in kubernetes_objects:
            assert isinstance(kubernetes_object, dict)
            assert 'kind' in kubernetes_object

        # when
        admission_reviews = convert_kubernetes_objects_to_admission_reviews(kubernetes_objects, 'test')

        # then
        assert isinstance(admission_reviews, tuple)
        assert len(admission_reviews) == 4
        for admission_review in admission_reviews:
            assert isinstance(admission_review, AdmissionReviewRequest)


class ArgsFromFileMock:
    def __init__(self, input_kubernetes_objects):
        self.input_kubernetes_objects = input_kubernetes_objects


class ArgsFromChartMock:
    def __init__(self, chart_location):
        self.input_kubernetes_objects = None
        self.helm_binary = 'helm'
        self.helm_options = ''
        self.input_chart = chart_location
        self.input_chart_values = None
        self.input_chart_namespace = 'test_namespace'
        self.input_chart_release_name = 'test'
