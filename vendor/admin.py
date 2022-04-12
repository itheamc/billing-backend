from django.contrib import admin
from .models import *


# Model Admin for Vendor
class VendorAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'name', 'email', 'phone', 'image_icon', 'website', 'address', 'added_by', 'added_at', 'updated_at')
    search_fields = ('address',)
    list_filter = ('address', 'added_by')


# Model Admin for StoreVendor
class StoreVendorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'logo', 'website', 'address', 'added_by', 'added_at',)
    search_fields = ('store',)
    list_filter = ('store',)


# Registering Vendor model
admin.site.register(Vendor, VendorAdmin)
admin.site.register(StoreVendor, StoreVendorAdmin)
