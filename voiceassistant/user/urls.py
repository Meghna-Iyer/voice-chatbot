from django.urls import path

from .views import UserListView, UserUpdateView, UserRegisterView, CustomTokenObtainPairView, CustomTokenRefreshView


app_name = 'user'

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token-obtain'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('info/', UserListView.as_view(), name='user'),
    path('update/', UserUpdateView.as_view(), name='user-update'),
]