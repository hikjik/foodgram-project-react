from django.urls import include, path

from .v1.urls import urlpatterns as api_v1

urlpatterns = [
    path("", include(api_v1)),
]
