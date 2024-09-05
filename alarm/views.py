from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from alarm.models import AlertSettings
from authentication.permissions import IsStudent
from .serializers import AlertSerializer, AlertSettingsSerializer, Alert

# Create your views here.


@extend_schema_view(
    create=extend_schema(
        summary="Create an alert for logged in student",
        description="Create an alert for logged in student",
    ),
    list=extend_schema(
        summary="List all alerts of logged in student",
        description="List all alerts of logged in student",
    ),
    destroy=extend_schema(
        summary="Delete an alert of logged in student",
        description="Delete an alert of logged in student",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Alert ID",
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve an alert of logged in student",
        description="Retrieve an alert of logged in student",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Alert ID",
            )
        ],
    ),
    activate=extend_schema(
        summary="Activate an alert of logged in student",
        description="Activate an alert of logged in student",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Alert ID",
            )
        ],
    ),
    deactivate=extend_schema(
        summary="Deactivate an alert of logged in student",
        description="Deactivate an alert of logged in student",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Alert ID",
            )
        ],
    ),
    update=extend_schema(
        summary="Update an alert of logged in student",
        description="Update an alert of logged in student",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Alert ID",
            )
        ],
    ),
    partial_update=extend_schema(
        summary="Partially update an alert of logged in student",
        description="Partially update an alert of logged in student",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Alert ID",
            )
        ],
    ),
)
@extend_schema(tags=["Alerts"])
class AlertViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsStudent]
    serializer_class = AlertSerializer

    def get_queryset(self):
        super().get_queryset()
        return self.request.user.alerts.all()

    def perform_create(self, serializer):
        alert = serializer.save()
        alert.students.add(self.request.user)

    def perform_destroy(self, instance):
        instance.students.remove(self.request.user)
        if not instance.students.exists():
            instance.delete()

    @action(detail=True, methods=["POST"])
    def activate(self, request, pk=None):
        alert: Alert = self.get_object()
        alert.activate()
        return Response(AlertSerializer(alert).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def deactivate(self, request, pk=None):
        alert: Alert = self.get_object()
        alert.deactivate()
        return Response(AlertSerializer(alert).data, status=status.HTTP_200_OK)


@extend_schema_view(
    get_settings=extend_schema(
        summary="Retrieve alert settings of logged in student",
        description="Retrieve alert settings of logged in student",
    ),
    update_settings=extend_schema(
        summary="Update alert settings of logged in student",
        description="Update alert settings of logged in student",
    ),
)
@extend_schema(tags=["Alert Settings"])
class AlertSettingsViewSet(viewsets.GenericViewSet):
    permission_classes = [IsStudent]
    serializer_class = AlertSettingsSerializer

    def get_queryset(self):
        return AlertSettings.objects.filter(student=self.request.user)

    def get_object(self):
        return self.get_queryset().first()

    @action(detail=False, methods=["GET"])
    def get_settings(self, request):
        alert_settings = self.get_object()
        return Response(
            AlertSettingsSerializer(alert_settings).data, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["PUT"])
    def update_settings(self, request):
        alert_settings = self.get_object()
        serializer = self.get_serializer(alert_settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
