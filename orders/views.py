from django.shortcuts import render, redirect
from django.contrib import messages
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('products:product_list')
        
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_amount = cart.get_total_price()
            order.save()
            
            for item in cart:
                variant = item['variant']
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    price=item['price'],
                    quantity=item['quantity']
                )
                # Deduct stock
                variant.stock -= item['quantity']
                if variant.stock < 0:
                    variant.stock = 0
                variant.save()
            
            cart.clear()
            # In a real app, send email here
            print(f"DEBUG: Order {order.id} confirmed. Email sent to {order.email}")
            
            return render(request, 'orders/success.html', {'order': order})
    else:
        # Pre-fill form if user is authenticated and has a default address
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': request.user.phone_number,
            }
            address = request.user.addresses.filter(is_default=True).first()
            if address:
                initial_data.update({
                    'street': address.street,
                    'city': address.city,
                    'postal_code': address.postal_code,
                    'country': address.country,
                })
        form = OrderCreateForm(initial=initial_data)
        
    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})
