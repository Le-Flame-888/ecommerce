import stripe
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .emails import send_order_confirmation_email

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('products:product_list')
        
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Pre-checkout stock check
            for item in cart:
                variant = item['variant']
                if variant.stock < item['quantity']:
                    messages.error(request, f"Désolé, le produit {variant.product.name} ({variant.size}/{variant.color}) n'a plus assez de stock (disponible: {variant.stock}).")
                    return redirect('cart:cart_detail')

            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            
            # Apply coupon if exists
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            
            order.total_amount = cart.get_total_price_after_discount()
            order.save()
            
            line_items = []
            for item in cart:
                variant = item['variant']
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    price=item['price'],
                    quantity=item['quantity']
                )
                # Prepare line item for Stripe
                line_items.append({
                    'price_data': {
                        'currency': settings.STRIPE_CURRENCY,
                        'unit_amount': int(item['price'] * 100),
                        'product_data': {
                            'name': variant.product.name,
                        },
                    },
                    'quantity': item['quantity'],
                })
            
            # Create Stripe Checkout Session
            success_url = request.build_absolute_uri(reverse('orders:payment_success')) + f'?order_id={order.id}'
            cancel_url = request.build_absolute_uri(reverse('orders:payment_cancelled'))
            
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=success_url,
                    cancel_url=cancel_url,
                    client_reference_id=str(order.id),
                )
                order.stripe_id = session.id
                order.save()
                
                cart.clear()
                return redirect(session.url, code=303)
            except Exception as e:
                messages.error(request, f"Erreur de paiement : {str(e)}")
                return redirect('orders:checkout')

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
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.db import transaction
from products.models import ProductVariant

def payment_success(request):
    order_id = request.GET.get('order_id')
    
    with transaction.atomic():
        # Lock the order row to prevent simultaneous processing
        order = get_object_or_404(Order.objects.select_for_update(), id=order_id)
        
        if not order.paid:
            # Mark as paid
            order.paid = True
            order.status = 'confirmed'
            order.save()
            
            # Deduct stock for all items using select_for_update to lock variants
            for item in order.items.all():
                if item.variant:
                    # Lock the specific variant row
                    variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                    variant.stock -= item.quantity
                    if variant.stock < 0:
                        variant.stock = 0
                    variant.save()
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
    messages.success(request, f'Commande #{order.id} payée et confirmée avec succès !')
    return render(request, 'orders/success.html', {'order': order})

def payment_cancelled(request):
    messages.warning(request, "Le paiement a été annulé.")
    return render(request, 'orders/cancel.html')

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
