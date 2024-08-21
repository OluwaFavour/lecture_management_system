from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import SessionAuthentication


class CustomSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "authentication.authentication_classes.SessionAuthentication"  # full import path OR class ref
    name = "SessionAuthentication"  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "session_token",
        }
