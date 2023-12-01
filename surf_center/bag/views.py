from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse
from product.models import Product, Service, LessonSchedule
from django.contrib import messages
from .contexts import bag_contents
import datetime



# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """
    context = bag_contents(request)
    bag = request.session.get('bag', {'products': {}, 'lessons': {}})
    return render(request, 'bag/bag.html', context)


def add_to_bag(request, item_id, item_type):

    bag = request.session.get('bag', {'products': {}, 'lessons': {}})
    redirect_url = request.POST.get('redirect_url')
    size = request.POST.get('product_size', None)
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, pk=item_id)

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

        booked_count = LessonSchedule.objects.filter(service=lesson, date=selected_date, time_slot=selected_time_slot).count()
        if booked_count >= lesson.max_participants:
            messages.error(request, f'Sorry, the selected lesson slot is fully booked.')
            return redirect(redirect_url)
        
        if LessonSchedule.objects.filter(date=selected_date, time_slot=selected_time_slot, is_booked=True).exists():
            messages.error(request, "Sorry, but this time slot is already booked.")
            return redirect(redirect_url)
        

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
            messages.success(request, f'Added {item_type} to your bag')


    request.session['bag'] = bag
    print(request.session['bag'])
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
                    messages.success(request, f'Updated {product.name} (Size: {size}) quantity to {quantity} in your bag')
            else:
                del bag['products'][item_id]['items_by_size'][size]
                messages.success(request, f'Removed {product.name} (Size: {size}) from your bag')
        else:
            if quantity > 0:
                    bag['products'][item_id] = quantity
                    messages.success(request, f'Updated {product.name} quantity to {quantity} in your bag')
            else:
                bag['products'].pop[item_id]
                messages.success(request, f'Removed {product.name} from your bag')
                 

    elif item_type == 'lesson':
        quantity = int(request.POST.get('quantity', 1))
        lesson = get_object_or_404(Service, pk=item_id)
        selected_date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')

        print("POST data - Quantity:", quantity, "Date:", selected_date, "Time Slot:", selected_time_slot)

        if not selected_date or not selected_time_slot:
             return redirect(reverse('view_bag'))

        lesson_key = f"{selected_date}_{selected_time_slot}"
        print(f"Lesson key for update: {lesson_key}")
        print(f"Lesson keys available in bag: {list(bag['lessons'].keys())}")

        if lesson_key in bag['lessons']:
            bag['lessons'][lesson_key]['quantity'] = quantity
            bag['lessons'][lesson_key]['details']['total_price'] = quantity * lesson.price_per_participant
            messages.success(request, f'Updated {item_type} on {selected_date} at {selected_time_slot} to {quantity} participants')
        else:
            messages.error(request, "Lesson time slot not found in your bag")   
            print(f"Lesson keys available in bag: {list(bag['lessons'].keys())}")
        
    print("Bag after update:", bag)    
    request.session['bag'] = bag
    print(f"Bag after update: {bag}")
    return redirect(reverse('view_bag'))

def remove_from_bag(request, item_id):
    """Remove the specified product or lesson from the shopping bag"""

    try:
        bag = request.session.get('bag', {'products': {}, 'lessons': {}})
        item_type = request.POST.get('item_type')

        print(f"Attempting to remove {item_type} with ID {item_id} from bag")
        print(f"POST Data: {request.POST}")


        if item_type == 'product':
            size = request.POST.get('product_size', None)
            product = get_object_or_404(Product, pk=item_id)

            if size:
                del bag['products'][item_id]['items_by_size'][size]
                if not bag['products'][item_id]['items_by_size']:
                    del bag['products'][item_id]
                messages.success(request, f'Removed {product.name} (Size: {size}) from your bag')
            else:
                del bag['products'][item_id]
                messages.success(request, f'Removed {product.name} from your bag')

        elif item_type == 'lesson':
            lesson = get_object_or_404(Service, pk=item_id)
            selected_date = request.POST.get('date', None)
            selected_time_slot = request.POST.get('time_slot', None)
            lesson_key = f"{selected_date}_{selected_time_slot}"
            del bag['lessons'][lesson_key]
            messages.success(request, f'Removed {lesson.get_type_display} lesson on {selected_date} at {selected_time_slot} from your bag')

            if not selected_date or not selected_time_slot:
                messages.error(request, "Invalid lesson date or time slot.")
                return HttpResponse("Invalid lesson date or time slot.", status=400)

            lesson_key = f"{selected_date}_{selected_time_slot}"

            if lesson_key in bag['lessons']:
                del bag['lessons'][lesson_key]
                messages.success(request, f'Removed {lesson.get_type_display} lesson on {selected_date} at {selected_time_slot} from your bag')
            else:
                messages.error(request, "Lesson time slot not found in your bag.")
                return HttpResponse(status=404)

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        print(f"Error removing item from bag: {e}")
        return HttpResponse(status=500)

