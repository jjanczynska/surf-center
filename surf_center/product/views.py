from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Service, LessonSchedule
from datetime import date
from django.db.models import Q

def all_products(request):
    """ A view to show all the products """
    products = Product.objects.all()
    services = Service.objects.filter(
        Q(category__name="private_lesson") | Q(category__name="group_lesson")
    )
    lesson_schedules = LessonSchedule.objects.filter(date__gte=date.today(), is_available=True)

    context = {
        'products' : products,
        'services' : services,
        'lesson_schedules' : lesson_schedules
    }

    return render(request, 'products-services/products.html', context)


def surfing_equipment(request):
    """ A view to show all surfing equipment products """

    products = Product.objects.filter(
        Q(category__name='surf_boards') |
        Q(category__name='water_boots') |
        Q(category__name='wetsuits') |
        Q(category__name='secondhand') |
        Q(category__name='water_ponchos') 
    )
    context = {
        'products' : products,
    }

    return render(request, 'products-services/surfing-equipment.html', context)


def surfing_equipment_detail(request, product_id):
    """ A view to show individual surfing equipent products details"""

    product = get_object_or_404(Product, pk=product_id)

    context = {'product': product}

    return render (request, 'products-services/surfing-equipment-detail.html', context)

def lessons(request):
    """ A view to show all services categorised as lessons """

    services = Service.objects.filter(
        Q(category__name='private_lesson') |
        Q(category__name='group_lesson') 
    )
    no_lessons_available = False
    all_lessons_booked = True

    for service in services:
        lesson_schedules = LessonSchedule.objects.filter(service=service, date__gte=date.today(), is_available=True)
        if lesson_schedules.exists():
            all_lessons_booked = False
            break

    if not services:
        no_lessons_available = True


    context = {
        'services' : services,
        'no_lessons_available': no_lessons_available,
        'all_lessons_booked': all_lessons_booked,
    }

    return render(request, 'products-services/lessons.html', context)

def lesson_detail(request, lesson_id):
    """ A view to show individual lesson details """
    lesson = get_object_or_404(Service, pk=lesson_id)
    available_slots = LessonSchedule.objects.filter(service=lesson, date__gte=date.today(), is_available=True)

    context = {
        'lesson': lesson,
        'available_slots': available_slots,
    }

    return render(request, 'products-services/lessons-detail.html', context)

def special_offers(request):
    """ A view to show products and services in special offers """

    new_arrivals = Product.objects.filter(description__icontains='New Arrival')
    deals = Product.objects.filter(description__icontains='Deal')
    clearance = Product.objects.filter(description__icontains='Clearance')
    secondhand = Product.objects.filter(description__icontains='Secondhand')
    service_offers = Service.objects.filter(is_special_offer=True)
    product_offers = Product.objects.filter(is_special_offer=True)

    context = {
        'new_arrivals': new_arrivals,
        'deals': deals,
        'clearance': clearance,
        'secondhand': secondhand,
        'product_offers': product_offers,
        'service_offers': service_offers,
    }

    return render(request, 'products-services/special-offers.html', context)
