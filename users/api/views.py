from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.api.serializers import UserSerializer


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'register'


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_scope = 'login'


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    throttle_scope = 'refresh'
