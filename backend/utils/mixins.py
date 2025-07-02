from rest_framework.permissions import IsAdminUser
from rest_framework.mixins import DestroyModelMixin

class ForbidListMixin:
    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class CustomDestroyMixin(DestroyModelMixin):
    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()