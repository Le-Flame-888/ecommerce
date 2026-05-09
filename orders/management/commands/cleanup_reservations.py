from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from orders.models import Order

class Command(BaseCommand):
    help = 'Releases stock reservations for pending orders older than 30 minutes.'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(minutes=30)
        expired_orders = Order.objects.filter(
            status='pending',
            paid=False,
            created_at__lt=threshold
        )
        
        count = expired_orders.count()
        for order in expired_orders:
            # cancel_order() triggers the signal to restore stock
            order.cancel_order()
            self.stdout.write(self.style.SUCCESS(f'Cancelled Order #{order.id} and restored stock.'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {count} expired reservations.'))
