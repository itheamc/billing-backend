from django.urls import path
from api.v1.store import views

urlpatterns = [
    path('', views.get_store, name='get_store'),
    path('list', views.get_stores, name='get_stores'),
    path('register_store', views.register_store, name='register_store'),
    path('add_staff', views.add_staff, name='add_staff'),
    path('login', views.store_login, name='store_login'),
]