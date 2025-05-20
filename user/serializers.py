import random

from django.core.mail import send_mail
from django.conf import settings

from rest_framework import serializers

from .models import User, EmailVerification, PasswordResetOtp


# class RegisterUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "uid",
            "email",
            "name",
            "password",
            "nickname",
            "phone",
            "profile_image",
            "cover_image",
            "bio",
            "dob",
            "gender",
            "country",
            "city",
            "address",
            "postal_code",
            "is_subscribed",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "uid",
            "is_active",
            "created_at",
            "updated_at",
            "status",
        ]

    def validate_email(self, value):
        """Check that the email is unique."""
        # If this is an update (instance exists), allow same email
        if self.instance:
            if self.instance.email == value:
                return value

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
            verification = EmailVerification.objects.filter(
                user=user, code=data["code"]
            ).latest("created_at")
        except (User.DoesNotExist, EmailVerification.DoesNotExist):
            raise serializers.ValidationError("Invalid email or code.")

        if verification.is_expired():
            verification.delete()
            raise serializers.ValidationError("The verification code has expired.")

        user.is_active = True
        user.save()
        verification.delete()  # Optional cleanup
        return data


class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email.")
        return value

    def save(self, **kwargs):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        # Get or create verification record
        verification, created = EmailVerification.objects.get_or_create(user=user)

        # Regenerate code
        verification.code = str(random.randint(1000, 9999))
        verification.save()

        # Send email
        send_mail(
            subject="Your verification code",
            message=f"Your new verification code is: {verification.code}. It will expire in 5 minutes",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return verification


class RequestPasswordResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, instance):
        if not User.objects.filter(email=instance).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return instance

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        otp_entry = PasswordResetOtp.objects.create(user=user)
        otp = otp_entry.otp

        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP for password reset is {otp}. It will expire in 5 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return otp


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")
        try:
            user = User.objects.get(email=email)
            otp_entry = PasswordResetOtp.objects.get(
                user=user, otp=otp, is_verified=False, is_used=False
            )
        except (User.DoesNotExist, PasswordResetOtp.DoesNotExist):
            raise serializers.ValidationError("Invalid OTP or Email")

        if otp_entry.is_expired:
            raise serializers.ValidationError("OTP has expired.")

        attrs["user"] = user
        attrs["otp_entry"] = otp_entry

        return attrs

    def save(self):
        otp_entry = self.validated_data["otp_entry"]
        otp_entry.is_verified = True
        otp_entry.save()
        return otp_entry


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            user = User.objects.get(email=email)
            otp_entry = PasswordResetOtp.objects.filter(
                user=user, is_verified=True, is_used=False
            ).latest("created_at")
        except (User.DoesNotExist, PasswordResetOtp.DoesNotExist):
            raise serializers.ValidationError(
                "OTP verification not completed for this user."
            )

        if otp_entry.is_expired:
            raise serializers.ValidationError("OTP has expired. Request a new OTP")
        attrs["user"] = user
        attrs["otp_entry"] = otp_entry
        return attrs

    def save(self):
        user = self.validated_data["user"]
        otp_entry = self.validated_data["otp_entry"]
        user.set_password(self.validated_data["new_password"])
        user.save()

        otp_entry.is_used = True
        otp_entry.save()


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    new_password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["old_password", "new_password", "new_password2"]

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data["old_password"]):
            raise serializers.ValidationError("Password is incorrect")
        if validated_data["new_password"] != validated_data["new_password2"]:
            raise serializers.ValidationError("Passwords do not match")
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance
