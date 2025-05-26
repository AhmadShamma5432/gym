from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .autocomplete_views import SubCategoryAutocomplete, BrandAutocomplete

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"main-categories", MainCategoryViewSet, basename="main-category")
router.register(r"sub-categories", SubCategoryViewSet, basename="sub-category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"rates", RatingViewSet, basename="rate")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"profiles", ProfileView, basename="profile")
router.register(r"orders", OrderView, basename="order")


products_router = routers.NestedSimpleRouter(router, r"products", lookup="product")
products_router.register(r"comments", CommentViewSet, basename="product-comments")
products_router.register(r"rates", RatingViewSet, basename="product-rates")


urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls)),
]
