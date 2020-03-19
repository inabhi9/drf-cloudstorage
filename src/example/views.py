from rest_framework.viewsets import ModelViewSet

from example.models import Example
from example.serializers import ExampleSerializer


class ExampleViewSet(ModelViewSet):
    queryset = Example.objects.all()
    serializer_class = ExampleSerializer
