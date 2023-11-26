from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add/<str:item_id>/<str:item_type>/', views.add_to_bag, name='add_to_bag'),
]