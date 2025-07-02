from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView
from authentication import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("user", views.AuthUserViewSet, basename="user")

urlpatterns = [
    path('signup/', views.AuthView.as_view(), name='signup'),
    path("login/", views.CustomTokenObtainView.as_view(), name="token_obtain_pair"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path('reactivate/', views.ReactivateView.as_view(), name='reactivate'),
    path("", include(router.urls))
]