from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Admin site customizations
    admin.site.site_header = "Gifty Admin Panel"
    admin.site.site_title = "Gifty Admin Portal"
    admin.site.index_title = "Welcome to Gifty's Admin Panel"

    # Fields displayed in list view
    list_display = ('phone', 'name', 'is_active', 'is_staff', 'is_superuser')

    # Filters in sidebar
    list_filter = ('is_active', 'is_staff', 'is_superuser')

    # Searchable fields
    search_fields = ('name', 'phone')

    # Editable directly in list view
    list_editable = ('is_active',)

    # Fieldsets for detail view
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('name',)}),  # Removed duplicate phone
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login',)}),
    )

    # Fields when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Read-only fields
    readonly_fields = ('last_login',)

    # Default ordering
    ordering = ('phone',)