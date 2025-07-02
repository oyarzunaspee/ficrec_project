from django.db import models
import uuid
from authentication.models import Reader

class Collection(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='reader_collection')
    name = models.CharField(max_length=250)
    about = models.TextField(blank=True, null=True)
    private = models.BooleanField(default=False)
    created = models.DateField(auto_now=True)
    deleted = models.BooleanField(default=False)
    fandom = models.BooleanField(default=False)
    ship = models.BooleanField(default=False)
    warnings = models.BooleanField(default=False)
    tags = models.BooleanField(default=False)
    summary = models.BooleanField(default=False)
    characters = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

class Rec(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="collection_recs")
    title = models.CharField(max_length=250)
    words = models.IntegerField()
    author = models.TextField()
    chapters = models.CharField(max_length=20)
    fandom = models.TextField()
    rating = models.CharField(max_length=100)
    warnings = models.TextField()
    ship = models.TextField()
    characters = models.TextField()
    tags = models.TextField()
    summary = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    link = models.URLField()
    created = models.DateField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.title} - {self.author} ({self.collection.reader.user.username})"