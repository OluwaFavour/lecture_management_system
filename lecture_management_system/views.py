from drf_spectacular.utils import extend_schema, inline_serializer

from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


class APIRootView(GenericAPIView):
    @extend_schema(
        summary="API Root",
        description="The entry point for the API.",
        responses={
            200: inline_serializer(
                name="APIRootResponse",
                fields={
                    "schema": serializers.URLField(),
                    "swagger": serializers.URLField(),
                    "redoc": serializers.URLField(),
                },
            )
        },
        tags=["root"],
    )
    def get(self, request):
        return Response(
            {
                "schema": reverse("docs", request=request),
                "swagger": reverse("swagger-ui", request=request),
                "redoc": reverse("redoc", request=request),
            }
        )
