from django.urls import path, include


urlpatterns = [
    path("api/v1/auth/", include('authentication.urls')),
    path("api/v1/profile/", include('user_profile.urls')),
    path("api/v1/public/", include('public.urls')),

]
