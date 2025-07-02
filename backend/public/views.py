from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from authentication.models import Reader
from user_profile.models import Collection, Rec
from rest_framework import viewsets, mixins, authentication
from public import serializers
from utils.mixins import ForbidListMixin
from rest_framework.decorators import action
from utils.serializers import RecSerializer
from django.db.models.query import QuerySet
from django.db.models import Q, Count

class PublicProfileViewSet(ForbidListMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Reader.objects.filter(user__is_active=True)
    serializer_class = serializers.PublicUserSerializer
    lookup_field = "user__username"

class PublicCollectionViewSet(ForbidListMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Collection.objects.filter(deleted=False, private=False, reader__user__is_active=True)
    serializer_class = serializers.PublicCollectionSerializer
    lookup_field = "uid"

    @action(methods=["GET"], detail=True, url_path="recs", serializer_class=RecSerializer)
    def get_recs(self, request, *args, **kwargs):
        recs = self.get_object().collection_recs.filter(deleted=False, collection__reader__user__is_active=True, collection__private=False, collection__deleted=False)
        query = request.query_params.get('query') or None
        if query:
            recs = recs.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(fandom__icontains=query) | Q(ship__icontains=query))
        page = self.paginate_queryset(recs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)


class SaveRecViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.PublicSavedSerializer
    queryset = Rec.objects.filter(deleted=False, collection__deleted=False, collection__private=False)
    lookup_field = "uid"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class QueryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [AllowAny]
    queryset = Collection.objects.filter(deleted=False, private=False, reader__user__is_active=True)
    serializer_class = serializers.QuerySerializer

    def list(self, request, format=None):

        query_search = request.query_params.get('query') or None
        query_type = request.query_params.get('type') or None
        tags = request.query_params.get('tags') or None

        if (not query_search or not query_type):
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        final_query = Q(**{"collection_recs__deleted": False})

        if tags:
            final_query = final_query.__and__(Q(**{"collection_recs__tags__icontains": tags.split(",")}))

        queryset = self.get_queryset()
        if query_type not in ["link", "ship"]:
            for query in query_search.split(","):
                key_string = f"collection_recs__{query_type}__icontains"
                new_query = dict()
                new_query[key_string] = query
                final_query = final_query.__and__(Q(**new_query))
        
        elif query_type == "ship":
            if len(query_search.split(",")) == 1:
                final_query = final_query.__and__(Q(**{"collection_recs__ship__icontains": query_search.replace(",", "")}))
            else:
                regex_search = query_search.replace(",", "|")
                regex = r"^.*(?P<ship>.*(" + regex_search + r").*/.*(" + regex_search + r").*).*$"
                final_query = final_query.__and__(Q(**{"collection_recs__ship__iregex": regex}))

        elif query_type == "link":
            final_query = final_query.__and__(Q(**{"collection_recs__link": query_search}))

        

        queryset = queryset.annotate(
                matching_recs=Count(
                'collection_recs',
                filter=final_query,
                distinct=True
                )
            ).filter(matching_recs__gt=0)
        
    
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        
        return Response(serializer.data, status=status.HTTP_200_OK)