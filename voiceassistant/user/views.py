from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, UserUpdateSerializer, RegisterSerializer


class UserRegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [JSONParser] 


class UserListView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateSerializer
    parser_classes = [JSONParser] 

    def get_object(self):
        return self.request.user
    

class CustomTokenObtainPairView(TokenObtainPairView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response

    
class CustomTokenRefreshView(TokenRefreshView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response