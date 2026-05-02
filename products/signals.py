from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import ProductVariant

@receiver(post_save, sender=ProductVariant)
def check_stock_level(sender, instance, **kwargs):
    """
    Checks stock levels and alerts admin if low or out of stock.
    """
    threshold = 5 # Low stock threshold
    
    if instance.stock == 0:
        subject = f'ALERTE : Rupture de stock - {instance.product.name}'
        message = f'Le produit {instance.product.name} (Taille: {instance.size}, Couleur: {instance.color}) est désormais en rupture de stock.'
        send_to_admin(subject, message)
        
    elif instance.stock <= threshold:
        subject = f'AVERTISSEMENT : Stock faible - {instance.product.name}'
        message = f'Le produit {instance.product.name} (Taille: {instance.size}, Couleur: {instance.color}) a un stock faible : {instance.stock} unités restantes.'
        send_to_admin(subject, message)

def send_to_admin(subject, message):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL], # Assuming this is set in settings
            fail_silently=True,
        )
    except:
        pass
