from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from jossauth import models as joss_models
from utils import lifetime
from core.choices import StatusChoices
from .models import EmailVerification, User
from .serializers import (
    ChangePasswordSerializer,
    LoginUserSerializer,
    RequestPasswordResetOTPSerializer,
    ResendVerificationCodeSerializer,
    SetNewPasswordSerializer,
    UserSerializer,
    VerifyEmailSerializer,
    VerifyOTPSerializer,
)

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

    def perform_create(self, serializer):
        password = serializer.validated_data.pop("password", None)
        
        user = serializer.save()
        user.set_password(password)
        user.save()
        # EmailVerification.objects
        verification = EmailVerification.objects.create(user=user)
        send_mail(
            subject="Your verification code",
            message=f"Your verification code is: {verification.code}. It will expire in 5 minutes",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Email verified successfully."})


class ResendVerificationCodeView(generics.GenericAPIView):
    def post(self, request):
        serializer = ResendVerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Verification code resent."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetOTPView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"details": "OTP sent successfully to your email."},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "OTP verified successfully. You can now reset your password."},
            status=status.HTTP_200_OK,
        )


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):  # patch instead of put
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class RetrieveUpdateDestroyUserAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
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

        token_bearer = RefreshToken.for_user(user)
        access_token = str(token_bearer.access_token)
        refresh_token = str(token_bearer)
        response = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'access_token_remaining_days': lifetime.get_token_lifetime_remaining_days(access_token) if access_token else 0,
                'refresh_token_remaining_days': lifetime.get_token_lifetime_remaining_days(refresh_token) if refresh_token else 0,
            }
        return Response(response, status=status.HTTP_200_OK,)


class ChangeUserPasswordView(generics.UpdateAPIView):
    http_method_names = ["patch"]
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# MUMIT
# class LoginAPI(views.APIView):
    
#     def post(self, request: Request) -> Response:
#         email, password = request.data.get('email'), request.data.get('password')
#         authenticated, message = User.joss_auth(email, password)
#         if authenticated:
#             user = User.objects.get(email=email)
#             token = joss_models.JossToken.objects.create(user=user)
#             return Response(token.token_details, status=status.HTTP_200_OK)
#         return Response(dict(error=message), status=status.HTTP_401_UNAUTHORIZED)

class TokenRefreshAPI(views.APIView):
    
    def post(request: Request) -> Response:
        refresh_token = request.data.get('refreshToken')
        token_bearer = RefreshToken(refresh_token)
        access_token = str(token_bearer.access_token)
        refresh_token = str(token_bearer)
        response = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'access_token_remaining_days': lifetime.get_token_lifetime_remaining_days(access_token) if access_token else 0,
                'refresh_token_remaining_days': lifetime.get_token_lifetime_remaining_days(refresh_token) if refresh_token else 0,
            }
        return Response(response, status=status.HTTP_200_OK)
    

# class JossTest(views.APIView):
#     def get(self, request: Request) -> Response:
#         try:
#             from utils.operations import extract_auth_token
#             token = extract_auth_token(request)
#             from utils.lifetime import get_token_lifetime_remaining
#             remaining = get_token_lifetime_remaining(token)

#             return Response({'message': 'works', 'token': token, 'remaining_days': remaining}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'message': 'does not work', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# def joss_test(request):
#     from django.http import JsonResponse
#     print(request.headers)
#     from utils.operations import extract_auth_token
#     token = extract_auth_token(request)
#     return JsonResponse({'message': 'works', 'access_token': token}, status=200)