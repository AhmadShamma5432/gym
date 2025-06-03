from rest_framework import serializers
from .models import (
    MainCategory,
    SubCategory,
    Brand,
    Product,
    Rating,
    Comment,
    Size,
    Color,
    ProductImage,
    Profile,
    Order,
    OrderItem,
)
from django.db import transaction
from core.serializers import UserSerializer


class MainCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the MainCategory model.
    """

    class Meta:
        model = MainCategory
        fields = ["id", "name_en", "name_ar"]


class SubCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the SubCategory model.
    """

    class Meta:
        model = SubCategory  # noqa: F405
        fields = ["id", "name_en", "name_ar"]


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for the Brand model.
    """

    class Meta:
        model = Brand
        fields = ["id", "name_en", "name_ar"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "created_at"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        user_id = self.context["user_id"]
        return Comment.objects.create(
            **validated_data, user_id=user_id, product_id=product_id
        )


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name"]


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_main"]

class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ["id", "user", "value","comment", "created_at"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        user_id = self.context["user_id"]
        return Rating.objects.create(
            **validated_data, user_id=user_id, product_id=product_id
        )

class ProductSerializer(serializers.ModelSerializer):
    rating_counts = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    product_rate = serializers.SerializerMethodField()
    ratings = RatingSerializer(many=True,read_only=True)
    main_category = MainCategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "main_category",
            "sub_category",
            "brand",
            "name_en",
            "name_ar",
            "description_en",
            "description_ar",
            "price",
            "is_offered",
            "old_price",
            "stock",
            "why_should_i_buy_it_en",
            "why_should_i_buy_it_ar",
            
            "how_should_i_take_it_en",
            "how_should_i_take_it_ar",
            
            "rating_counts",
            "ratings",
            "product_rate",
            "sizes",
            "colors",
            "images",
        ]

    def get_sizes(self, obj):
        return [size.name for size in obj.sizes.all()]

    def get_colors(self, obj):
        return [color.name for color in obj.colors.all()]

    def get_images(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(image.image.url) for image in obj.images.all()
        ]

    def get_product_rate(self,obj):
        print(obj.product_rate)
        if hasattr(obj, 'product_rate') and obj.product_rate:
            return RatingSerializer(obj.product_rate[0]).data  # or serialize the whole object
            return RatingSerializer(obj.product_rate)
        return None

    def get_rating_counts(self, obj):
        return {
            "1": getattr(obj, "rating_1", 0),
            "2": getattr(obj, "rating_2", 0),
            "3": getattr(obj, "rating_3", 0),
            "4": getattr(obj, "rating_4", 0),
            "5": getattr(obj, "rating_5", 0),
        }


class UpdateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["value","comment"]


class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["text"]


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name_en", "name_ar", "price"]


class ProfileSerializer(serializers.ModelSerializer):
    fitness_level = serializers.CharField(
        source="get_fitness_level_display", read_only=True
    )
    user = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "user",
            "weight",
            "goal_weight",
            "height",
            "birth_date",
            "fitness_level",
            "fitness_goal",
            "certification",
            "years_of_experience",
        ]
        read_only_fields = ["id"]

    def get_user(self, obj):
        return obj.user.phone

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     # Optionally hide coach-specific or player-specific fields based on role
    #     if data['role'] == 'PLAYER':
    #         data.pop('certification')
    #         data.pop('years_of_experience')
    #     else:
    #         data.pop('fitness_level')
    #         data.pop('fitness_level_display')
    #         data.pop('fitness_goal')

    #     return data

    def create(self, validated_data):
        user_id = self.context["user_id"]
        validated_data["user_id"] = user_id
        profile = Profile.objects.create(**validated_data)
        return profile


class OrderItemProductSerializer(serializers.ModelSerializer):
    main_category = MainCategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "main_category",
            "sub_category",
            "brand",
            "name_en",
            "name_ar",
            "description_en",
            "description_ar",
            "price",
            "is_offered",
            "old_price",
            "stock",
            'image'
        ]
    def get_image(self, obj):
        request = self.context.get("request")
        try: 
            return request.build_absolute_uri(obj.images.all()[0].image.url) 
        except: return ""


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(write_only=True)
    total_product_price = serializers.CharField(max_length=100)
    color = serializers.CharField(required=False)
    size = serializers.CharField(required=False)
    

    class Meta:
        model = OrderItem
        fields = [
            "product",
            "product_id",
            "quantity",
            "size",
            "color",
            "total_product_price",
        ]

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid product ID.")
        return value

    def get_product(self, obj):
        request = self.context.get("request")
        serializer = OrderItemProductSerializer(
            obj.product, context={"request": request}
        )
        return serializer.data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserSerializer(read_only=True)
    total_products_price = serializers.CharField(max_length=100)

    class Meta:
        model = Order
        fields = [
            "id",
            "payment_status",
            "placed_at",
            "address",
            "city",
            "area",
            "street",
            "postal_Code",
            "total_products_price",
            "user",
            "items",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            user_id = self.context["user_id"] 
            items_data = validated_data.pop("items")

            order = Order.objects.create(user_id=user_id, **validated_data)

            order_items = []
            for item_data in items_data:
                product_id = item_data.pop("product_id")
                order_item = OrderItem(order=order, product_id=product_id, **item_data)
                order_items.append(order_item)

            OrderItem.objects.bulk_create(order_items)

            return order
