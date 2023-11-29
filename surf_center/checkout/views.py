from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from bag.contexts import bag_contents

def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('product'))

    order_form = OrderForm()
    
    context = bag_contents(request)  
    context['order_form'] = order_form 
    
    return render(request, 'checkout/checkout.html', context)