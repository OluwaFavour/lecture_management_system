from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

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

    @extend_schema(
        summary="Get previous messages between a lecturer and a class rep",
        description="Get previous messages between a lecturer and a class rep",
        parameters=[
            OpenApiParameter(
                name="lecturer_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="The ID of the lecturer",
            ),
            OpenApiParameter(
                name="class_rep_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="The ID of the class rep",
            ),
        ],
        responses={200: PreviousMessagesSerializer},
    )
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
        recipient_id = lecturer_id if request.user.is_class_rep else class_rep_id

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
        description="Connect to the WebSocket at ws://<domain>/ws/chat/{other_user_id}/",
        parameters=[
            OpenApiParameter(
                name="other_user_id",
                description="The ID of the other user to chat with",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={101: OpenApiTypes.STR, 400: OpenApiTypes.STR},
        examples=[
            OpenApiExample(
                "Successful connection",
                value="Switching Protocols (Successful WebSocket connection)",
                status_codes=[101],
            ),
            OpenApiExample(
                "Failed connection",
                value="Bad Request (Invalid WebSocket connection)",
                status_codes=[400],
            ),
        ],
    )
    @action(detail=False, methods=["GET"])
    def websocket_info(self, request):
        return Response(
            {
                "detail": "This endpoint describes how to connect to the WebSocket for chat."
            }
        )
