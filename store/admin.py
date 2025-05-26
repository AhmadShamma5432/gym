from .models import *
from django.contrib import admin


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

class SizeInline(admin.TabularInline):
    model = Product.sizes.through
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        # Cache size queryset once
        if not hasattr(request, '_size_queryset_cache'):
            request._size_queryset_cache = Size.objects.order_by('name')

        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "size":
            kwargs['queryset'] = request._size_queryset_cache
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
class ColorInline(admin.TabularInline):
    model = Product.colors.through
    extra = 1 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('color','product')
    

class ImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product')
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Optimized admin class for the Product model.
    """
    list_display = ('id', 'name_en', 'name_ar', 'main_category', 'sub_category', 'brand', 'price')

    search_fields = ('name_en', 'name_ar', 'main_category__name_en', 'sub_category__name_en', 'brand__name_en')

    exclude = ['colors','sizes']

    inlines = [
        ImageInline,
        SizeInline,
    ]

    autocomplete_fields = ('sub_category', 'brand')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'main_category', 'sub_category', 'brand'
        ).prefetch_related(
            'images',
            'sizes',
            'colors'
        ).distinct()