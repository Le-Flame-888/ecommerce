from django.shortcuts import render
from django.contrib import messages
from products.models import Product, Category

def home(request):
    featured_products = Product.objects.filter(is_active=True).order_by('-id')[:8]
    categories = Category.objects.all()[:4]
    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        # In production, use send_mail() here
        print(f"DEBUG: Contact form — From: {name} ({email}), Subject: {subject}, Message: {message}")
        messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
        return render(request, 'core/contact.html', {'sent': True})
    return render(request, 'core/contact.html')
