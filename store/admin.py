from .models import *
from django.contrib import admin
from django.utils.html import format_html


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    """
    Custom admin class for the MainCategory model.
    """
    list_display = ('id', 'name_en', 'name_ar')

    search_fields = ('id','name_en', 'name_ar')

    list_filter = ('id','name_en','name_ar')

    ordering = ('id','name_en',)

    fields = ('name_en', 'name_ar')

    list_per_page = 20


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'name_ar')
    search_fields = ('id', 'name_en', 'name_ar')
    list_filter = ('id','name_en','name_ar')
    ordering = ('id', 'name_en')
    fields = ('name_en', 'name_ar')
    list_per_page = 20

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'name_ar')
    search_fields = ('id','name_en', 'name_ar')
    list_filter = ('id','name_en', 'name_ar')
    ordering = ('id', 'name_en')
    fields = ('name_en', 'name_ar')
    list_per_page = 20

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at',)
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'is_main')
    list_filter = ('product', 'is_main')
    search_fields = ('product__name_en', 'product__name_ar')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main')
    readonly_fields = ()
    can_delete = True

class ProductSizeInline(admin.TabularInline):
    model = Product.sizes.through  # Use the auto-generated ManyToMany table
    extra = 1
    verbose_name = "Size"
    verbose_name_plural = "Sizes"

class ProductColorInline(admin.TabularInline):
    model = Product.colors.through  # Same here
    extra = 1
    verbose_name = "Color"
    verbose_name_plural = "Colors"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Optimized admin class for the Product model.
    """
    list_display = ('id', 'name_en', 'name_ar', 'main_category', 'sub_category', 'brand', 'price')

    search_fields = ('name_en', 'name_ar', 'main_category__name_en', 'sub_category__name_en', 'brand__name_en')

    list_filter = (
        'main_category__name_en',
        'sub_category__name_en',
        'brand__name_en',
        'price'
    )

    inlines = [
        ProductImageInline,
        ProductSizeInline,
        ProductColorInline,
    ]

    autocomplete_fields = ('sub_category', 'brand')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'main_category', 'sub_category', 'brand'
        ).prefetch_related(
            'sizes',
            'colors',
            'images'
        )