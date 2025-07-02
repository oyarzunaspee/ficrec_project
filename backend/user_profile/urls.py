from django.urls import path, include
from user_profile import views
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register("user", views.ProfileViewSet)
router.register("collections", views.CollectionViewSet)
router.register("saved", views.SavedViewSet)

collection_router = routers.NestedSimpleRouter(router, "collections", lookup='collection')
collection_router.register("recs", views.RecViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("", include(collection_router.urls))
]