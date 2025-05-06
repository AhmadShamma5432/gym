import django_filters
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductFilter(django_filters.FilterSet):
    """
    Custom filter for the Product model.
    Allows filtering by main_category, sub_category, brand, or any combination.
    """
    main_category = django_filters.NumberFilter(field_name="main_category", lookup_expr='exact')
    sub_category = django_filters.NumberFilter(field_name="sub_category", lookup_expr='exact')
    brand = django_filters.NumberFilter(field_name="brand", lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['main_category', 'sub_category', 'brand']