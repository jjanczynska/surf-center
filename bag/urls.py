from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path(
        'add/<str:item_id>/<str:item_type>/',
        views.add_to_bag,
        name='add_to_bag'
    ),
    path(
        'update/<str:item_id>/<str:item_type>',
        views.update_bag,
        name='update_bag'
    ),
    path(
        'remove/<str:item_id>/',
        views.remove_from_bag,
        name='remove_from_bag'
    ),
]
