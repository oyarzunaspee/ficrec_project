from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from authentication import serializers

from rest_framework import viewsets, mixins, generics
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class AuthView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.RegisterSerializer

class CustomTokenObtainView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e
        
        token, refresh = serializer.validated_data
        response = Response(token, status=status.HTTP_200_OK)
        response.set_cookie(
            "ficrecfresher",
            refresh,
            httponly=True,
            samesite="None",
            secure=True,
            max_age=60 * 60 * 24 * 7
        )
        return response

class CustomTokenRefreshView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.CustomTokenRefreshSerializer

    def get(self, request, *args, **kwargs):
        refresh = request.COOKIES.get("ficrecfresher")
        if not refresh:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.CustomTokenRefreshSerializer(data=dict(), context=refresh)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]
    serializer_class = serializers.CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(
            "ficrecfresher",
            "",
            httponly=True,
            samesite="None",
            secure=True,
            max_age=60 * 60 * 24 * 7
        )
        return response

class ReactivateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [BasicAuthentication]
    serializer_class = serializers.ReactivateSerializer
    

class AuthUserViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes      = [IsAuthenticated]
    authentication_classes  = [JWTAuthentication]
    serializer_class = serializers.RegisterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(pk=self.request.user.pk)
        return queryset
    
    def get_object(self):
        return self.request.user
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    @action(["post"], detail=False, url_path="password", serializer_class=serializers.ResetPasswordSerializer)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(["post"], detail=False, url_path="verify", serializer_class=serializers.ResetPasswordSerializer)
    def verify_password(self, request, *args, **kwargs):
        if not request.user.check_password(request.data["password"]):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(["post"], detail=False, url_path="username", serializer_class=serializers.ResetUsernameSerializer)
    def change_username(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)