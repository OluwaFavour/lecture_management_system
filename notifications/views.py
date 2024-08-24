from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, extend_schema_view

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import serializers

from authentication.permissions import IsClassRep, IsStudent
from .models import Notification
from .serializers import NotificationSerializer


# Create your views here.
@extend_schema_view(
    list=extend_schema(
        summary="List all notifications. This action can only be performed by a student.",
        description="This endpoint returns all notifications that are related to the student's level.",
    ),
    retrieve=extend_schema(
        summary="Retrieve a notification. This action can only be performed by a student.",
        description="This endpoint returns a single notification that is related to the student's level.",
    ),
    create=extend_schema(
        summary="Create a notification. This action can only be performed by a class rep",
        description="This endpoint allows class reps to create notifications.",
    ),
    update=extend_schema(
        summary="Update a notification. This action can only be performed by a class rep",
        description="This endpoint allows class reps to update notifications.",
    ),
    partial_update=extend_schema(
        summary="Partial update a notification. This action can only be performed by a class rep",
        description="This endpoint allows class reps to partial update notifications.",
    ),
    destroy=extend_schema(
        summary="Delete a notification. This action can only be performed by a class rep",
        description="This endpoint allows class reps to delete notifications.",
    ),
    mark_as_read=extend_schema(
        summary="Mark a notification as read. This action can only be performed by a student.",
        description="This endpoint allows students to mark notifications as read.",
    ),
    is_read_by_student=extend_schema(
        summary="Check if a notification is read by a student. This action can only be performed by a student.",
        description="This endpoint allows students to check if a notification is read by them.",
    ),
)
@extend_schema(tags=["notifications"])
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsStudent]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsClassRep]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return NotificationSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(creator__level=request.user.level)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: OpenApiTypes.NONE},
        request=OpenApiTypes.NONE,
    )
    @action(detail=True, methods=["POST"])
    def mark_as_read(self, request, pk=None):
        notification: Notification = self.get_object()
        notification.mark_as_read(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: inline_serializer(
                name="IsReadByStudentResponse",
                fields={"is_read_by_student": serializers.BooleanField()},
            )
        }
    )
    @action(detail=True, methods=["GET"])
    def is_read_by_student(self, request, pk=None):
        notification: Notification = self.get_object()
        return Response(
            {"is_read_by_student": notification.is_read_by_student(request.user)},
            status=status.HTTP_200_OK,
        )
