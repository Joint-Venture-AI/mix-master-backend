from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from core.choices import StatusChoices
from .models import User
from .serializers import LoginUserSerializer, UserSerializer

# Create your views here.


class ListCreateUserAPIView(generics.ListCreateAPIView):
    queryset = User.objects.IS_ACTIVE().order_by("id")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsAdminUser]

        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]


class RetrieveUpdateDestroyUserAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user
    
    def perform_destroy(self, instance):
        instance.status = StatusChoices.REMOVED
        instance.save()
        
        

class LoginUserView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refreshToken": str(refresh),
                "accessToken": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

