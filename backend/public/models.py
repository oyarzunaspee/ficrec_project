from django.db import models
from user_profile.models import Rec
from authentication.models import Reader
import uuid

class Saved(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    saved_by = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name="reader_saved")
    rec = models.ForeignKey(Rec, on_delete=models.CASCADE, related_name="rec_saved")
    read = models.BooleanField(default=False)
    created = models.DateField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created']
    
    def __str__(self):
        return f"{self.saved_by.user.username} - {self.rec.title}"