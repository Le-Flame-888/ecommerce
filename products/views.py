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
        
    # Advanced Filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    color = request.GET.get('color')
    size = request.GET.get('size')
    
    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)
    if color:
        products = products.filter(variants__color__iexact=color).distinct()
    if size:
        products = products.filter(variants__size__iexact=size).distinct()

    # Enhanced Search
    query = request.GET.get('q', '')
    if query:
        words = query.split()
        q_objects = Q()
        for word in words:
            q_objects |= Q(name__icontains=word) | Q(description__icontains=word)
        products = products.filter(q_objects)
        
        # Relevance Ranking: Name matches are more important
        # We can use Case/When for weighting in complex scenarios, 
        # but for SQLite, we'll use a simplified distinct ordering.
        products = products.order_by('-id').distinct()

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('base_price')
    elif sort == 'price_desc':
        products = products.order_by('-base_price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        if not query: # Only use default sort if not searching
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
        'min_price': min_price,
        'max_price': max_price,
        'current_color': color,
        'current_size': size,
    })

from django.contrib import messages
from .forms import ReviewForm

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]
    
    reviews = product.reviews.all()
    
    if request.method == 'POST' and request.user.is_authenticated:
        # Check if user already reviewed this product
        if product.reviews.filter(user=request.user).exists():
            messages.error(request, "Vous avez déjà laissé un avis sur ce produit.")
            return redirect('products:product_detail', slug=slug)
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Merci pour votre avis !")
            return redirect('products:product_detail', slug=slug)
    else:
        form = ReviewForm()
        
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'form': form,
    })
