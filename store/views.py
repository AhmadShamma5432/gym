from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from store.filters import ProductFilter
from rest_framework import viewsets

from .models import MainCategory, SubCategory, Brand, Product
from django.db.models import Case, Count, IntegerField, Value, When
from .serializers import *
from rest_framework.mixins import *
from rest_framework.decorators import action
from django.db.models import Prefetch


class MainCategoryViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """
    API endpoint for MainCategory.
    """

    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer


class SubCategoryViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class BrandViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
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
    search_fields = ["name_en", "name_ar"] 

    def get_queryset(self):
        rating_prefetch = Prefetch(
            'ratings',
            queryset = Rating.objects.select_related("product", "user").filter(user=self.request.user),
            to_attr = 'product_rate'
        )
        return (
            Product.objects.prefetch_related(
                "product_comments__user", "sizes", "colors", "images",rating_prefetch
            )
            .select_related("main_category", "sub_category", "brand")
            .filter(is_active=True)
            .annotate(
                rating_1=Count(
                    Case(
                        When(ratings__value=1, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                rating_2=Count(
                    Case(
                        When(ratings__value=2, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                rating_3=Count(
                    Case(
                        When(ratings__value=3, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                rating_4=Count(
                    Case(
                        When(ratings__value=4, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                rating_5=Count(
                    Case(
                        When(ratings__value=5, then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
            )
        )
    # def get_serializer_context(self):
    #     return {"request": self.request}


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer

    def get_queryset(self):

        return Rating.objects.select_related("product", "user").filter(
            product__id=self.kwargs["product_pk"], user=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return UpdateRatingSerializer
        return RatingSerializer

    def get_serializer_context(self):
        return {
            "user_id": self.request.user.id,
            "product_id": self.kwargs["product_pk"],
        }


class CommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Comment.objects.select_related("product", "user").filter(
            product__id=self.kwargs["product_pk"]
        )

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return UpdateCommentSerializer
        return CommentSerializer

    def get_serializer_context(self):
        return {
            "user_id": self.request.user.id,
            "product_id": self.kwargs["product_pk"],
        }


class ProfileView(
    CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet
):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = self.perform_create(serializer)
        return Response(ProfileSerializer(profile).data)

    @action(detail=False, methods=["GET", "PUT"])
    def me(self, request):
        profile, created = Profile.objects.get_or_create(user_id=request.user.id)
        if request.method == "GET":
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = ProfileSerializer(profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related(
                "items__product__brand",
                "items__product__main_category",
                "items__product__sub_category",
            )
            .select_related("user")
            .order_by('-id')
        )

    def get_serializer_context(self):
        return {
            "user_id": self.request.user.id,
            "user": self.request.user,
            "request": self.request,
        }

    def get_serializer_class(self):
        return OrderSerializer
