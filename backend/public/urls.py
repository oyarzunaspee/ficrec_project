from django.urls import path, include
from public import views
from rest_framework_nested import routers


router = routers.SimpleRouter()
router.register("user", views.PublicProfileViewSet)
router.register("find", views.QueryViewSet)

username_router = routers.NestedSimpleRouter(router, "user", lookup='reader')
username_router.register("collections", views.PublicCollectionViewSet)

collection_router = routers.NestedSimpleRouter(username_router, "collections", lookup='collection')
collection_router.register("recs", views.SaveRecViewSet, basename="recs")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(username_router.urls)),
    path("", include(collection_router.urls))
]