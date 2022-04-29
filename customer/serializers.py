from rest_framework import serializers
from .models import Customer


# -----------------------------------@mit-----------------------------------
# Serializer for Customer model
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'phone', 'email', 'address')
