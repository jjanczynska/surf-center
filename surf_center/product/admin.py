from django.contrib import admin
from .models import Category, Product, Service, LessonSchedule

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
        'is_special_offer',
    )

    ordering = ('sku',)

    list_filter = ('category', 'is_special_offer',)

class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'get_type_display',
        'price',
        'max_participants',
        'is_special_offer',
        'image',
    )

    list_filter = ('type', 'is_special_offer',)

    search_fields = ('category__name',)

    def get_type_display(self, obj):
        return obj.get_type_display()
    get_type_display.short_description = 'Type of Lesson'

class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = ('service', 'date', 'time_slot', 'is_available')
    list_filter = ('date', 'service__type','is_available' )
    search_fields = ('service__name', 'date',)
    actions = ['mark_unavailable', 'mark_available']

    def mark_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    mark_unavailable.short_description = "Mark selected schedules as unavailable"

    def mark_available(self, request, queryset):
        queryset.update(is_available=True)
    mark_available.short_description = "Mark selected schedules as available"

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'name',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(LessonSchedule, LessonScheduleAdmin)
