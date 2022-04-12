from django.urls import path
from api.v1.vendor import views

urlpatterns = [
    path('', views.vendors, name='vendors'),
    path('add_vendor', views.add_vendor, name='add_vendor'),
]