from rest_framework import serializers
from catalogue.models import ProductCategory, Variant, Product, Attribute, ProductTax, ProductMedia
from vendor.serializers import VendorSerializer


# -------------------------------------@mit-------------------------------------
# ProductTax serializer
class ProductTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTax
        fields = ('id', 'cgst', 'sgst', 'igst', 'ugst')


# -------------------------------------@mit-------------------------------------
# Product Category Serializer
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'name',)


# -------------------------------------@mit-------------------------------------
# Attribute Serializer
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('id', 'name', 'value', 'unit')


# -------------------------------------@mit-------------------------------------
# Variant Serializer
class VariantSerializer(serializers.ModelSerializer):
    tax = ProductTaxSerializer(read_only=True)
    attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Variant
        fields = (
            'id', 'cost_price', 'mrp', 'selling_price', 'tax', 'quantity', 'sku', 'is_active',
            'attributes',)


# -------------------------------------@mit-------------------------------------
# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)
    variants = VariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'category', 'vendor', 'sku', 'is_active', 'tags', 'variants',)
        exclude = ('created_at', 'updated_at',)


# -------------------------------------@mit-------------------------------------
# ProductMedia Serializer
class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ('id', 'image', 'product', 'variant', 'image_url', 'uploaded_at', 're_uploaded_at',)
        extra_kwargs = {'uploaded_at': {'read_only': True}, 're_uploaded_at': {'read_only': True},
                        'image_url': {'read_only': True}, 'image': {'write_only': True}, 'product': {'read_only': True},
                        'variant': {'read_only': True}}
