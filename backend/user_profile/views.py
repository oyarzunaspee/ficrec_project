from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from user_profile.models import Collection, Rec
from django.db.models.query import QuerySet
from rest_framework.decorators import action
from public.models import Saved
from authentication.models import Reader
from rest_framework import mixins, viewsets
from user_profile import serializers
from utils.mixins import CustomDestroyMixin
from utils.serializers import RecSerializer


class ProfileViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.ReaderSerializer
    queryset = Reader.objects.filter(user__is_active=True)

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_object(self):
        reader = self.get_queryset().get(user=self.request.user.pk)
        return reader
    
    def list(self, request, format=None):
        if not request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(self.request.user.user_reader)
        return Response(serializer.data)

    @action(["patch"], detail=False, url_path="update")
    def toggle_field(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user.user_reader, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(["get"], detail=False, url_path="bookmarks", serializer_class=serializers.SavedListSerializer)
    def get_bookmarks(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user.user_reader, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class CollectionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, CustomDestroyMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.CollectionSerializer
    queryset = Collection.objects.filter(deleted=False)
    lookup_field = "uid"

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(reader__user=self.request.user)
        return queryset

    
    @action(methods=["GET"], detail=True, url_path="recs", serializer_class=RecSerializer)
    def get_recs(self, request, *args, **kwargs):
        recs = self.get_object().collection_recs.filter(deleted=False, collection__reader__user__is_active=True, collection__deleted=False)
        query = request.query_params.get('query') or None
        if query:
            recs = recs.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(fandom__icontains=query) | Q(ship__icontains=query))
        page = self.paginate_queryset(recs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @action(["patch"], detail=True, url_path="toggle", serializer_class=serializers.ToggleSerializer)
    def toggle_field(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(["post"], detail=True, url_path="add/rec", serializer_class=serializers.PrepareRecSerializer)
    def add_rec(self, request, uid=None, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rec_serializer = serializer.save()
        return Response(rec_serializer.data, status=status.HTTP_201_CREATED)
    

class RecViewSet(viewsets.GenericViewSet, CustomDestroyMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Rec.objects.filter(deleted=False, collection__deleted=False, collection__reader__user__is_active=True)
    serializer_class = serializers.EditRecSerializer
    lookup_field = "uid"

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            col_uid = self.kwargs["collection_uid"]
            queryset = queryset.filter(collection__reader__user=self.request.user, collection__uid=col_uid)
        return queryset
    
 
class SavedViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, CustomDestroyMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Saved.objects.filter(deleted=False, rec__deleted=False, rec__collection__deleted=False, rec__collection__private=False, rec__collection__reader__user__is_active=True)
    serializer_class = serializers.SavedSerializer
    lookup_field = "uid"

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(saved_by__user=self.request.user)
        return queryset

    @action(["patch"], detail=True, url_path="toggle")
    def mark_as_read(self, request, uid=None):
        queryset = self.get_queryset()
        return Response(status=status.HTTP_204_NO_CONTENT)