from django.urls import path, include
from api.v1.catalogue import views

urlpatterns = [
    path('product/', include([
        # path('<int:id>', views.product, name='product'),
        path('add', views.add_product, name='add_product'),
        path('update/<int:id>', views.update_product, name='update_product'),
        path('delete/<int:id>', views.delete_product, name='delete_product'),
        path('list', views.product_list, name='product_list'),
        path('variant/', include([
            path('add', views.add_variant, name='add_variant'),
            path('update/<int:id>', views.update_variant, name='update_variant'),
            path('delete/<int:id>', views.delete_variant, name='delete_variant'),
            # path('<int:id>', views.variant, name='variant'),
            path('attribute/', include([
                path('add', views.add_attribute, name='add_attribute'),
                path('update/<int:id>', views.update_attribute, name='update_attribute'),
                path('delete/<int:id>', views.delete_attribute, name='delete_attribute'),
                # path('<int:id>', views.attribute, name='attribute'),
            ]))
        ])),
        path('media/', include([
            path('add', views.add_product_media, name='add_media'),
            path('delete/<int:id>', views.delete_product_media, name='delete_media'),
        ])),
    ])),
]
