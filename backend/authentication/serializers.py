from authentication.models import Reader
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from typing import Any
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        attrs["username"] = attrs["username"].lower()
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["token"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data, str(refresh)
    

class CustomTokenRefreshSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        refresh = self.token_class(self.context)

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)
        if user_id and (
            user := get_user_model().objects.get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        ):
            if not api_settings.USER_AUTHENTICATION_RULE(user):
                raise AuthenticationFailed(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                )

        data = {"token": str(refresh.access_token)}

        return data


    

class ReactivateSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=4, trim_whitespace=True)
    password = serializers.CharField(required=True, write_only=True, min_length=6)

    def save(self):
        try:
            user = User._default_manager.get_by_natural_key(self.validated_data["username"])
        except User.DoesNotExist:
            return serializers.ValidationError("User does not exist")
        check_password = user.check_password(self.validated_data["password"])
        if check_password:
            user.is_active = True
            user.save()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True, min_length=6)
    password_check = serializers.CharField(required=True, write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ["username", "password", "password_check"]

    def validate(self, data):
        if data["password"] != data["password_check"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def save(self):
        new_user = User.objects.create(
            username = self.validated_data["username"].lower(),
            password = self.validated_data["password"]
        )
        new_user.set_password(self.validated_data["password"])
        new_user.save()
        Reader.objects.create(user = new_user)

class ResetPasswordSerializer(RegisterSerializer):
    def save(self):
        user = self.context["view"].get_object()
        user.set_password(self.validated_data["password"])
        user.save()

class ResetUsernameSerializer(serializers.Serializer):
    new_username = serializers.CharField(min_length=4, trim_whitespace=True)

    def validate(self, data):
        if User.objects.filter(username=data["new_username"].lower()):
            raise serializers.ValidationError("Username already taken")
        return data
    
    def save(self):
        user = self.context["view"].get_object()
        user.username = self.validated_data["new_username"].lower()
        user.save()