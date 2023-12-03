from django.urls import path
from .import views

urlpatterns = [
    path('', views.all_products, name='all_products'),
    path('surfing-equipment/', views.surfing_equipment, name='surfing_equipment'),
    path('lessons/', views.lessons, name='lessons'),
    path('special-offers/', views.special_offers, name='special_offers'),
    path('lessons-detail/<int:lesson_id>/', views.lesson_detail, name='lessons_detail'),
    path('surfing-equipment-detail/<int:product_id>', views.surfing_equipment_detail, name='surfing_equipment_detail'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
]