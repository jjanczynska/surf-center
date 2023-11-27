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

        if LessonSchedule.objects.filter(date=selected_date, time_slot=selected_time_slot, is_booked=True).exists():
            return HttpResponse("Sorry but this time slot is already booked", status=400)
        

        lesson_key = f"{selected_date}_{selected_time_slot}"
        if lesson_key not in bag['lessons']:
            bag['lessons'][lesson_key] = {
                'item_id': item_id,
                'quantity': quantity,
                'details': {
                    'date': selected_date,
                    'time_slot': selected_time_slot,
                    'total_price': quantity * lesson.price_per_participant
                }
            }
        
    request.session['bag'] = bag
    return redirect(redirect_url)



