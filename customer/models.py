from django.db import models


# -----------------------------------@mit-----------------------------------
# Customer model
class Customer(models.Model):
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(max_length=180, null=True, blank=True)
    address = models.CharField(max_length=240, null=True, blank=True)
    added_by = models.ForeignKey('store.StoreStaff', on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # property to return the dict of the customer
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'added_by': self.added_by.as_dict if self.added_by else None,
            'added_on': self.added_at,
            'updated_on': self.updated_at
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
