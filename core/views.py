from django.shortcuts import render, redirect
import os
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from products.models import Product, Category
from .models import Newsletter
from django.utils.translation import gettext as _

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
        full_message = _("Message from %(name)s (%(email)s):\n\n%(message)s") % {'name': name, 'email': email, 'message': message_text}
        send_mail(
            f"Contact Form: {subject_text}",
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Sending to self as admin notification
            fail_silently=False,
        )
        
        messages.success(request, _('Your message has been sent successfully! We will get back to you as soon as possible.'))
        return render(request, 'core/contact.html', {'sent': True})
    
    return render(request, 'core/contact.html')

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

@require_POST
def newsletter_signup(request):
    email = request.POST.get('email')
    if email:
        if Newsletter.objects.filter(email=email).exists():
            messages.warning(request, _("You are already subscribed to our newsletter."))
        else:
            Newsletter.objects.create(email=email)
            
            # Sync with Brevo (Sendinblue)
            api_key = os.getenv('BREVO_API_KEY')
            list_id = os.getenv('BREVO_LIST_ID')
            
            if api_key and list_id:
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key['api-key'] = api_key
                api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
                
                create_contact = sib_api_v3_sdk.CreateContact(
                    email=email,
                    list_ids=[int(list_id)],
                    update_enabled=True
                )
                
                try:
                    api_instance.create_contact(create_contact)
                except ApiException as e:
                    # Log error if needed, but don't crash for the user
                    print(f"Brevo API Error: {e}")
            
            messages.success(request, _("Thank you! You are now subscribed to the LUXE. newsletter."))
    else:
        messages.error(request, _("Please enter a valid email address."))
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
