from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import ProductVariant
from .cart import Cart
from django.utils.translation import gettext as _

@require_POST
def cart_add(request):
    cart = Cart(request)
    variant_id = request.POST.get('variant_id')
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))
        # Stock validation
        if variant.stock <= 0:
            messages.error(request, _('Sorry, "%(name)s (%(size)s)" is out of stock.') % {'name': variant.product.name, 'size': variant.size})
            return redirect('cart:cart_detail')
        if quantity > variant.stock:
            messages.warning(request, _('Limited stock: only %(stock)d unit(s) available for "%(name)s (%(size)s)".') % {'stock': variant.stock, 'name': variant.product.name, 'size': variant.size})
            quantity = variant.stock
        cart.add(variant=variant, quantity=quantity)
        messages.success(request, _('"%(name)s (%(size)s)" added to cart.') % {'name': variant.product.name, 'size': variant.size})
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > variant.stock:
        messages.warning(request, _('Limited stock: only %(stock)d unit(s) available.') % {'stock': variant.stock})
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
    messages.success(request, _('"%(name)s" removed from cart.') % {'name': variant.product.name})
    return redirect('cart:cart_detail')

from coupons.forms import CouponApplyForm

def cart_detail(request):
    cart = Cart(request)
    coupon_apply_form = CouponApplyForm()
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'coupon_apply_form': coupon_apply_form
    })
