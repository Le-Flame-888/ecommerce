import os
import django
import shutil
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_project.settings')
django.setup()

from products.models import Category, Product, ProductVariant, ProductImage

# Ensure media directory exists
os.makedirs('media/products', exist_ok=True)

def add_product(name, slug, category_name, description, price, img_url, size, stock):
    cat, _ = Category.objects.get_or_create(name=category_name, slug=category_name.lower())
    
    product, created = Product.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'category': cat, 'description': description, 'base_price': price}
    )
    
    if created:
        # Add a few variants
        ProductVariant.objects.create(product=product, size=size, color='Standard', stock=stock)
        
        # Download image
        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                ProductImage.objects.create(product=product, image=File(img_temp, name=f'{slug}.jpg'))
                print(f"Added product: {name}")
        except Exception as e:
            print(f"Failed to add image for {name}: {e}")

# Extra products
data = [
    ("Hoodie Zenith", "hoodie-zenith", "Hommes", "Confort ultime en coton bio.", 550.00, "https://images.unsplash.com/photo-1556821840-3a63f95609a7?q=80&w=600", "L", 20),
    ("Pantalon Cargo Nomad", "cargo-nomad", "Hommes", "Style utilitaire moderne.", 480.00, "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?q=80&w=600", "42", 15),
    ("Casquette Onyx", "casquette-onyx", "Accessoires", "Minimalisme urbain.", 180.00, "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?q=80&w=600", "Unique", 30),
    ("Veste Bomber Stealth", "bomber-stealth", "Hommes", "Protection et style.", 850.00, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?q=80&w=600", "XL", 10),
    ("Sac à dos Urban", "sac-urban", "Accessoires", "Idéal pour le quotidien.", 350.00, "https://images.unsplash.com/photo-1553062407-98eebd4c7a6d?q=80&w=600", "Unique", 25),
    ("Robe Minimaliste", "robe-minimaliste", "Femmes", "L'élégance du noir.", 650.00, "https://images.unsplash.com/photo-1539109132382-381bb3f1c2b3?q=80&w=600", "S", 12),
]

for item in data:
    add_product(*item)

print("Seed extended finished!")
