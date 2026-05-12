from .models import Product

def recently_viewed(request):
    product_ids = request.session.get('recently_viewed', [])
    if not product_ids:
        return {'recently_viewed_products': []}
    
    # Fetch products and preserve order from the session list
    products = Product.objects.filter(id__in=product_ids, is_active=True).prefetch_related('images')
    
    # Map to preserve order
    product_map = {p.id: p for p in products}
    ordered_products = [product_map[pid] for pid in product_ids if pid in product_map]
    
    return {'recently_viewed_products': ordered_products}
