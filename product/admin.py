from django.contrib import admin
from .models import Category, Product, Service, LessonSchedule, Subscriber


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
    list_display = ('date', 'time_slot', 'is_booked', 'service')
    list_filter = ('date', 'is_booked', 'service')
    search_fields = ('date', 'service__type')
    actions = ['mark_as_booked', 'mark_available']

    def mark_as_booked(self, request, queryset):
        queryset.update(is_abooked=True)
    mark_as_booked.short_description = "Mark selected schedules as booked"

    def mark_available(self, request, queryset):
        queryset.update(is_booked=False)
    mark_available.short_description = "Mark selected schedules as available"


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'name',
    )


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(LessonSchedule, LessonScheduleAdmin)
