
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

class SessionAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that populates scope["user"] from Django session
    """
    async def __call__(self, scope, receive, send):
        # Get session key from cookies
        session_key = None
        headers = dict(scope.get('headers', []))
        if b'cookie' in headers:
            cookies = headers[b'cookie'].decode()
            for cookie in cookies.split('; '):
                if cookie.startswith('sessionid='):
                    session_key = cookie.split('=')[1]
                    break

        if session_key:
            scope['user'] = await self.get_user_from_session(session_key)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_session(self, session_key):
        try:
            session = Session.objects.get(session_key=session_key)
            user_id = session.get_decoded().get('_auth_user_id')
            User = get_user_model()
            return User.objects.get(id=user_id)
        except (Session.DoesNotExist, User.DoesNotExist):
            return AnonymousUser()