from django.test import TestCase, Client
from django.urls import reverse
from .models import User

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertEqual(user.username, 'testuser')

class UserAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login_view(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_wishlist_toggle(self):
        from products.models import Product, Category
        cat = Category.objects.create(name='Test')
        prod = Product.objects.create(name='Test Prod', base_price=10.00, category=cat)
        self.client.login(username='testuser', password='password123')
        self.client.get(reverse('users:toggle_wishlist', kwargs={'product_id': prod.id}))
        self.assertIn(prod, self.user.wishlist.all())
