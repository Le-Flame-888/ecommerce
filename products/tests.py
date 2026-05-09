from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Product, ProductVariant, Review
from users.models import User

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Smartphone',
            description='A great phone',
            base_price=500.00,
            category=self.category
        )

    def test_category_slug_generation(self):
        """Test that category slug is generated automatically."""
        self.assertEqual(self.category.slug, 'electronics')

    def test_product_slug_generation(self):
        """Test that product slug is generated automatically."""
        self.assertEqual(self.product.slug, 'test-smartphone')

    def test_product_variant_final_price(self):
        """Test the final price calculation with price modifier."""
        variant = ProductVariant.objects.create(
            product=self.product,
            size='64GB',
            color='Black',
            stock=10,
            price_modifier=50.00
        )
        self.assertEqual(variant.final_price, 550.00)

    def test_product_average_rating_only_approved(self):
        """Test product average rating only considers approved reviews."""
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')
        Review.objects.create(product=self.product, user=user1, rating=4, comment='Good', is_approved=True)
        Review.objects.create(product=self.product, user=user2, rating=2, comment='Bad', is_approved=False)
        
        self.assertEqual(self.product.get_average_rating(), 4.0)
        self.assertEqual(self.product.get_review_count(), 1)

class ProductViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Apparel')
        self.p1 = Product.objects.create(name='A-Shirt', description='Nice shirt', base_price=20.00, category=self.category)
        self.p2 = Product.objects.create(name='B-Pants', description='Cool pants', base_price=40.00, category=self.category)
        
        # Add variants for filtering tests
        ProductVariant.objects.create(product=self.p1, size='M', color='Red', stock=5)
        ProductVariant.objects.create(product=self.p2, size='L', color='Blue', stock=10)

    def test_product_list_view(self):
        """Test that the product list page loads and shows products."""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A-Shirt')
        self.assertContains(response, 'B-Pants')

    def test_product_list_search(self):
        """Test searching for products."""
        response = self.client.get(reverse('products:product_list') + '?q=shirt')
        self.assertContains(response, 'A-Shirt')
        self.assertNotContains(response, 'B-Pants')

    def test_product_list_filter_price(self):
        """Test filtering products by price."""
        response = self.client.get(reverse('products:product_list') + '?max_price=30')
        self.assertContains(response, 'A-Shirt')
        self.assertNotContains(response, 'B-Pants')

    def test_product_list_filter_color(self):
        """Test filtering products by color (variant)."""
        response = self.client.get(reverse('products:product_list') + '?color=Red')
        self.assertContains(response, 'A-Shirt')
        self.assertNotContains(response, 'B-Pants')

    def test_product_detail_view_shows_only_approved_reviews(self):
        """Test the product detail page only shows approved reviews."""
        user1 = User.objects.create_user(username='reviewer1', password='pass')
        user2 = User.objects.create_user(username='reviewer2', password='pass')
        
        Review.objects.create(product=self.p1, user=user1, rating=5, comment='Amazing!', is_approved=True)
        Review.objects.create(product=self.p1, user=user2, rating=1, comment='Terrible!', is_approved=False)

        response = self.client.get(reverse('products:product_detail', kwargs={'slug': self.p1.slug}))
        self.assertContains(response, 'Amazing!')
        self.assertNotContains(response, 'Terrible!')
