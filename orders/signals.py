from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from django.db.models.signals import post_save, pre_save

from django.db import transaction
from products.models import ProductVariant

@receiver(pre_save, sender=Order)
def restore_stock_on_cancellation(sender, instance, **kwargs):
    """
    Restore stock if an order status is changed to 'cancelled'.
    """
    if instance.id:
        try:
            # Use select_for_update on the order check if needed, 
            # but more importantly on the variant restoration.
            previous_order = Order.objects.get(id=instance.id)
            previous_status = previous_order.status
            
            # Restore stock if moving to cancelled or returned from a non-restored state
            if previous_status not in ['cancelled', 'returned'] and instance.status in ['cancelled', 'returned']:
                with transaction.atomic():
                    for item in instance.items.all():
                        if item.variant:
                            # Lock the variant row to prevent race conditions
                            variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                            variant.stock += item.quantity
                            variant.save()
                    print(f"DEBUG: Stock restored for Order #{instance.id} (Status: {instance.status})")
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def send_order_status_update_email(sender, instance, created, **kwargs):
    """
    Send an email notification when an order status changes to 'shipped' or 'delivered'.
    """
    if not created:
        # Check if status has changed
        # Note: In a production environment, we'd compare the old status with the new one.
        # For simplicity in this demo, we'll send it if status is 'shipped' or 'delivered'.
        if instance.status in ['shipped', 'delivered']:
            subject = f'Mise à jour de votre commande #{instance.id} - LUXE.'
            
            # Choose specific message based on status
            status_text = "été expédiée" if instance.status == 'shipped' else "été livrée"
            
            context = {
                'order': instance,
                'status_text': status_text,
            }
            
            html_message = render_to_string('orders/order_status_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                html_message=html_message,
                fail_silently=False,
            )
