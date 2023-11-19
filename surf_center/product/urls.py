from django.urls import path
from .import views

urlpatterns = [
    path('', views.all_products, name='all_products'),
    path('surfing-equipment/', views.surfing_equipment, name='surfing_equipment'),
    path('lessons/', views.lessons, name='lessons'),
    path('special-offers/', views.special_offers, name='special_offers'),
]