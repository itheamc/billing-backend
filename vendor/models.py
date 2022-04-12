from cloudinary.models import CloudinaryField
from django.contrib import admin
from django.db import models
from django.utils.html import format_html


# __________________________________@mit__________________________________
# Vendor model
class Vendor(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    phone = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    logo = CloudinaryField('image', overwrite=True, folder="vendors/logo", null=True, blank=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    address = models.OneToOneField('common.Address', on_delete=models.PROTECT, related_name='vendor')
    added_by = models.ForeignKey('store.StoreStaff', on_delete=models.PROTECT, related_name='vendor_added_by')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Property for image url
    @property
    def image_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        else:
            return None

    # Display image icon
    @admin.display
    def image_icon(self):
        return format_html('<img src="%s" style="width:36px;height:36px;object-fit: cover;"/>' % self.image_url)

    # Property for dictionary
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'logo': self.image_url,
            'website': self.website,
            'address': self.address.as_dict,
            'added_by': {
                'store': self.added_by.store.name,
            },
        }

    def __str__(self):
        return self.name


# __________________________________@mit__________________________________
# Store Vendor model
class StoreVendor(models.Model):
    store = models.ForeignKey('store.Store', on_delete=models.PROTECT, related_name='vendors')
    vendor = models.ForeignKey('Vendor', on_delete=models.PROTECT, related_name='store_vendors')
    added_by = models.ForeignKey('store.StoreStaff', on_delete=models.PROTECT, related_name='store_vendor_added_by')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Property for vendor name
    @property
    def name(self):
        return self.vendor.name

    # Property for vendor logo
    @property
    def logo(self):
        return self.vendor.logo

    # Property for vendor website
    @property
    def website(self):
        return self.vendor.website

    # Property for vendor address
    @property
    def address(self):
        return self.vendor.address

    # Property for vendor phone
    @property
    def phone(self):
        return self.vendor.phone

    # Property for vendor email
    @property
    def email(self):
        return self.vendor.email

    # Property for dictionary
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
            'website': self.website,
            'address': self.address.as_dict,
            'phone': self.phone,
            'email': self.email,
            'created_by': {
                'store': self.vendor.added_by.store.name,
                'added_at': self.vendor.added_at.strftime('%d-%m-%Y %H:%M:%S'),
            },
            'added_by': {
                'name': self.added_by.full_name,
                'added_at': self.added_at.strftime('%d-%m-%Y %H:%M:%S'),
            }
        }

    def __str__(self):
        return self.vendor.name

    class Meta:
        verbose_name = 'Store Vendor'
        verbose_name_plural = "Store Vendors"
