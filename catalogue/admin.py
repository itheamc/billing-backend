from django.contrib import admin
from .models import *


# ModelAdmin for the ProductCategory model
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'store_category', 'created_at', 'updated_at',)
    list_filter = ('store_category', 'created_at',)
    search_fields = ('name', 'store_category',)
    ordering = ('-created_at',)


# ModelAdmin for the Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'description', 'category', 'store', 'vendor', 'sku', 'is_active', 'tags',)
    list_filter = ('store', 'vendor', 'category',)
    search_fields = ('name', 'category', 'store', 'vendor',)
    ordering = ('-created_at',)


# ModelAdmin for the Variant model
class VariantAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product', 'cost_price', 'mrp', 'selling_price', 'tax', 'quantity', 'sku',
        'is_active',)
    list_filter = ('product', 'is_active',)
    search_fields = ('product', 'sku',)
    ordering = ('-created_at',)


# ModelAdmin for the Attribute model
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant', 'name', 'value', 'unit',)
    list_filter = ('name', 'variant',)
    search_fields = ('name', 'value', 'variant',)


# ModelAdmin for the ProductTax model
class ProductTaxAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant', 'cgst', 'sgst', 'igst', 'other',)
    list_filter = ('id',)
    search_fields = ('id',)


# ModelAdmin for the ProductMedia model
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_icon', 'image_of', 'uploaded_at', 're_uploaded_at',)
    list_filter = ('id',)
    search_fields = ('id',)


# Registering the models
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(ProductTax, ProductTaxAdmin)
admin.site.register(ProductMedia, ProductMediaAdmin)
