from cloudinary.models import CloudinaryField
from django.contrib import admin
from django.db import models

# __________________________________@mit__________________________________
# Store Category Model
from django.utils.html import format_html


class StoreCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    image = CloudinaryField('image', overwrite=True, folder="store/category", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Property for image url
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

    # Property for getting store category object to dictionary data
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image_url,
            'is_active': self.is_active
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Store Category'
        verbose_name_plural = 'Store Categories'


# __________________________________@mit__________________________________
# Store Model
class Store(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    phone = models.CharField(max_length=10, null=False, blank=False, unique=True)
    email = models.CharField(max_length=255, null=False, blank=False, unique=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)
    gstin = models.CharField(max_length=255, null=False, blank=False, unique=True)
    logo = CloudinaryField('image', overwrite=True, folder="store/logo", null=True, blank=True)
    category = models.ForeignKey('store.StoreCategory', on_delete=models.PROTECT, related_name='stores')
    address = models.OneToOneField('common.Address', on_delete=models.PROTECT, related_name='stores')
    # subscription = models.OneToOneField('common.Subscription', on_delete=models.PROTECT,
    # related_name='stores',)    # Will be added later if necessary
    is_active = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
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

    # Property for getting store object to dictionary data
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tagline': self.tagline,
            'phone': self.phone,
            'email': self.email,
            'logo': self.image_url,
            'category': self.category.as_dict,
            'address': self.address.as_dict,
            'gstin': self.gstin,
            'is_active': self.is_active,
            'created_at': self.joined_at,
            'updated_at': self.updated_at
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'


# __________________________________@mit__________________________________
# Store Staff Model
class StoreStaff(models.Model):
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='staffs')
    user = models.OneToOneField('authentication.CasperUser', on_delete=models.CASCADE, related_name='staff')
    image = CloudinaryField('image', overwrite=True, folder="store/staff", null=True, blank=True)
    position = models.CharField(max_length=120, null=False, blank=False, default='Unspecified')
    updated_at = models.DateTimeField(auto_now=True)

    # Property for admin
    @property
    def is_admin(self):
        return self.user.is_store_admin

    # Property for staff
    @property
    def is_staff(self):
        return self.user.is_staff

    # Property for full name
    @property
    def full_name(self):
        return self.user.full_name

    # Property for email
    @property
    def email(self):
        return self.user.email

    # Property for phone
    @property
    def phone(self):
        return self.user.phone

        # Required for Permissions

    @property
    def permission(self):
        return self.permissions

    # Property for as_dict
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.email,
            'phone': self.phone,
            'image': self.image_url,
            'position': self.position,
            'is_admin': self.is_admin,
            'is_staff': self.is_staff,
            'is_active': self.user.is_active,
            'added_at': self.user.joined_at,
            'permissions': self.permission.as_dict,
        }

    # Property for image url
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

    class Meta:
        verbose_name = 'Store Staff'
        verbose_name_plural = 'Store Staffs'

    def __str__(self):
        return '%s (%s)' % (self.user.first_name, 'admin' if self.is_admin else self.position or 'staff')


# -------------------------------@mit--------------------------------
# Permission Model
class StaffPermission(models.Model):
    staff = models.OneToOneField('store.StoreStaff', on_delete=models.CASCADE, related_name='permissions')
    # catalogue related permissions
    manage_catalogues = models.BooleanField(default=False)
    # store related permissions
    manage_stores = models.BooleanField(default=False)
    # vendor related permissions
    manage_vendors = models.BooleanField(default=False)
    # customer related permissions
    manage_customers = models.BooleanField(default=False)
    # order related permissions
    manage_orders = models.BooleanField(default=False)
    # report related permissions
    manage_reports = models.BooleanField(default=False)
    # staff related permissions
    manage_staffs = models.BooleanField(default=False)
    # settings related permissions
    manage_settings = models.BooleanField(default=False)

    # property for has catalogue permissions
    @property
    def has_catalogue_permissions(self):
        return self.manage_catalogues

    # property for has store permissions
    @property
    def has_store_permissions(self):
        return self.manage_stores

    # property for has vendor permissions
    @property
    def has_vendor_permissions(self):
        return self.manage_vendors

    # property for has customer permissions
    @property
    def has_customer_permissions(self):
        return self.manage_customers

    # property for has order permissions
    @property
    def has_order_permissions(self):
        return self.manage_orders

    # property for has report permissions
    @property
    def has_report_permissions(self):
        return self.manage_reports

    # property for has user permissions
    @property
    def has_staff_permissions(self):
        return self.manage_staffs

    # property for has settings permissions
    @property
    def has_settings_permissions(self):
        return self.manage_settings

    # property for store name
    @property
    def store_name(self):
        return self.staff.store.name

    # Meta class
    class Meta:
        verbose_name = 'Staff Permission'
        verbose_name_plural = 'Staff Permissions'

    # property for dictionary
    @property
    def as_dict(self):
        return {
            'manage_catalogues': self.has_catalogue_permissions,
            'manage_stores': self.has_store_permissions,
            'manage_vendors': self.has_vendor_permissions,
            'manage_customers': self.has_customer_permissions,
            'manage_orders': self.has_order_permissions,
            'manage_reports': self.has_report_permissions,
            'manage_users': self.has_staff_permissions,
            'manage_settings': self.has_settings_permissions
        }

    def __str__(self):
        if self.staff:
            return self.staff.user.full_name
        else:
            return 'StaffPermission'
