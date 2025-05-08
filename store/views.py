from django.shortcuts import render
from rest_framework.mixins import ListModelMixin,RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from store.filters import ProductFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets

from rest_framework.filters import SearchFilter, OrderingFilter
from .models import MainCategory, SubCategory, Brand, Product
from django.db.models import Case, Count, IntegerField, Value, When
from .serializers import *
from rest_framework.mixins import *
from rest_framework.decorators import action

class MainCategoryViewSet(GenericViewSet,ListModelMixin,RetrieveModelMixin):
    """
    API endpoint for MainCategory.
    """
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer

class SubCategoryViewSet(GenericViewSet,ListModelMixin,RetrieveModelMixin):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class BrandViewSet(GenericViewSet,ListModelMixin,RetrieveModelMixin):
    """
    API endpoint for Brand.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ProductViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """
    API endpoint for Product.
    Supports filtering by main_category, sub_category, brand, or any combination.
    """
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter  
    search_fields = ['name_en', 'name_ar']  # Fields to search by

    def get_queryset(self):
        return Product.objects.prefetch_related('product_comments__user','sizes','colors','images')\
                            .select_related('main_category', 'sub_category', 'brand')\
        .annotate(
            rating_1=Count(Case(When(ratings__value=1, then=Value(1)), output_field=IntegerField())),
            rating_2=Count(Case(When(ratings__value=2, then=Value(1)), output_field=IntegerField())),
            rating_3=Count(Case(When(ratings__value=3, then=Value(1)), output_field=IntegerField())),
            rating_4=Count(Case(When(ratings__value=4, then=Value(1)), output_field=IntegerField())),
            rating_5=Count(Case(When(ratings__value=5, then=Value(1)), output_field=IntegerField())),
        )
    


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.select_related('product', 'user').filter(product__id = self.kwargs['product_pk'],user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PATCH','PUT']:
            return UpdateRatingSerializer
        return RatingSerializer
    
    def get_serializer_context(self):
        return {"user_id": self.request.user.id,"product_id": self.kwargs['product_pk']}
    
    
class CommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Comment.objects.select_related('product', 'user').filter(product__id = self.kwargs['product_pk'])

    def get_serializer_class(self):
        if self.request.method in ['PATCH','PUT']:
            return UpdateCommentSerializer
        return CommentSerializer
   
    def get_serializer_context(self):
        return {"user_id": self.request.user.id,"product_id": self.kwargs['product_pk']}
    

     

class CartView(CreateModelMixin,DestroyModelMixin,RetrieveModelMixin,GenericViewSet):

    def get_queryset(self):
        return Cart.objects.prefetch_related('items__product').all()
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateCartSerailizer
        elif self.request.method == 'GET':
            return GetCartSerializer

class CartItemView(ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id = self.kwargs['cart_pk'])

    def get_serializer_class(self):
        if self.request.method == 'PATCH' or self.request.method == 'PUT':
            return UpdateCartItemSerializer
        elif self.request.method == 'POST':
            return CreateCartItemSerializer
        else:
            return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_pk":self.kwargs['cart_pk']}
    
class ProfileView(CreateModelMixin,UpdateModelMixin,RetrieveModelMixin,GenericViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        return {"user_id":self.request.user.id}
    

    def perform_create(self, serializer):
        return serializer.save()
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = self.perform_create(serializer)
        return Response(ProfileSerializer(profile).data)
    
    
    @action(detail=False,methods=['GET','PUT'])
    def me(self,request):
        profile , created = Profile.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = ProfileSerializer(profile,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderView(DestroyModelMixin,ListModelMixin,RetrieveModelMixin,CreateModelMixin,UpdateModelMixin,GenericViewSet):
    
    http_method_names = ['patch','delete','options','head','get','post']



    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializers
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        else:
            return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        else:
            profile , created = Profile.objects.get_or_create(user_id=self.request.user.id)
            return Order.objects.prefetch_related('items__product').filter(profile=profile)

    
    def create(self, request, *args, **kwargs):
        cart_id = None
        try: 
            cart_id = request.data['cart_id']
        except: 
            cart_id = None
        serializer = CreateOrderSerializers(data=request.data,context={"user_id":self.request.user.id,"cart_id":cart_id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response(OrderSerializer(order).data)
    