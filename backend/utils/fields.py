from rest_framework.serializers import ListSerializer, Field, ListSerializer
from django.core.paginator import Paginator
import copy
from django.db.models import Q

class CurrentReader:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.user_reader

    def __repr__(self):
        return '%s()' % self.__class__.__name__

class CurrentModel:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["view"].get_object()

    def __repr__(self):
        return '%s()' % self.__class__.__name__

class TagsField(Field):
    def to_representation(self, value):
        return value.split(", ")
    def to_internal_value(self, data):
        return str(data)
    
class CustomListField(ListSerializer):
    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child', copy.deepcopy(self.child))()
        self.allow_empty = kwargs.pop('allow_empty', True)
        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)
        assert self.child is not None, '`child` is a required argument.'
        # assert not inspect.isclass(self.child), '`child` has not been instantiated.'
        self.child.bind(field_name='', parent=self)
        super().__init__(*args, **kwargs)

class NestedListField(CustomListField):
    def __init__(self, *args, **kwargs):
        self.filter = kwargs.pop('filter', dict())
        self.paginated = kwargs.pop('paginated', None)
        super().__init__(*args, **kwargs)

    def to_representation(self, data):
        data = data.filter(**self.filter)
        query = self.context['request'].query_params.get('query') or None
        if query:
            data = data.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(fandom__icontains=query) | Q(ship__icontains=query))
        if not self.paginated:
            return super(NestedListField, self).to_representation(data)
        else:
            paginator = Paginator(data, self.paginated)

            pages = paginator.num_pages
            current = self.context['request'].query_params.get('page') or 1
            current = int(current)
            if current > pages:
                current = pages
            recs_by_page = paginator.page(current)
            serializer = self.child.__class__(recs_by_page, many=True)
   
            return dict(current=current, pages=pages, results=serializer.data)