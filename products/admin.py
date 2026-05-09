from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductVariant, ProductImage, Review

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline, ReviewInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Les avis sélectionnés ont été approuvés.")
    approve_reviews.short_description = "Approuver les avis"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Les avis sélectionnés ont été rejetés.")
    reject_reviews.short_description = "Rejeter (Désapprouver) les avis"

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock', 'availability')
    list_filter = ('product', 'size', 'color')
    
    def availability(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: red; font-weight: bold;">Rupture</span>')
        elif obj.stock <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">Faible</span>')
        return format_html('<span style="color: green;">OK</span>')
    availability.short_description = 'Statut Stock'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
