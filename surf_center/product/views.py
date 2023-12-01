from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Category, Product, Service, LessonSchedule
from django.contrib import messages
from datetime import date
from django.db.models.functions import Lower, Coalesce
from django.db.models import Q
from django.db.models import Value, IntegerField

from .forms import ProductForm


def all_products(request):
    """ A view to show all the products """
    products = Product.objects.all()
    services = Service.objects.filter(
        Q(category__name="private_lesson") | Q(category__name="group_lesson")
    )

    lesson_schedules = LessonSchedule.objects.filter(date__gte=date.today(), is_booked=False)

    all_categories = Category.objects.all()

    query = request.GET.get('q', '')
    categories = request.GET.get('category', '').split(',') if 'category' in request.GET else []
    sort = request.GET.get('sort', 'id')
    direction = request.GET.get('direction', 'asc')
    current_sorting = f'{sort}_{direction}'

    if sort == 'reset':
        products = products.order_by('id')
        services = services.order_by('id')
        current_sorting = 'None_None'
    elif sort:
        sortkey, direction = sort.split('_') if '_' in sort else (sort, 'asc')
        descending = '-' if direction == 'desc' else ''

    if query:
        search_query = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(search_query)
        services = services.filter(search_query)

    if categories:
        products = products.filter(category__name__in=categories)
        services = services.filter(category__name__in=categories)

    descending = '-' if direction == 'desc' else ''
    if sort in ['price', 'rating', 'name', 'category']:
        if sort == 'price':
            products = products.order_by(f'{descending}price')
            services = services.order_by(f'{descending}price')
        elif sort == 'rating':
            products = products.order_by(f'{descending}rating')
            # Services don't have ratings, use a default value
            services = services.annotate(rating=Value(0, output_field=IntegerField())).order_by(f'{descending}rating')
        elif sort == 'name':
            products = products.annotate(lower_name=Lower('name')).order_by(f'{descending}lower_name')
            services = services.annotate(lower_get_type_display=Lower('type')).order_by(f'{descending}lower_get_type_display')
        elif sort == 'category':
            products = products.order_by(f'{descending}category__name')
            services = services.order_by(f'{descending}category__name')


    context = {
        'products' : products,
        'services' : services,
        'lesson_schedules' : lesson_schedules,
        'search_term': query,
        'all_categories': all_categories,
        'current_sorting': current_sorting,
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

    categories = None
    sort = None
    direction = None

    if 'sort' in request.GET:
        sortkey = request.GET['sort']
        sort = sortkey
        direction = request.GET['direction'] if 'direction' in request.GET else 'asc'

        if sortkey == 'name':
            sortkey = 'lower_name'
            products = products.annotate(lower_name=Lower('name'))

        sortkey = f'-{sortkey}' if direction == 'desc' else sortkey
        products = products.order_by(sortkey)

    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

    context = {
        'products' : products,
        'current_categories': categories,
        'current_sorting' : f'{sort}_{direction}'
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
    no_lessons_available = services.count() == 0
    all_lessons_booked = LessonSchedule.objects.filter(
        service__in=services, 
        date__gte=date.today(), 
        is_booked=False
    ).exists()

    sort = None
    direction = None
    categories = None

    if 'sort' in request.GET:
        sortkey = request.GET['sort']
        sort = sortkeydirection = request.GET['direction'] if 'direction' in request.GET else 'asc'

        sortkey = f'-{sortkey}' if direction == 'desc' else sortkey
        services = services.order_by(sortkey)

    if 'category' in request.GET:
        categories = request.GET['category'].split(',')
        services = Service.objects.filter(category__name__in=categories)

    for service in services:
        lesson_schedules = LessonSchedule.objects.filter(service=service, date__gte=date.today(), is_booked=False)
        if lesson_schedules.exists():
            all_lessons_booked = False
            break

    if not services:
        no_lessons_available = True


    context = {
        'services' : services,
        'no_lessons_available': no_lessons_available,
        'all_lessons_booked': all_lessons_booked,
        'current_categories': categories,
        'current_sorting': f'{sort}_{direction}',
    }

    return render(request, 'products-services/lessons.html', context)

def lesson_detail(request, lesson_id):
    """ A view to show individual lesson details """
    lesson = get_object_or_404(Service, pk=lesson_id)
    available_slots = LessonSchedule.objects.filter(
        service=lesson, 
        date__gte=date.today(), 
        is_booked=False
        ).order_by('date', 'time_slot')

    context = {
        'lesson': lesson,
        'available_slots': available_slots,
    }

    return render(request, 'products-services/lessons-detail.html', context)

def special_offers(request):
    """ A view to show products and services in special offers """

    service_offers = Service.objects.filter(is_special_offer=True)
    product_offers = Product.objects.filter(is_special_offer=True)

    context = {
        'secondhand': secondhand,
        'product_offers': product_offers,
        'service_offers': service_offers,
    }

    return render(request, 'products-services/special-offers.html', context)

def add_product(request):
    """ Add a product to the store """
    form = ProductForm()
    template = 'products-services/add-product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)
