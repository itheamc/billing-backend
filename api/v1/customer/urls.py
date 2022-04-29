from django.urls import path
from api.v1.customer import views

urlpatterns = [
    path('add_customer', views.add_customer, name='add_customer'),
    path('get_customers', views.get_customers, name='get_customers'),
]
