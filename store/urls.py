from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .autocomplete_views import SubCategoryAutocomplete, BrandAutocomplete

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'main-categories', MainCategoryViewSet, basename='main-category')
router.register(r'sub-categories', SubCategoryViewSet, basename='sub-category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'rates', RatingViewSet, basename='rate')
router.register(r'comments', CommentViewSet, basename='comment')
router.register('cart',CartView,basename='cart')
router.register('profile',ProfileView,basename='profile')
router.register('order',OrderView,basename='order')

products_router = routers.NestedSimpleRouter(router, r'products', lookup='product')
products_router.register(r'comments', CommentViewSet, basename='product-comments')
products_router.register(r'rates', RatingViewSet, basename='product-rates')

nested_cart_router = routers.NestedDefaultRouter(router,'cart',lookup='cart')
nested_cart_router.register('items',CartItemView,basename='cart-items')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(nested_cart_router.urls)),
    
    # path('subcategory-autocomplete/', SubCategoryAutocomplete.as_view(), name='subcategory-autocomplete'),
    # path('brand-autocomplete/', BrandAutocomplete.as_view(), name='brand-autocomplete'),
]
