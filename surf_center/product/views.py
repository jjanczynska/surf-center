from django.shortcuts import render
from .models import Category, Product, Service

def all_products(request):
    """ A view to show all the products """
    products = Product.objects.all()

    context = {
        'products' : products,
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
    context = {
        'services' : services,
    }

    return render(request, 'products-services/lessons.html', context)

def special_offers(request):
    """ A view to show products and services in specil offers """

    new_arrivals = Product.objects.filter(description__icontains='New Arrival')
    deals = Product.objects.filter(description__icontains='Deal')
    clearance = Product.objects.filter(description__icontains='Clearance')
    secondhand = Product.objects.filter(description__icontains='Secondhand')

    context = {
        'new_arrivals': new_arrivals,
        'deals': deals,
        'clearance': clearance,
        'secondhand': secondhand,
    }

    return render(request, 'products-services/special-offers.html', context)
