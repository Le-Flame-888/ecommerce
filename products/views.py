from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category

def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'variants').order_by('-id')
    categories = Category.objects.all()
    
    # Optional filtering
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        
    # Pagination
    paginator = Paginator(products, 12) # 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'products/product_list.html', {
        'products': page_obj, # the template loops over 'products'
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'current_category': category_slug,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/product_detail.html', {
        'product': product,
    })
