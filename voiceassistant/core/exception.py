from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError, AuthenticationFailed

def custom_exception_handler(exc, context):
    if isinstance(exc, (TokenError, InvalidToken, TokenBackendError, AuthenticationFailed)):
        response_data = {
            'detail': 'Token is invalid or has expired.',
            'code': 'token_invalid',
        }
        return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

    response = exception_handler(exc, context)

    return response
