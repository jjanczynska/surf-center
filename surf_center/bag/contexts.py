from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.conf import settings
from product.models import Product, Service

def bag_contents(request):
    """Context for handling the shopping bag"""

    bag_items = []
    total = Decimal(0)
    product_total = Decimal(0)
    product_count = 0
    delivery = Decimal(0)

    bag = request.session.get('bag', {'products': {}, 'lessons': {}})


    # Adding products to the bag
    products = bag.get('products', {})
    for product_id, quantity in products.items():
        product = get_object_or_404(Product, pk=product_id)
        product_subtotal = quantity * product.price
        product_total += product_subtotal
        product_count += quantity
        bag_items.append({
            'id': product_id,
            'quantity': quantity,
            'item': product,
            'type': 'product',
            'subtotal': product_subtotal,
        })

    # calculating delivery for products

    if product_total > 0:
        delivery = product_total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)

    # Adding lessons to the bag
    lessons = bag.get('lessons', {})
    for lesson_id, details in lessons.items():
        lesson = get_object_or_404(Service, pk=lesson_id)

        selected_date = details['date']
        selected_time_slot = details['time_slot']
        number_of_participants = details['participants']
        total_price_per_lesson = Decimal(number_of_participants) * lesson.price_per_participant()

        bag_items.append({
            'id': lesson_id,
            'details': {
                'date': selected_date, 
                'time_slot': selected_time_slot, 
                'participants': number_of_participants, 
                'total_price': total_price_per_lesson
            },
        'item': lesson,
        'type': 'lesson',
        })

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'grand_total': total,
    }

    return context


    

