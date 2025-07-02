from utils.fields import TagsField, CurrentModel
from user_profile.models import Rec, Collection
from rest_framework.serializers import ModelSerializer, HiddenField, SerializerMethodField, CharField

class RecSerializer(ModelSerializer):
    author = TagsField()
    fandom = TagsField()
    warnings = TagsField()
    ship = TagsField()
    characters = TagsField()
    tags = TagsField()
    collection = HiddenField(default=CurrentModel())
    notes = CharField(allow_blank=True, required=False)

    class Meta:
        model = Rec
        exclude = ["created", "deleted", "id"]

class CollectionNameSerializer(ModelSerializer):
    recs = SerializerMethodField("rec_count")
    
    class Meta:
        model = Collection
        fields = ["uid", "name", "private", "recs"]

    def rec_count(self, instance):
        return instance.collection_recs.filter(deleted=False).count() or 0

class PublicCollectionSerializer(CollectionNameSerializer):
    class Meta:
        model = Collection
        fields = ["uid", "name", "private", "recs", "about"]