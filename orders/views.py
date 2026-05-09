import stripe
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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
            
            line_items = []
            try:
                with transaction.atomic():
                    order.save()
                    for item in cart:
                        variant = ProductVariant.objects.select_for_update().get(id=item['variant'].id)
                        
                        # Double check stock inside the transaction
                        if variant.stock < item['quantity']:
                            raise ValueError(f"Désolé, le produit {variant.product.name} n'a plus assez de stock.")
                        
                        variant.stock -= item['quantity']
                        variant.save()
                        
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
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart:cart_detail')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {str(e)}")
                return redirect('orders:checkout')
            
            # Create Stripe Checkout Session
            success_url = request.build_absolute_uri(reverse('orders:payment_success')) + f'?order_id={order.id}'
            cancel_url = request.build_absolute_uri(reverse('orders:payment_cancelled')) + f'?order_id={order.id}'
            
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
    
    addresses = []
    if request.user.is_authenticated:
        addresses = request.user.addresses.all()
        
    return render(request, 'orders/checkout.html', {
        'cart': cart, 
        'form': form,
        'addresses': addresses
    })
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.db import transaction
from products.models import ProductVariant

def payment_success(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/success.html', {'order': order})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('client_reference_id')
        
        if order_id:
            try:
                with transaction.atomic():
                    # Lock the order row to prevent simultaneous processing
                    order = Order.objects.select_for_update().get(id=order_id)
                    
                    if not order.paid:
                        # Mark as paid
                        order.paid = True
                        order.status = 'confirmed'
                        order.save()
                        
                        # Stock was already deducted at checkout to reserve it
                        # No need to deduct again here.
                        
                        # Send confirmation email
                        send_order_confirmation_email(order)
            except Order.DoesNotExist:
                return HttpResponse(status=404)

    return HttpResponse(status=200)

def payment_cancelled(request):
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if order.status == 'pending':
                order.cancel_order()
                messages.warning(request, "Le paiement a été annulé et votre réservation de stock a été libérée.")
            else:
                messages.warning(request, "Le paiement a été annulé.")
        except Order.DoesNotExist:
            messages.warning(request, "Le paiement a été annulé.")
    else:
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
