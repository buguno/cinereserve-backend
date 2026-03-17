from rest_framework.generics import CreateAPIView

from users.api.serializers import UserSerializer


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []
