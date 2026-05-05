import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Order, OrderItem
from products.models import Product, Category, ProductVariant
from users.models import User

class OrderFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        self.category = Category.objects.create(name='Clothing')
        self.product = Product.objects.create(
            name='Luxury Shirt',
            base_price=100.00,
            category=self.category
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='White',
            stock=10
        )
        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            street='123 Street',
            city='Casablanca',
            postal_code='20000',
            total_amount=100.00
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            variant=self.variant,
            price=100.00,
            quantity=2
        )

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_marks_order_as_paid_and_deducts_stock(self, mock_webhook):
        # Mock Stripe event
        mock_webhook.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': str(self.order.id),
                    'payment_status': 'paid'
                }
            }
        }

        # Simulate webhook call
        url = reverse('orders:stripe_webhook')
        response = self.client.post(
            url,
            data=json.dumps({'dummy': 'data'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='dummy_sig'
        )

        self.assertEqual(response.status_code, 200)
        
        # Verify order status
        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
        self.assertEqual(self.order.status, 'confirmed')
        
        # Verify stock deduction
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8) # 10 - 2

    def test_stock_restoration_on_cancellation(self):
        # First, simulate order being paid (status confirmed, stock deducted)
        self.order.status = 'confirmed'
        self.order.paid = True
        self.order.save()
        
        # Manually deduct stock as if webhook happened
        self.variant.stock -= 2
        self.variant.save()
        
        # Now cancel the order
        self.order.status = 'cancelled'
        self.order.save()
        
        # Verify stock is restored
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 10) # 8 + 2

    def test_insecure_payment_success_redirect_does_not_mark_as_paid(self):
        # Accessing the success page with an order ID should NOT mark it as paid anymore
        url = f"{reverse('orders:payment_success')}?order_id={self.order.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid)
        self.assertEqual(self.order.status, 'pending')
