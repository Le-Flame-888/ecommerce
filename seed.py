import os
import django
import shutil
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_project.settings')
django.setup()

from products.models import Category, Product, ProductVariant, ProductImage

# Ensure media directory exists
os.makedirs('media/products', exist_ok=True)

# 1. Create Category
cat, _ = Category.objects.get_or_create(name='Tendances', slug='tendances')

# 2. Create Sneaker
sneaker, created = Product.objects.get_or_create(
    name='Sneaker Phantom',
    defaults={'slug': 'sneaker-phantom', 'category': cat, 'description': 'Noir absolu.', 'base_price': 450.00}
)
if created:
    ProductVariant.objects.create(product=sneaker, size='42', color='Noir', stock=10)
    # copy static image to media
    src = 'static/images/sneaker.png'
    dst = 'media/products/sneaker.png'
    if os.path.exists(src):
        shutil.copy(src, dst)
        with open(dst, 'rb') as f:
            ProductImage.objects.create(product=sneaker, image=File(f, name='sneaker.png'))

# 3. Create T-Shirt
tshirt, created = Product.objects.get_or_create(
    name='T-Shirt Signature',
    defaults={'slug': 't-shirt-signature', 'category': cat, 'description': 'Blanc pur.', 'base_price': 200.00}
)
if created:
    ProductVariant.objects.create(product=tshirt, size='M', color='Blanc', stock=15)
    src = 'static/images/tshirt.png'
    dst = 'media/products/tshirt.png'
    if os.path.exists(src):
        shutil.copy(src, dst)
        with open(dst, 'rb') as f:
            ProductImage.objects.create(product=tshirt, image=File(f, name='tshirt.png'))

print("Seed finished!")
