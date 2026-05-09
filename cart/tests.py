from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category, ProductVariant

class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Phone', base_price=100.00, category=self.category
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, size='S', color='Black', stock=10
        )

    def test_cart_add_and_total(self):
        self.client.post(reverse('cart:cart_add'), {'variant_id': self.variant.id, 'quantity': 2})
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '200.00')

    def test_cart_remove(self):
        self.client.post(reverse('cart:cart_add'), {'variant_id': self.variant.id, 'quantity': 1})
        self.client.post(reverse('cart:cart_remove', kwargs={'variant_id': self.variant.id}))
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertContains(response, 'Votre panier est vide')

    def test_cart_update_quantity(self):
        self.client.post(reverse('cart:cart_add'), {'variant_id': self.variant.id, 'quantity': 1})
        self.client.post(reverse('cart:cart_update', kwargs={'variant_id': self.variant.id}), {'quantity': 5})
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertContains(response, '500.00')

    def test_cart_stock_validation(self):
        self.client.post(reverse('cart:cart_add'), {'variant_id': self.variant.id, 'quantity': 15})
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertContains(response, '1000.00')
