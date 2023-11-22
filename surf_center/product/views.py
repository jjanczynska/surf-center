from django.shortcuts import render
from .models import Category, Product, Service, LessonSchedule
from datetime import date

def all_products(request):
    """ A view to show all the products """
    products = Product.objects.all()
    services = Service.objects.filter(category__name="Lessons")
    lesson_schedules = LessonSchedule.objects.filter(date__gte=date.today(), is_available=True)

    context = {
        'products' : products,
        'services' : services,
        'lesson_schedules' : lesson_schedules
    }

    return render(request, 'products-services/products.html', context)


def lesson_detail(request, lesson_id):
    """ A view to show individual lesson details """
    lesson = get_object_or_404(Service, pk=lesson_id)
    available_slots = LessonSchedule.objects.filter(service=lesson.type, date__gte=date.today(), is_available=True)

    context = {
        'lesson': lesson,
        'available_slots': available_slots,
    }

    return render(request, 'products-services/lessons.html', context)


def surfing_equipment(request):
    """ A view to show all surfing equipment products """

    products = Product.objects.filter(category__name='Surfing Equipment')
    context = {
        'products' : products,
    }

    return render(request, 'products-services/surfing-equipment.html', context)

def lessons(request):
    """ A view to show all services categorised as lessons """

    services = Service.objects.filter(category__name='Lessons')
    no_lessons_available = False
    all_lessons_booked = False

    if not services:
        no_lessons_available = True
    elif all([service.booked for service in services]):
        all_lessons_booked = True

    context = {
        'services' : services,
        'no_lessons_available': no_lessons_available,
        'all_lessons_booked': all_lessons_booked,
    }

    return render(request, 'products-services/lessons.html', context)

def special_offers(request):
    """ A view to show products and services in specil offers """

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
        'product_offers'
        'service_offers': service_offers
    }

    return render(request, 'products-services/special-offers.html', context)
