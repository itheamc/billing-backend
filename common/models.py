from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


# __________________________________@mit__________________________________
# Address Model
class Address(models.Model):
    address_line_1 = models.CharField(max_length=500, blank=False, null=False)
    address_line_2 = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    pincode = models.BigIntegerField()
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, default=None)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, default=None)

    # Property for getting store address object to dictionary data
    @property
    def as_dict(self):
        return {
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'pincode': self.pincode,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'


# __________________________________@mit__________________________________
# Network Response Class
class NetworkResponse:
    def __init__(self, status=None, message=None, data=None):
        self.status = status
        self.message = message
        self.data = data

    def copy(self, status=None, message=None, data=None):
        if status is not None:
            self.status = status
        if message is not None:
            self.message = message
        if data is not None:
            self.data = data
        return self

    @property
    def as_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'data': self.data
        }
