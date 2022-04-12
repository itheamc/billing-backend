from django.contrib import admin

from .models import Address


# Model Admin for Address
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'pincode', 'latitude', 'longitude')
    list_filter = ('city', 'state')
    search_fields = ('city', 'state', 'country', 'pincode')


# Now register the new CasperUserAdmin...
admin.site.register(Address, AddressAdmin)
