from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagsViewSet

v1_router = DefaultRouter()
v1_router.register("tags", TagsViewSet)
v1_router.register("ingredients", IngredientViewSet)
v1_router.register("recipes", RecipeViewSet)

urlpatterns = v1_router.urls + [
    path("", include("djoser.urls.base")),
    path("auth/", include("djoser.urls.authtoken")),
]
