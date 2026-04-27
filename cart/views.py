from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import ProductVariant
from .cart import Cart

@require_POST
def cart_add(request):
    cart = Cart(request)
    variant_id = request.POST.get('variant_id')
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))
        cart.add(variant=variant, quantity=quantity)
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart.remove(variant)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})
