from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, AddressForm
from .models import Address
from products.models import Product

def register(request):
    if request.user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} ! Votre compte a été créé.')
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
            messages.success(request, 'Adresse ajoutée avec succès.')
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
        messages.success(request, f'"{product.name}" retiré des favoris.')
    else:
        request.user.wishlist.add(product)
        messages.success(request, f'"{product.name}" ajouté aux favoris !')
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))
