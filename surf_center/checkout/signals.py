from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Order, ProductsLineItem, LessonLineItem

@receiver(post_save, sender=ProductsLineItem)
def update_order_on_product_save(sender, instance, created, **kwargs):
    """
    Update order total on Productlineitem update/create
    """
    instance.order.update_total()

@receiver(post_delete, sender=ProductsLineItem)
def update_order_on_product_delete(sender, instance, **kwargs):
     """
    Update order total on Productlineitem delete
    """
    instance.order.update_total()

@receiver(post_save, sender=LessonLineItem)
def update_order_on_lesson_save(sender, instance, created, **kwargs):
    """
    Update order total on Lessonlineitem update/create
    """
    instance.order.update_total()

@receiver(post_delete, sender=LessonLineItem)
def update_order_on__lesson_save(sender, instance, **kwargs):
     """
    Update order total on Lessonlineitem delete
    """
    instance.order.update_total()