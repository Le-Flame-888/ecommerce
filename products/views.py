from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category

def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'variants')
    categories = Category.objects.all()
    
    # Category filtering
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    # Search
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('base_price')
    elif sort == 'price_desc':
        products = products.order_by('-base_price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-id')
        
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'current_category': category_slug,
        'current_sort': sort,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })
