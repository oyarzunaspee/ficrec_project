from rest_framework import serializers
from django.core.validators import RegexValidator
from authentication.models import Reader
from user_profile.models import Collection, Rec
from user_profile.utils import CODE_REGEX
from public.models import Saved
from utils import fields as utils_fields
from utils import serializers as utils_serializers
import re
from bs4 import BeautifulSoup
import nh3


class ReaderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    collections = utils_fields.NestedListField(
        child=utils_serializers.CollectionNameSerializer,
        source="reader_collection",
        read_only=True,
        filter = dict(deleted=False, reader__user__is_active=True)
    )
    class Meta:
        model = Reader
        fields = ["uid", "username", "bio", "avatar", "collections", "highlight"]
        read_only_fields = ["uid", "username", "collections"]

class CollectionSerializer(serializers.ModelSerializer):
    reader = serializers.HiddenField(default=utils_fields.CurrentReader())
    username = serializers.CharField(source="reader.user.username")
    # recs = utils_fields.NestedListField(
    #     child = utils_serializers.RecSerializer,
    #     source = "collection_recs",
    #     read_only = True,
    #     paginated = 15,
    #     filter = dict(deleted=False, collection__reader__user__is_active=True)
    # )
    class Meta:
        model = Collection
        exclude = ["created", "deleted", "id"]
        read_only_fields = ["uid", "recs", "fandom", "ship", "warnings", "tags", "summary"]
        extra_kwargs = {'reader': {'write_only': True}}
        
class ToggleSerializer(serializers.Serializer):
    toggle = serializers.ChoiceField(["private", "fandom", "ship", "warnings", "tags", "summary", "characters"])

    def save(self, **kwargs):
        collection = self.context["view"].get_object()
        field = self.validated_data["toggle"]
        field_value = getattr(collection, field)
        setattr(collection, field, not field_value)
        collection.save()

        return collection

class PrepareRecSerializer(serializers.Serializer):
    notes = serializers.CharField(allow_blank=True, required=False)
    code = serializers.CharField(required=True, validators=[RegexValidator(CODE_REGEX)])
    
    def validate_code(self, value):
        regex = re.search(CODE_REGEX, value)
        
        if not regex:
            raise ValueError("Invalid code")
        if len(value) != regex.end():
            raise ValueError("Invalid code")

        regex_keys = list(regex.groupdict().keys())
        if len(regex_keys) < 8:
            raise ValueError("Invalid code")
        # required groups
        for key in ["url", "title", "chapters", "rating", "words", "warnings", "fandom", "author"]:
            if key not in regex_keys:
                raise ValueError("Invalid code")
        return value
    
    def format_code(self):
        regex = re.search(CODE_REGEX, self.data["code"])
        content = regex.groupdict()
        keys = list(content.keys())
        rec_data = dict(notes = self.data["notes"])

        for key in keys:
            if key == "url":
                soup = BeautifulSoup(regex.group(key), 'html.parser')
                rec_data["link"] = soup.a["href"]
            if key == "summary":
                rec_data["summary"] = regex.group(key)
            if key in ["title", "chapters", "rating", "words"]:
                rec_data[key] = nh3.clean(regex.group(key), tags={""})
            if key in ["author", "fandom", "warnings", "ship", "characters", "tags"]:
                if regex.group(key):
                    rec_data[key] = nh3.clean(regex.group(key), tags={""})
        return rec_data
    
    def save(self):
        data = self.format_code()
        serializer = utils_serializers.RecSerializer(data=data, context=self.context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

class EditRecSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rec
        fields = ["notes"]

class SavedListSerializer(serializers.ModelSerializer):
    bookmarks = serializers.SerializerMethodField()
    class Meta:
        model = Reader
        fields = ["bookmarks"]

    def get_bookmarks(self, obj):
        return obj.reader_saved.all().values_list("rec__uid", flat=True).distinct()

class SavedCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["name", "uid"]    

class SavedSerializer(serializers.ModelSerializer):
    collection = SavedCollectionSerializer(source="rec.collection", read_only=True)
    rec = utils_serializers.RecSerializer(read_only=True)
    maker = serializers.CharField(source="rec.collection.reader.user.username")

    class Meta:
        model = Saved
        fields = ["collection", "rec", "maker", "uid", "read"]