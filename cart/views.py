from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import ProductVariant
from .cart import Cart

@require_POST
def cart_add(request):
    cart = Cart(request)
    variant_id = request.POST.get('variant_id')
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))
        # Stock validation
        if variant.stock <= 0:
            messages.error(request, f'Désolé, "{variant.product.name} ({variant.size})" est en rupture de stock.')
            return redirect('cart:cart_detail')
        if quantity > variant.stock:
            messages.warning(request, f'Stock limité : seulement {variant.stock} unité(s) disponible(s) pour "{variant.product.name} ({variant.size})".')
            quantity = variant.stock
        cart.add(variant=variant, quantity=quantity)
        messages.success(request, f'"{variant.product.name} ({variant.size})" ajouté au panier.')
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > variant.stock:
        messages.warning(request, f'Stock limité : seulement {variant.stock} unité(s) disponible(s).')
        quantity = variant.stock
    if quantity < 1:
        quantity = 1
    cart.add(variant=variant, quantity=quantity, override_quantity=True)
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart.remove(variant)
    messages.success(request, f'"{variant.product.name}" retiré du panier.')
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})
