from django.contrib import admin
from .models import User, UserPermission

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active', 'is_staff')

@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'permission_name')
    search_fields = ('user__email', 'permission_name')
    list_filter = ('permission_name',)
