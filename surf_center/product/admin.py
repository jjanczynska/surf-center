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
        'get_type_display',
        'price',
        'date',
        'booked',
        'image',
    )
    ordering = (
        'date',
        'type',
    )
    list_filter = (
        'type', 
        'date',
        'booked',
        )
    search_fields = (
        'category__name', 
        'date',
        )
    def get_type_display(self, obj):
        return obj.get_type_display()
    get_type_display.short_description = 'Type of Lesson'

    

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'name',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)
