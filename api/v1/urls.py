from django.urls import path, include
from .store import urls as store_urls
from .catalogue import urls as catalogue_urls
from .vendor import urls as vendor_urls

urlpatterns = [
    path('store/', include(store_urls)),
    path('catalogue/', include(catalogue_urls)),
    path('vendor/', include(vendor_urls)),
]
