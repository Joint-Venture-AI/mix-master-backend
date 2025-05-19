from rest_framework import serializers

from .models import User



class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        


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
            "cover_iamge",
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
            "status"
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
    
    
class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
