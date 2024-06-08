from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse

from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .forms import OrderForm
from .models import Order, ProductsLineItem, LessonLineItem
from product.models import Product, Service
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from bag.contexts import bag_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        print("Bag contents at checkout:", bag)  # Debug print

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.original_bag = json.dumps(bag)
            order.stripe_pid = request.POST.get('client_secret').split('_secret')[0]
            order.save()
            
            for item_id, item_data in bag.get('products', {}).items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, dict):
                        items_by_size = item_data['items_by_size']
                        for size, quantity in items_by_size.items():
                            order_line_item = ProductsLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                            print(f"Saved product line item: {order_line_item}")  # Debug print
                    else:
                        order_line_item = ProductsLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                        print(f"Saved product line item: {order_line_item}")  # Debug print

                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            for lesson_key, lesson_data in bag.get('lessons', {}).items():
                try:
                    lesson = Service.objects.get(id=lesson_data['item_id'])
                    order_line_item = LessonLineItem(
                        order=order,
                        service=lesson,
                        quantity=lesson_data['quantity'],
                        date=lesson_data['details']['date'],
                        time_slot=lesson_data['details']['time_slot'],
                    )
                    order_line_item.save()
                    print(f"Saved lesson line item: {order_line_item}")  # Debug print

                except Service.DoesNotExist:
                    messages.error(request, (
                        "One of the lessons wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            order.update_total()
            print(f"Updated order total: {order.grand_total}")  # Debug print

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(
                reverse('checkout_success', args=[order.order_number])
            )
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(
                request,
                "There's nothing in your bag at the moment"
            )
            return redirect(reverse('product'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

        context = bag_contents(request)
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

        return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    print(f"Order at checkout success: {order}")  # Debug print

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # User's profile attached to order
        order.user_profile = profile
        order.save()

        # User's info being saved
        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    # Send confirmation email
    subject = render_to_string(
        'checkout/confirmation_emails/confirmation_subject.html',
        {'order': order})
    body = render_to_string(
        'checkout/confirmation_emails/confirmation_emails_body.html',
        {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [order.email]
    )

    messages.success(request, f'Order successfully processed! \
        Your surfing order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout-success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
