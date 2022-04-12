from django.contrib import admin
from .models import *


# Model Admin for Store
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'phone', 'email', 'image_icon', 'category', 'gstin', 'address', 'is_active', 'joined_at',)
    list_filter = ('is_active',)
    search_fields = ('name', 'gstin', 'phone', 'email',)


# Model Admin for StoreCategory
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image_icon', 'is_active', 'created_at',)
    list_filter = ('is_active', 'name',)
    search_fields = ('name', 'is_active',)


# Model Admin for store staff
class StoreStaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'user', 'image_icon', 'is_admin', 'is_staff', 'position', 'updated_at',)
    list_filter = ('store', 'position',)
    search_fields = ('id', 'store', 'user', 'position',)


# Model admin for casper user permissions
class StaffPermissionsAdmin(admin.ModelAdmin):
    list_display = (
        'store_name', 'staff', 'manage_catalogues', 'manage_stores', 'manage_vendors', 'manage_customers', 'manage_orders',
        'manage_staffs',
        'manage_reports', 'manage_settings')
    list_filter = ('manage_catalogues', 'manage_stores', 'manage_vendors',)
    search_fields = ('user__email',)


# Registering the models
admin.site.register(StoreCategory, StoreCategoryAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(StoreStaff, StoreStaffAdmin)
admin.site.register(StaffPermission, StaffPermissionsAdmin)
