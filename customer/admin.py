from django.contrib import admin
from .models import Customer


# Registering Customer model
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'store', 'address', 'added_at')
    list_filter = ('store',)
    search_fields = ('name', 'email', 'phone',)


admin.site.register(Customer, CustomerAdmin)
