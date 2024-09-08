from channels.db import database_sync_to_async

from django.contrib.auth.models import AnonymousUser

from authentication.models import Session


@database_sync_to_async
def get_session_user(session_token):
    try:
        session = Session.objects.get(token=session_token, is_current=True)
        user = session.user
    except Session.DoesNotExist:
        return AnonymousUser()
    return user


class SessionAuthMiddleware:
    """
    Custom middleware (session auth) to authenticate the user using the session key.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Get the session token from the scope
        session_token = str(scope["query_string"].split(b"session_token=")[1], "utf-8")

        if not session_token:
            scope["user"] = AnonymousUser()
            return await self.app(scope, receive, send)

        # Get the user from the session
        user = await get_session_user(session_token)

        # Add the user to the scope
        scope["user"] = user

        # Pass control to the inner application
        return await self.app(scope, receive, send)
