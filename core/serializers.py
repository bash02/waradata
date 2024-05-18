from .models import User, generate_referral_code
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer, TokenCreateSerializer as BaseTokenCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .backends import MultiFieldModelBackend

User = get_user_model

class UserCreateSerializer(BaseUserCreateSerializer):
    id = serializers.UUIDField(read_only=True)
    referral_or_promo_code = serializers.CharField(max_length=8, required=False)

    class Meta(BaseUserCreateSerializer.Meta):
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'gender', 'phone', 'address', 'birth_date', 'image', 'password', 'referral_or_promo_code']


class UserSerializer(BaseUserSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'image', 'role', 'balance', 'bonuce']




class TokenCreateSerializer(BaseTokenCreateSerializer):
    def validate(self, attrs):
        # Extract login fields from request data
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        # Check authentication using multiple fields
        user = MultiFieldModelBackend().authenticate(
            request=self.context.get("request"),
            username=username or email,
            password=password,
        )
        if user and user.is_active:
            return attrs
        self.fail("invalid_credentials")        