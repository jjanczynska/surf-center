from django.contrib import admin
from django.urls import path
from . import views
from home.views import index

urlpatterns = [
    path('', index, name='home'),
   
]
