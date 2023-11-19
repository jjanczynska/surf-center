from django.contrib import admin
from .models import Category, Product, Service

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )

    ordering = ('sku',)

class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'type',
        'time_slots',
        'date',
        'max_participants',
        'booked',
    )

    list_filter = ('type', 'date', 'booked',)
    search_fields = ('category__name', 'date',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'name',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)
