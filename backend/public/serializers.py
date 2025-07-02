from authentication.models import Reader
from user_profile.models import Collection
from public.models import Saved
from rest_framework import serializers
from utils import fields
from utils import serializers as util_serializers
from rest_framework.validators import UniqueTogetherValidator

class PublicUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    collections = fields.NestedListField(
        child = util_serializers.PublicCollectionSerializer,
        source = "reader_collection",
        read_only = True,
        filter = dict(deleted=False, private=False, reader__user__is_active=True)
    )
    class Meta:
        model = Reader
        fields = ["username", "avatar", "bio", "collections", "highlight"]

class CollectionUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    class Meta:
        model = Reader
        exclude = ["id", "user", "uid"]

class PublicCollectionSerializer(serializers.ModelSerializer):
    # recs = fields.NestedListField(
    #     child = util_serializers.RecSerializer,
    #     source = "collection_recs",
    #     read_only = True,
    #     paginated = 15,
    #     filter = dict(deleted=False, collection__private=False, collection__reader__user__is_active=True)
    # )
    reader = CollectionUserSerializer(read_only=True)
    class Meta:
        model = Collection
        exclude = ["private", "created", "deleted", "id"]

class PublicSavedSerializer(serializers.ModelSerializer):
    saved_by = serializers.HiddenField(default=fields.CurrentReader())
    rec = serializers.HiddenField(default=fields.CurrentModel())
    class Meta:
        model = Saved
        fields = ["saved_by", "rec"]
        validators = [
            UniqueTogetherValidator(
                queryset=Saved.objects.filter(deleted=False),
                fields=['saved_by', 'rec']
            )
        ]

class QuerySerializer(serializers.ModelSerializer):
    maker = serializers.CharField(source="reader.user.username")
    matching_recs = serializers.IntegerField()
    class Meta:
        model = Collection
        fields = ["name", "about", "uid", "maker", "matching_recs"]