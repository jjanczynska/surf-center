from django.db import models
from django.conf import settings
import datetime

# Create your models here.

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=254)
    display_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.display_name

class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    is_special_offer = models.BooleanField(default=False, verbose_name="Special Offer")

    def __str__(self):
        return self.name

class Service(models.Model):
    
    PRIVATE = 'Private'
    GROUP = 'Group'
    LESSON_TYPES = [
        (PRIVATE, 'Private Lesson'),
        (GROUP, 'Group Lesson'),
    ]

    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=10, choices=LESSON_TYPES, default=GROUP)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    max_participants = models.PositiveIntegerField(default=1)
    description = models.TextField()
    is_special_offer = models.BooleanField(default=False, verbose_name="Special Offer")

    def save(self, *args, **kwargs):
        super(Service, self).save(*args, **kwargs)
    
    @property
    def price_per_participant(self):
        return 30.00 if self.type == self.PRIVATE else 15.00

    @property
    def max_participants(self):
        return 1 if self.type == self.PRIVATE else 5

class LessonSchedule(models.Model):
    TIME_SLOTS = [
        ('09:30', '9:30 AM'),
        ('11:00', '11:00 AM'),
        ('13:00', '1:00 PM'),
        ('14:30', '2:30 PM'),
        ('16:00', '4:00 PM'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=5, choices=TIME_SLOTS)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.service.get_type_display()} Lesson on {self.date} at {self.get_time_slot_display()}"