from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
import time
from rest_framework.authentication import get_authorization_header
from .models import User

class CookieAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None
        
        payload = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=getattr(settings, 'JWT_ALGORITHM'))

        expire = payload.get('exp')

        if expire < time.time():
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('No such user')
        
        return (user, None)

class AllowAnyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return (None, None)