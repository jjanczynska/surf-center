from django.db import models
from django.conf import settings
import datetime

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=254)
    display_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.display_name

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    
    PRIVATE = 'Private'
    GROUP = 'Group'
    LESSON_TYPES = [
        (PRIVATE, 'Private Lesson'),
        (GROUP, 'Group Lesson'),
    ]

    TIME_SLOTS = [
        ('10:00', '10:00 AM'),
        ('11:30', '11:30 AM'),
        ('13:30', '1:30 PM'),
        ('15:00', '3:00 PM'),
        ('16:30', '4:30 PM'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=10, choices=LESSON_TYPES, default=GROUP)
    time_slots = models.CharField(max_length=5, choices=TIME_SLOTS)
    date = models.DateField()
    max_participants = models.PositiveIntegerField(default=1)
    description = models.TextField()
    booked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.type == self.GROUP:
            self.max_participants = 5
        elif self.type == self.PRIVATE:
            self.max_participants = 1

        super(Service, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.get_type_display()} on {self.date} at {self.get_time_slot_display()}"

    def is_fully_booked(self):
        return self.booked

    def book_lesson(self):
        if not self.is_fully_booked():
            self.booked = True
            self.save()
            return True
        else:
            return False