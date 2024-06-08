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

    for product_id, item_data in products.items():
        product = get_object_or_404(Product, pk=product_id)

        if isinstance(item_data, dict):
            for size, quantity in item_data['items_by_size'].items():
                subtotal = quantity * product.price
                product_total += subtotal
                total += subtotal
                product_count += quantity
                bag_items.append({
                    'id': product_id,
                    'quantity': quantity,
                    'item': product,
                    'type': 'product',
                    'size': size,
                    'subtotal': item_data * product.price
                })

        else:
            subtotal = item_data * product.price
            product_total += subtotal
            total += subtotal
            product_count += item_data
            bag_items.append({
                'id': product_id,
                'quantity': item_data,
                'item': product,
                'type': 'product',
                'subtotal': item_data * product.price
            })

    # calculating delivery for products

    if product_total > 0:
        delivery = (
            product_total *
            Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        )

    # Adding lessons to the bag
    lessons = bag.get('lessons', {})

    for lesson_key, lesson_info in lessons.items():

        if 'item_id' not in lesson_info or 'details' not in lesson_info:
            continue

        lesson_id = lesson_info['item_id']
        quantity = lesson_info['quantity']
        lesson = get_object_or_404(Service, pk=lesson_id)
        participants = lesson_info.get('quantity', 1)
        date = lesson_info['details'].get('date', 'Not Specified')
        time_slot = lesson_info['details'].get('time_slot', 'Not Specified')

        total_price_per_lesson = (
            Decimal(quantity) *
            Decimal(lesson.price_per_participant)
        )
        total += total_price_per_lesson

        bag_items.append({
            'id': lesson_id,
            'quantity': quantity,
            'item': lesson,
            'type': 'lesson',
            'subtotal': total_price_per_lesson,
            'date': date,
            'time_slot': time_slot,
            'participants': participants
        })

    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'subtotal': item_data * product.price,
        'grand_total': grand_total,
    }

    return context
