from rest_framework import serializers
from .models import Address


# -----------------------------------@mit-----------------------------------
# Address Serializer
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
