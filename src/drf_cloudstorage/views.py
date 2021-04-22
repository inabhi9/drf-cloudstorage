from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from drf_cloudstorage.models import CloudFile
from drf_cloudstorage.serializers import CloudFileSerializer, CloudFileListSerializer, CloudFileURLSignedListSerializer


class CloudFileViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = CloudFile.objects.all()
    serializer_class = CloudFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        serializer = CloudFileURLSignedListSerializer(serializer.instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
