from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from product.models import Product, Service, LessonSchedule
from decimal import Decimal
import datetime

# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id, item_type):

    bag = request.session.get('bag', {'products': {}, 'lessons': {}})
    redirect_url = request.POST.get('redirect_url')

    if item_type == 'product':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=item_id)

        if item_id in bag['products']:
            bag['products'][item_id] += quantity
        else:
            bag['products'][item_id] = quantity

    elif item_type == 'lesson':
        quantity = int(request.POST.get('quantity', 1))
        lesson = get_object_or_404(Service, pk=item_id)
        selected_date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')

    try:
            lesson_schedule = LessonSchedule.objects.get(
                service=lesson, 
                date=selected_date, 
                time_slot=selected_time_slot,
                is_available=True
            )

    except LessonSchedule.DoesNotExist:
        return HttpResponse("Selected time slot is not available", status=400)



        lesson_details = {
            'date': selected_date,
            'time_slot': selected_time_slot,
            'quantity': quantity,
            'total_price': Decimal(quantity) * lesson.price_per_participant()
        }

        lesson_key = f"{item_id}_{selected_date}_{selected_time_slot}"
        bag['lessons'][lesson_key] = lesson_details

    request.session['bag'] = bag
    return redirect(redirect_url)



