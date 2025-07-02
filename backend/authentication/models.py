from django.db import models
from django.contrib.auth.models import User
import uuid

class Reader(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_reader')
    avatar = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=100)
    highlight = models.CharField(default="default")

    def __str__(self):
        return self.user.username