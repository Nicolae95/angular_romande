from channels_api.bindings import ResourceBinding

from company.models import Question
from company.serializers import QuestionSerializer


class LogBinding(ResourceBinding):

    model = ClientLog
    stream = "logs"
    serializer_class = ClientLogSerializer
    queryset = ClientLog.objects.all()

    @detail_action()
    def publish(self, pk, data=None, **kwargs):
        instance = self.get_object(pk)
        result = instance.publish()
        return result, 200

    @list_action()
    def report(self, data=None, **kwargs):
        report = self.get_queryset()
        return report, 200
