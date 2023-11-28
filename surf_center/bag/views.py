from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse
from product.models import Product, Service, LessonSchedule
from django.contrib import messages
import datetime

# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id, item_type):

    bag = request.session.get('bag', {'products': {}, 'lessons': {}})
    redirect_url = request.POST.get('redirect_url')
    size = request.POST.get('product_size', None)
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, pk=item_id)

    if product.has_sizes:
        size = request.POST.get('product_size')  
    else:
        size = None 

    if item_type == 'product':
        if size:
            if item_id in bag['products']:
                if isinstance(bag['products'][item_id], dict):
                    bag['products'][item_id]['items_by_size'][size] = bag['products'][item_id]['items_by_size'].get(size, 0) + quantity
                else:
                    bag['products'][item_id] = {'items_by_size': {size: quantity}}
            else:
                bag['products'][item_id] = {'items_by_size': {size: quantity}}
        else:
            bag['products'][item_id] = bag['products'].get(item_id, 0) + quantity
             messages.success(request, f'Added {product.name} to your bag')
  

    elif item_type == 'lesson':
        quantity = int(request.POST.get('quantity', 1))
        lesson = get_object_or_404(Service, pk=item_id)
        selected_date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')

        if not selected_date or not selected_time_slot:
            messages.error(request, "You must include a date and time for lessons.")
            return redirect(redirect_url)
        
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


def update_bag(request, item_id, item_type):
    """Update the quantity of the specified product"""

    bag = request.session.get('bag', {'products': {}, 'lessons': {}})
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']

    if item_type == 'product':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=item_id)

        if size:
            if quantity > 0:
                    bag['products'][item_id]['items_by_size'] = {size: quantity}
            else:
                del bag['products'][item_id]['items_by_size'][size]
        else:
            if quantity > 0:
                    bag['products'][item_id] = quantity
            else:
                bag['products'].pop[item_id]
                 

    elif item_type == 'lesson':
        quantity = int(request.POST.get('quantity', 1))
        lesson = get_object_or_404(Service, pk=item_id)
        selected_date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')

        lesson_key = f"{selected_date}_{selected_time_slot}"
        if lesson_key not in bag['lessons']:
            bag['lessons'][lesson_key]['quantity'] = quantity
            bag['lessons'][lesson_key]['details']['total_price'] = quantity * lesson.price_per_participant
        else:
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
    return redirect(reverse('view_bag'))

def remove_from_bag(request, item_id):
    """Remove the specified product or lesson from the shopping bag"""

    try:
        bag = request.session.get('bag', {'products': {}, 'lessons': {}})
        item_type = request.POST.get('item_type')

        if item_type == 'product':
            size = request.POST.get('product_size', None)
            product = get_object_or_404(Product, pk=item_id)

            if size:
                del bag['products'][item_id]['items_by_size'][size]
                if not bag['products'][item_id]['items_by_size']:
                    del bag['products'][item_id]
            else:
                del bag['products'][item_id]

        elif item_type == 'lesson':
            lesson = get_object_or_404(Service, pk=item_id)
            selected_date = request.POST.get('date', None)
            selected_time_slot = request.POST.get('time_slot', None)
            lesson_key = f"{selected_date}_{selected_time_slot}"
            del bag['lessons'][lesson_key]

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(status=500)

