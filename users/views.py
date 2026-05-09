from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, AddressForm
from .models import Address
from products.models import Product

from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _

def register(request):
    if request.user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send Welcome Email
            try:
                send_mail(
                    _('Welcome to LUXE.!'),
                    _('Hello %(username)s,\n\nThank you for joining LUXE.! We are delighted to have you as a member.\n\nStart exploring our collections now: http://127.0.0.1:8000/products/\n\nThe LUXE. team') % {'username': user.username},
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except:
                pass
                
            login(request, user)
            messages.success(request, _('Welcome %(username)s! Your account has been created.') % {'username': user.username})
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    addresses = request.user.addresses.all()
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            if not addresses.exists():
                address.is_default = True
            address.save()
            messages.success(request, _('Address added successfully.'))
            return redirect('users:profile')
    else:
        address_form = AddressForm()
        
    return render(request, 'users/profile.html', {
        'addresses': addresses,
        'address_form': address_form
    })

@login_required
def wishlist(request):
    products = request.user.wishlist.all()
    return render(request, 'users/wishlist.html', {'products': products})

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product in request.user.wishlist.all():
        request.user.wishlist.remove(product)
        messages.success(request, _('"%(name)s" removed from wishlist.') % {'name': product.name})
    else:
        request.user.wishlist.add(product)
        messages.success(request, _('"%(name)s" added to wishlist!') % {'name': product.name})
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))
