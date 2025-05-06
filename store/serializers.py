from rest_framework import serializers
from .models import *
from core.models import User
from django.db import transaction
from core.serializers import UserSerializer

class MainCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the MainCategory model.
    """
    class Meta:
        model = MainCategory
        fields = ['id', 'name_en', 'name_ar']

class SubCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the SubCategory model.
    """
    class Meta:
        model = SubCategory
        fields = ['id', 'name_en', 'name_ar']

class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for the Brand model.
    """
    class Meta:
        model = Brand
        fields = ['id', 'name_en', 'name_ar']

class ProductSerializer(serializers.ModelSerializer):
    main_category = MainCategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id','main_category','sub_category','brand','name_en', 'name_ar',
            'description_en', 'description_ar','price','is_offered','offerd_price',
            'stock','why_should_i_buy_it','how_should_i_take_it'
        ]
class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'user', 'value', 'created_at']

    def create(self, validated_data):
        product_id = self.context['product_id']
        user_id = self.context['user_id']
        return Rating.objects.create(**validated_data,user_id=user_id,product_id=product_id)
    
class UpdateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['value']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']

    def create(self, validated_data):
        product_id = self.context['product_id']
        user_id = self.context['user_id']
        return Comment.objects.create(**validated_data,user_id=user_id,product_id=product_id)
    
class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']

    def create(self, validated_data):
        product_id = self.context['product_id']
        user_id = self.context['user_id']
        return Comment.objects.create(**validated_data,user_id=user_id,product_id=product_id)
    
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']

class ProductSerializer(serializers.ModelSerializer):
    rating_counts = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    product_comments = CommentSerializer(many=True,read_only=True)
    main_category = MainCategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id','main_category','sub_category','brand','name_en', 'name_ar',
            'description_en', 'description_ar','price','is_offered','old_price',
            'stock','why_should_i_buy_it','how_should_i_take_it','rating_counts','product_comments',
            'sizes','colors','images'
        ]

    def get_sizes(self,obj):
        return [size.name for size in obj.sizes.all()]
    
    def get_colors(self,obj):
        return [color.name for color in obj.colors.all()]
    
    def get_images(self, obj):
        request = self.context.get('request')
        return [
            request.build_absolute_uri(image.image.url)
            for image in obj.images.all()
        ]
    
    def get_rating_counts(self, obj):
        return {
            "1": getattr(obj, 'rating_1', 0),
            "2": getattr(obj, 'rating_2', 0),
            "3": getattr(obj, 'rating_3', 0),
            "4": getattr(obj, 'rating_4', 0),
            "5": getattr(obj, 'rating_5', 0),
        }     
           
class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'user', 'value', 'created_at']

    def create(self, validated_data):
        product_id = self.context['product_id']
        user_id = self.context['user_id']
        return Rating.objects.create(**validated_data,user_id=user_id,product_id=product_id)
    
class UpdateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['value']


    
class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name_en','name_ar','price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']

    def get_total_price(self,obj):
        return obj.product.price * obj.quantity

class CreateCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']
    
    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_pk']
        with transaction.atomic():

            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"The product you are looking for is not exist")
            
            cart_item , created = CartItem.objects.get_or_create(cart_id=cart_id,
                                                                product=product,
                                                                defaults={'quantity':quantity})
            if not created :
                cart_item.quantity += quantity
                cart_item.save()

            self.instance = cart_item

            return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']
    
    def get_total_price(self,obj):
        return obj.product.price * obj.quantity

class CreateCartSerailizer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Cart
        fields = ['id','created_at']

class GetCartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id','items','total_price']

    def get_total_price(self,obj):
        return sum([ value.product.price * value.quantity for value in obj.items.all()])


class ProfileSerializer(serializers.ModelSerializer):
    fitness_level = serializers.CharField(source='get_fitness_level_display', read_only=True)
    user = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = [
            'id',
            'first_name',
            'last_name',
            'user',
            'weight',
            'goal_weight',
            'height',
            'birth_date',
            'fitness_level',
            'fitness_goal',
            'certification',
            'years_of_experience',
        ]
        read_only_fields = ['id']
    
    def get_user(self,obj):
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
        user_id = self.context['user_id']
        validated_data['user_id'] = user_id
        print(user_id)
        profile = Profile.objects.create(**validated_data)
        return profile

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True,many=True)
    profile = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id','placed_at','payment_status','profile','items']
    
    def get_profile(self,obj):
        return {
            "phone": obj.profile.user.phone,
            "first_name": obj.profile.first_name,
            "last_name": obj.profile.last_name
        }


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializers(serializers.Serializer):
    
    cart_id = serializers.UUIDField(write_only=True)
  
    def validate_cart_id(self,value):
        if not Cart.objects.filter(pk=value).exists():
            print("here")
            raise serializers.ValidationError("No cart with given ID was found")
        if CartItem.objects.filter(cart_id = value).count() == 0 :
            print("here")
            raise serializers.ValidationError("The Cart is empty")

    def save(self, **kwargs):

        with transaction.atomic():
            cart_id = self.context['cart_id']
            user_id = self.context['user_id']
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            if len(cart_items) == 0 :
                raise serializers.ValidationError("There is no items in your cart to order")

            profile ,created= Profile.objects.get_or_create(user_id=user_id)
            order = Order.objects.create(profile_id=profile.id)

            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    quantity = item.quantity,
                    price = item.product.price
                )
                for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            return order