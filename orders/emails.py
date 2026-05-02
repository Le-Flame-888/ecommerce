from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_confirmation_email(order):
    """
    Send order confirmation email to the customer.
    """
    subject = f'Confirmation de votre commande #{order.id}'
    
    # Render HTML template
    html_message = render_to_string('orders/order_confirmation_email.html', {
        'order': order,
    })
    
    # Create plain text version
    plain_message = strip_tags(html_message)
    
    # Send email
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=False,
    )