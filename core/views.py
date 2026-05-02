from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from products.models import Product, Category
from .models import Newsletter

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
        subject_text = request.POST.get('subject', '')
        message_text = request.POST.get('message', '')
        
        # Send email to admin
        full_message = f"Message de {name} ({email}):\n\n{message_text}"
        send_mail(
            f"Contact Form: {subject_text}",
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Sending to self as admin notification
            fail_silently=False,
        )
        
        messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
        return render(request, 'core/contact.html', {'sent': True})
    
    return render(request, 'core/contact.html')

@require_POST
def newsletter_signup(request):
    email = request.POST.get('email')
    if email:
        if Newsletter.objects.filter(email=email).exists():
            messages.warning(request, "Vous êtes déjà inscrit à notre newsletter.")
        else:
            Newsletter.objects.create(email=email)
            messages.success(request, "Merci ! Vous êtes maintenant inscrit à la newsletter LUXE.")
    else:
        messages.error(request, "Veuillez entrer une adresse email valide.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /cart/",
        "Disallow: /orders/",
        "Disallow: /users/profile/",
        "",
        "Sitemap: http://127.0.0.1:8000/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
