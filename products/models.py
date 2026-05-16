from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit

class Category(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', verbose_name=_('parent category'))
    image = ProcessedImageField(
        verbose_name=_('image'),
        upload_to='categories/',
        processors=[ResizeToFit(1200, 1200)],
        format='WEBP',
        options={'quality': 85},
        null=True, blank=True
    )
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 400)],
        format='WEBP',
        options={'quality': 80}
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_list') + f'?category={self.slug}'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

class Product(models.Model):
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(_('description'))
    base_price = models.DecimalField(_('base price'), max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_('category'))
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def get_average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if not reviews:
            return 0
        return sum([review.rating for review in reviews]) / reviews.count()

    def get_review_count(self):
        return self.reviews.filter(is_approved=True).count()

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name=_('product'))
    size = models.CharField(_('size'), max_length=50)
    color = models.CharField(_('color'), max_length=50)
    stock = models.PositiveIntegerField(_('stock'), default=0)
    price_modifier = models.DecimalField(_('price modifier'), max_digits=10, decimal_places=2, default=0.00, help_text=_("Amount added to base price"))

    class Meta:
        verbose_name = _('product variant')
        verbose_name_plural = _('product variants')

    def __str__(self):
        return f"{self.product.name} - {self.size} / {self.color}"
    
    @property
    def final_price(self):
        return self.product.base_price + self.price_modifier

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('product'))
    image = ProcessedImageField(
        verbose_name=_('image'),
        upload_to='products/',
        processors=[ResizeToFit(1600, 1600)],
        format='WEBP',
        options={'quality': 85}
    )
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(600, 750)],
        format='WEBP',
        options={'quality': 80}
    )
    alt_text = models.CharField(_('alt text'), max_length=255, blank=True, null=True)
    is_main = models.BooleanField(_('is main'), default=False)

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')

    def __str__(self):
        return f"Image for {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('product'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('user'))
    rating = models.PositiveSmallIntegerField(_('rating'), choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(_('comment'))
    is_approved = models.BooleanField(_('is approved'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
