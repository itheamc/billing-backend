from cloudinary.models import CloudinaryField
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.html import format_html


# ------------------------------------@mit------------------------------------
# Product Category Model
class ProductCategory(models.Model):
    name = models.CharField(max_length=120, unique=True, null=False, blank=False)
    store_category = models.ForeignKey('store.StoreCategory', on_delete=models.CASCADE, related_name='store_categories')
    description = models.TextField(null=True, blank=True)
    added_by = models.ForeignKey('store.Store', null=True, on_delete=models.SET_NULL, related_name='product_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


# ------------------------------------@mit------------------------------------
# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True, default="")
    category = models.ForeignKey('catalogue.ProductCategory', on_delete=models.PROTECT, related_name='products')
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='products')
    vendor = models.ForeignKey('vendor.StoreVendor', on_delete=models.PROTECT, related_name='products')
    sku = models.CharField(max_length=255, blank=False, null=False)
    tags = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    added_by = models.ForeignKey('store.StoreStaff', null=True, on_delete=models.SET_NULL, related_name='products')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


# ------------------------------------@mit------------------------------------
# Variant Model
class Variant(models.Model):
    product = models.ForeignKey('catalogue.Product', on_delete=models.CASCADE,
                                related_name='variants')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=255, blank=False, null=False)
    added_by = models.ForeignKey('store.StoreStaff', null=True, on_delete=models.SET_NULL, related_name='variants')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variants"

    def __str__(self):
        return self.sku


# ------------------------------------@mit------------------------------------
# Attribute Model
class Attribute(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    value = models.CharField(max_length=50, null=False, blank=False)
    unit = models.CharField(max_length=50, null=True, blank=True)
    variant = models.ForeignKey('catalogue.Variant', on_delete=models.CASCADE, related_name='attributes')

    class Meta:
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"

    def __str__(self):
        return self.name


# ------------------------------------@mit------------------------------------
# Product Media Model
class ProductMedia(models.Model):
    image = CloudinaryField('image', overwrite=True, folder="products", null=True, blank=True)
    product = models.ForeignKey('catalogue.Product', null=True, blank=True, default=None, on_delete=models.CASCADE,
                                related_name='media')
    variant = models.ForeignKey('catalogue.Variant', null=True, blank=True, default=None, on_delete=models.CASCADE,
                                related_name='media')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    re_uploaded_at = models.DateTimeField(auto_now=True)

    # property to return the image parent
    @property
    def image_of(self):
        return self.product.sku if self.product else self.variant.sku if self.variant else "No Product"

    # Property to get image url
    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return None

    # Display image icon
    @admin.display
    def image_icon(self):
        return format_html('<img src="%s" style="width:36px;height:36px;object-fit: cover;"/>' % self.image_url)

    # property for dict
    @property
    def as_dict(self):
        return {
            'image': self.image_url,
            'image_of': self.image_of,
            'uploaded_at': self.uploaded_at,
            're_uploaded_at': self.re_uploaded_at
        }

    def __str__(self):
        return self.image_of

    class Meta:
        verbose_name = "Product Media"
        verbose_name_plural = "Product Medias"


# ------------------------------------@mit------------------------------------
# Product Tax Model
# CGST -> Central Goods and Services Tax
# SGST -> State Goods and Services Tax
# IGST -> Integrated Goods and Services Tax
# UGST -> Union Goods and Services Tax
class ProductTax(models.Model):
    cgst = models.DecimalField(max_digits=5, decimal_places=2)
    sgst = models.DecimalField(max_digits=5, decimal_places=2)
    igst = models.DecimalField(max_digits=5, decimal_places=2)
    other = models.DecimalField(max_digits=5, decimal_places=2)
    variant = models.OneToOneField('catalogue.Variant', on_delete=models.CASCADE, related_name='tax')

    def __str__(self):
        return str(self.cgst) if self.cgst else str(self.sgst) if self.sgst else str(self.igst) if self.igst else str(
            self.other)

    class Meta:
        verbose_name = "Product Tax"
        verbose_name_plural = "Product Taxes"
