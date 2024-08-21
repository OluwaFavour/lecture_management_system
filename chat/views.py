from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Message
from .serializers import PreviousMessagesSerializer, PreviousMessages

# Create your views here.


@extend_schema(tags=["chat"])
class ChatViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "previous_messages":
            return PreviousMessagesSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "websocket_info":
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=["GET"],
        url_path="(?P<lecturer_id>\d+)/(?P<class_rep_id>\d+)/previous-messages",
    )
    def previous_messages(self, request, lecturer_id=None, class_rep_id=None):
        if lecturer_id == class_rep_id:
            return Response(
                {"error": "lecturer_id and class_rep_id cannot be the same"},
                status=400,
            )

        sender_id = request.user.id
        recipient_id = lecturer_id if request.user.is_classrep else class_rep_id

        if sender_id not in [lecturer_id, class_rep_id]:
            return Response(
                {"error": "Invalid lecturer_id or class_rep_id"},
                status=400,
            )

        if sender_id == recipient_id:
            return Response(
                {"error": "sender_id and recipient_id cannot be the same"},
                status=400,
            )

        sent_messages = Message.objects.filter(
            sender_id=sender_id, recipient_id=recipient_id
        )
        received_messages = Message.objects.filter(
            sender_id=recipient_id, recipient_id=sender_id
        )

        serializer = PreviousMessagesSerializer(
            PreviousMessages(sent_messages, received_messages)
        )
        return Response(serializer.data)

    @extend_schema(
        summary="WebSocket Chat Connection",
        description="Connect to the WebSocket at ws://<domain>/ws/chat/{lecturer_id}/{class_rep_id}/",
        parameters=[
            OpenApiParameter(
                name="lecturer_id",
                description="The ID of the lecturer",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="class_rep_id",
                description="The ID of the class rep",
                required=True,
                type=str,
            ),
        ],
        responses={
            "101": "Switching Protocols (Successful WebSocket connection)",
            "400": "Invalid room name or connection error",
        },
    )
    @action(detail=False, methods=["GET"])
    def websocket_info(self, request):
        return Response(
            {
                "detail": "This endpoint describes how to connect to the WebSocket for chat."
            }
        )
