from rest_framework import serializers

from common.serializers import AddressSerializer
from .models import Vendor, StoreVendor


# -----------------------------------@mit-----------------------------------
# Vendor Serializers
class VendorSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Vendor
        fields = ('id', 'name', 'phone', 'email', 'image_url', 'website', 'address',)


# -----------------------------------@mit-----------------------------------
# StoreVendor Serializers
class StoreVendorSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()
    vendor = VendorSerializer(read_only=True)
    added_by = serializers.StringRelatedField()

    class Meta:
        model = StoreVendor
        fields = ('id', 'store', 'vendor', 'added_by',)
