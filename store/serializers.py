from rest_framework import serializers

from common.serializers import AddressSerializer
from store.models import StoreCategory, Store


# -----------------------------------@mit-----------------------------------
# StoreCategory Serializer
class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCategory
        fields = ('id', 'name', 'image_url', 'is_active')


# -----------------------------------@mit-----------------------------------
# Store Serializer
class StoreSerializer(serializers.ModelSerializer):
    category = StoreCategorySerializer(read_only=True)
    address = AddressSerializer()

    class Meta:
        model = Store
        fields = ('id', 'name', 'tagline', 'phone', 'email', 'image_url', 'gstin', 'is_active', 'category', 'address',)
        extra_kwargs = {'image_url': {'read_only': True}}


# -----------------------------------@mit-----------------------------------
# Store Staff Serializer
class StoreStaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()
    user = serializers.StringRelatedField()

    class Meta:
        model = Store
        fields = ('id', 'store', 'user')
