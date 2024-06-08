import uuid
from django_countries.fields import CountryField

from django.db import models
from django.db.models import Sum
from django.conf import settings

from product.models import Product, Service, LessonSchedule
from profiles.models import UserProfile

# Create your models here.


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country', null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0
    )
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    original_bag = models.TextField(
        null=False, blank=False, default=''
    )
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default=''
    )

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        print("Updating order total...")
        product_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        lesson_total = self.lessonitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        self.order_total = product_total + lesson_total
        self.grand_total = self.order_total + (self.delivery_cost or 0)
        print(f"Order Total: {self.order_total}, Delivery Cost: {self.delivery_cost}, Grand Total: {self.grand_total}")
        self.save()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class ProductsLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='lineitems'
    )
    product = models.ForeignKey(
        Product,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False
    )

    def save(self, *args, **kwargs):
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total()
        print(f"Product Line Item Total: {self.lineitem_total}, Quantity: {self.quantity}, Product Price: {self.product.price}")

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'


class LessonLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='lessonitems'
    )
    service = models.ForeignKey(
        Service,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(null=False, blank=False, default=0)
    date = models.DateField(null=False, blank=False)
    time_slot = models.CharField(
        max_length=5,
        choices=LessonSchedule.TIME_SLOTS
    )
    lineitem_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False
    )

    def save(self, *args, **kwargs):
        self.lineitem_total = (
             self.service.price_per_participant * self.quantity
        )
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f'{self.service.type} lesson on {self.date} at {self.time_slot}'
