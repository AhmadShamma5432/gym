from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Customizing the UserAdmin for the custom User model
class CustomUserAdmin(UserAdmin):
    # Customize the admin site header and title
    admin.site.site_header = "Fit Admin Panel"
    admin.site.site_title = "Fit Admin Portal"
    admin.site.index_title = "Welcome to Fit Admin Panel"

# Register the User model with the custom admin class
admin.site.register(User)