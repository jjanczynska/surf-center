from django.shortcuts import render
from .models import Category, Product, Service

def all_products(request):
    """ A view to show all the products """
    products = Product.objects.all()
    services = Service.objects.filter(category__name="Lessons")

    context = {
        'products' : products,
        'services' : services,
    }

    return render(request, 'products-services/products.html', context)

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

    service_offers = Service.object.filters(description__icontains='Special Offer')

    context = {
        'new_arrivals': new_arrivals,
        'deals': deals,
        'clearance': clearance,
        'secondhand': secondhand,
        'service_offers': service_offers
    }

    return render(request, 'products-services/special-offers.html', context)
