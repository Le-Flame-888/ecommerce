import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Order, OrderItem
from products.models import Product, Category, ProductVariant
from users.models import User
from django.conf import settings

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
        # Create a pending order as if it came from checkout
        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            street='123 Street',
            city='Casablanca',
            postal_code='20000',
            total_amount=100.00,
            status='pending'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            variant=self.variant,
            price=100.00,
            quantity=2
        )

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_marks_order_as_paid(self, mock_webhook):
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
        
        # Verify stock WAS NOT deducted again (still at 10 because manual creation didn't deduct)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 10)

    def test_stock_restoration_on_cancellation(self):
        # Setup: Order exists and stock was deducted (simulated)
        self.variant.stock = 8
        self.variant.save()
        
        # Now cancel the order
        self.order.status = 'cancelled'
        self.order.save()
        
        # Verify stock is restored
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 10) # 8 + 2

    @patch('stripe.checkout.Session.create')
    def test_stock_reservation_at_checkout(self, mock_stripe_create):
        # Mock Stripe session
        mock_stripe_create.return_value = type('obj', (object,), {'id': 'sess_123', 'url': 'http://stripe.com/pay'})
        
        # Setup cart in session
        session = self.client.session
        session[settings.CART_SESSION_ID] = {
            str(self.variant.id): {'quantity': 3, 'price': str(self.variant.final_price)}
        }
        session.save()
        
        # Verify initial stock
        self.assertEqual(self.variant.stock, 10)
        
        # Proceed to checkout
        url = reverse('orders:checkout')
        response = self.client.post(url, {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'phone': '0600000000',
            'street': 'Street 1',
            'city': 'Rabat',
            'postal_code': '10000',
            'country': 'Maroc'
        })
        
        # Check if redirected (either 302 or 303)
        self.assertIn(response.status_code, [302, 303])
        
        # If it was a 302 to the checkout page, it means it failed
        if response.status_code == 302 and response.url == url:
            from django.contrib.messages import get_messages
            msgs = [m.message for m in get_messages(response.wsgi_request)]
            self.fail(f"Checkout failed and redirected back to form. Messages: {msgs}")

        # Verify stock was deducted immediately
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 7) # 10 - 3
