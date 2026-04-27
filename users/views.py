from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, AddressForm
from .models import Address

def register(request):
    if request.user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
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
            return redirect('users:profile')
    else:
        address_form = AddressForm()
        
    return render(request, 'users/profile.html', {
        'addresses': addresses,
        'address_form': address_form
    })

from products.models import Product

@login_required
def wishlist(request):
    products = request.user.wishlist.all()
    return render(request, 'users/wishlist.html', {'products': products})

@login_required
def toggle_wishlist(request, product_id):
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, id=product_id)
    if product in request.user.wishlist.all():
        request.user.wishlist.remove(product)
    else:
        request.user.wishlist.add(product)
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))
