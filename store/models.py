from django.db import models
from project.settings import AUTH_USER_MODEL
from django.core.validators import MinValueValidator, MaxValueValidator


class MainCategory(models.Model):
    name_en = models.CharField(max_length=50, unique=True)
    name_ar = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name_en

    class Meta:
        db_table = "MainCategory"


class SubCategory(models.Model):
    """
    Represents the sub-category of a product.
    """

    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name_en} ({self.name_ar})"

    class Meta:
        db_table = "SubCategory"


class Brand(models.Model):
    """
    Represents a brand with English and Arabic names.
    """

    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name_en} ({self.name_ar})"

    class Meta:
        db_table = "Brand"


class Size(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    # hex_code = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Represents a product with a main category, sub-category, and a foreign key to Brand.
    """

    main_category = models.ForeignKey(
        MainCategory, on_delete=models.CASCADE, related_name="sub_categories"
    )
    sub_category = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, related_name="products"
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")

    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)

    description_en = models.TextField(blank=True, default="")
    description_ar = models.TextField(blank=True, default="")

    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    is_offered = models.BooleanField()
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    why_should_i_buy_it_en = models.TextField()
    why_should_i_buy_it_ar = models.TextField()

    how_should_i_take_it_en = models.TextField()
    how_should_i_take_it_ar = models.TextField()

    sizes = models.ManyToManyField(Size, related_name="product_sizes", blank=True)
    colors = models.ManyToManyField(Color, related_name="product_colors", blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name_en} ({self.name_ar})"

    class Meta:
        db_table = "Product"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="product_images/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name_en}"


class Rating(models.Model):
    """
    Represents a rating given by a user to a product.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings"
    )
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating value must be between 1 and 5.",
    )
    comment = models.TextField(default='no comment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rated {self.product.name_en} as {self.value}"

    class Meta:
        unique_together = ("user", "product")


class Comment(models.Model):
    """
    Represents a comment made by a user on a product.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_comments"
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    weight = models.FloatField()  # in kg
    goal_weight = models.FloatField(null=True, blank=True)
    height = models.FloatField()  # in cm
    birth_date = models.DateField(null=True, blank=True)

    # Player-specific info
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ("BEGINNER", "Beginner"),
            ("INTERMEDIATE", "Intermediate"),
            ("ADVANCED", "Advanced"),
        ],
        null=True,
        blank=True,
    )
    fitness_goal = models.TextField(
        null=True, blank=True
    )  # e.g., "Lose fat", "Build muscle"

    certification = models.CharField(max_length=255, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)


class Order(models.Model):
    pending = "P"
    complete = "C"
    failed = "F"
    CHOICES_ARRAY = [(pending, "pending"), (complete, "complete"), (failed, "failed")]
    placed_at = models.DateField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=CHOICES_ARRAY, default=pending
    )
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    postal_Code = models.CharField(max_length=255)
    total_products_price = models.DecimalField(max_digits=12, decimal_places=3)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    total_product_price = models.DecimalField(max_digits=12, decimal_places=3)
    size = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
