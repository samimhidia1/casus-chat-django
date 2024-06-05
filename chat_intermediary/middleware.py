import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
                logging.info(f"Decoded token: {decoded_token}")
                user_id = decoded_token.get('user_id')
                try:
                    user = User.objects.get(id=user_id)
                    request.user = user
                except User.DoesNotExist:
                    logging.error(f"User with id {user_id} does not exist.")
                    request.user = None
            except (InvalidToken, TokenError, jwt.DecodeError) as e:
                logging.error(f"Token decoding error: {e}")
                request.user = None
        else:
            request.user = None
