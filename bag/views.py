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
                    items_by_size = bag['products'][item_id]['items_by_size']
                    current_quantity = items_by_size.get(size, 0)
                    updated_quantity = current_quantity + quantity
                    items_by_size[size] = updated_quantity

                else:
                    items_by_size = {size: quantity}
                    bag['products'][item_id] = {'items_by_size': items_by_size}
            else:
                bag['products'][item_id] = {'items_by_size': {size: quantity}}
        else:
            new_quantity = bag['products'].get(item_id, 0) + quantity
            bag['products'][item_id] = new_quantity
            messages.success(request, f'Added {product.name} to your bag')

    elif item_type == 'lesson':
        quantity = int(request.POST.get('quantity', 1))
        lesson = get_object_or_404(Service, pk=item_id)
        selected_date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')

        if lesson.type == Service.PRIVATE and quantity != 1:
            messages.error(
                request,
                f'Only one participant is allowed for private lessons.'
            )
            return redirect(redirect_url)

        is_valid_quantity = 2 <= quantity <= 5
        if lesson.type == Service.GROUP and not is_valid_quantity:
            message.error(
                request,
                f'Group lessons must have between 2 and 5 participants'
                )
            return redirect(redirect_url)

        if not selected_date or not selected_time_slot:
            messages.error(
                request,
                f'You must include a date and time for lessons.'
                )
            return redirect(redirect_url)

        booked_count = LessonSchedule.objects.filter(
            service=lesson,
            date=selected_date,
            time_slot=selected_time_slot
            ).count()
        if booked_count >= lesson.max_participants:
            messages.error(
                request,
                f'Sorry, the selected lesson slot is fully booked.'
                )
            return redirect(redirect_url)

        scheduled_lessons = LessonSchedule.objects.filter(
            date=selected_date,
            time_slot=selected_time_slot,
            is_booked=True
        )
        if scheduled_lessons.exists():
            messages.error(
                request,
                'Sorry, but this time slot is already booked.'
            )
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
    redirect_url = request.POST.get('redirect_url', reverse('view_bag'))

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
                success_message = (
                    f'Updated {product.name} (Size: {size}) '
                    f'quantity to {quantity} in your bag'
                )
                messages.success(request, success_message)

            else:
                del bag['products'][item_id]['items_by_size'][size]
                messages.success(
                    request,
                    f'Removed {product.name} (Size: {size}) from your bag'
                )
        else:
            if quantity > 0:
                bag['products'][item_id] = quantity
                messages.success(
                    request,
                    f'Updated {product.name}'
                    f'quantity to {quantity} in your bag'
                )
            else:
                bag['products'].pop[item_id]
                messages.success(
                    request,
                    f'Removed {product.name} from your bag'
                    )

    elif item_type == 'lesson':
        quantity = int(request.POST.get('quantity', 1))
        lesson = get_object_or_404(Service, pk=item_id)
        selected_date = request.POST.get('date')
        selected_time_slot = request.POST.get('time_slot')

        if not selected_date or not selected_time_slot:
            return redirect(reverse('view_bag'))

        if lesson.type == Service.PRIVATE and quantity != 1:
            messages.error(
                request,
                'Only one participant is allowed for private lessons.'
                )
            return redirect(redirect_url)

        if lesson.type == Service.GROUP and not (2 <= quantity <= 5):
            messages.error(
                request,
                'Group lessons must have between 2 and 5 participants'
                )
            return redirect(redirect_url)

        lesson_key = f"{selected_date}_{selected_time_slot}"

        if lesson_key in bag['lessons']:
            bag['lessons'][lesson_key]['quantity'] = quantity
            total_price = quantity * lesson.price_per_participant
            bag['lessons'][lesson_key]['details']['total_price'] = total_price

            success_message = (
                f'Updated {item_type} on {selected_date} at '
                f'{selected_time_slot} to {quantity} participants'
            )
            messages.success(request, success_message)

        else:
            del bag['lessons'][lesson_key]
            messages.success(
                request,
                f'Removed {item_type} on {selected_date}'
                f'at {selected_time_slot} from your bag'
            )

    else:
        messages.error(request, f'Lesson time slot not found in your bag')

    request.session['bag'] = bag
    request.session.modified = True
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
                messages.success(
                    request,
                    f'Removed {product.name} (Size: {size}) from your bag'
                )
            else:
                del bag['products'][item_id]
                messages.success(
                    request,
                    f'Removed {product.name} from your bag'
                )

        elif item_type == 'lesson':
            lesson = get_object_or_404(Service, pk=item_id)
            selected_date = request.POST.get('date', None)
            selected_time_slot = request.POST.get('time_slot', None)
            lesson_key = f"{selected_date}_{selected_time_slot}"
            del bag['lessons'][lesson_key]
            messages.success(
                request,
                f'Removed {lesson.get_type_display}'
                f'lesson on {selected_date} at'
                f'{selected_time_slot} from your bag'
            )

            if not selected_date or not selected_time_slot:
                messages.error(request, "Invalid lesson date or time slot.")
                return HttpResponse(
                    "Invalid lesson date or time slot.",
                    status=400
                )

            lesson_key = f"{selected_date}_{selected_time_slot}"

            if lesson_key in bag['lessons']:
                del bag['lessons'][lesson_key]
                messages.success(
                    request,
                    f'Removed {lesson.get_type_display}'
                    f'lesson on {selected_date}'
                    f'at {selected_time_slot} from your bag'
                )
            else:
                messages.error(
                    request,
                    "Lesson time slot not found in your bag."
                )
                return HttpResponse(status=404)

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        print(f"Error removing item from bag: {e}")
        return HttpResponse(status=500)
