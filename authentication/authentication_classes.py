from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Session

User = get_user_model()


class SessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get session details from the request session
        session_token = request.session.get("session_token")
        user_id = request.session.get("user_id")

        if not session_token or not user_id:
            return None

        try:
            session = Session.objects.get(
                token=session_token, user_id=user_id, is_current=True
            )
            user = session.user
        except Session.DoesNotExist:
            raise AuthenticationFailed("Invalid session or expired session.")

        return (user, None)

    def authenticate_header(self, request):
        return "Session"
