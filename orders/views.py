from django.shortcuts import render, redirect
from django.contrib import messages
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .emails import send_order_confirmation_email

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
            
            # Apply coupon if exists
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            
            order.total_amount = cart.get_total_price_after_discount()
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
            
            # Send order confirmation email
            send_order_confirmation_email(order)
            
            cart.clear()
            messages.success(request, f'Commande #{order.id} confirmée avec succès !')
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
        
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow cancellation if order is not yet shipped
    if order.status in ['pending', 'confirmed']:
        if order.cancel_order():
            messages.success(request, f"La commande #{order.id} a été annulée et le stock a été restauré.")
        else:
            messages.warning(request, "La commande est déjà annulée.")
    else:
        messages.error(request, "Impossible d'annuler une commande déjà expédiée ou livrée.")
    
    return redirect('users:profile')
