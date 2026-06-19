from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Material icon name")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Destination(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    country = models.CharField(max_length=100)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='destinations/')
    image_2 = models.ImageField(upload_to='destinations/', blank=True)
    image_3 = models.ImageField(upload_to='destinations/', blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='destinations')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)
    tours_count = models.PositiveIntegerField(default=0)
    price_starting = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='INR')
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-is_popular', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.country}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:destination_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f"{self.name}, {self.country}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    tour = models.ForeignKey('tours.Tour', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    hotel = models.ForeignKey('tours.Hotel', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    restaurant = models.ForeignKey('tours.Restaurant', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='reviews/', blank=True)
    is_verified = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.rating}★"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, null=True, blank=True)
    tour = models.ForeignKey('tours.Tour', on_delete=models.CASCADE, null=True, blank=True)
    hotel = models.ForeignKey('tours.Hotel', on_delete=models.CASCADE, null=True, blank=True)
    restaurant = models.ForeignKey('tours.Restaurant', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        items = []
        if self.destination: items.append(self.destination.name)
        if self.tour: items.append(self.tour.title)
        if self.hotel: items.append(self.hotel.name)
        if self.restaurant: items.append(self.restaurant.name)
        return f"{self.user.email} - {', '.join(items)}"

class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, null=True, blank=True)
    tour = models.ForeignKey('tours.Tour', on_delete=models.CASCADE, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        verbose_name_plural = 'Recently viewed'

    def __str__(self):
        return f"{self.user.email} - {self.destination or self.tour}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=[('percent', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_cart_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class Notification(models.Model):
    NOTIF_TYPES = (
        ('booking_confirmed', 'Booking Confirmed'),
        ('payment_success', 'Payment Successful'),
        ('tour_approved', 'Tour Approved'),
        ('tour_rejected', 'Tour Rejected'),
        ('refund_processed', 'Refund Processed'),
        ('review_received', 'Review Received'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_notif_type_display()}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activity logs'

    def __str__(self):
        return f"{self.user} - {self.action}"

class AdminActionLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action_type = models.CharField(max_length=50)
    target_model = models.CharField(max_length=100)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.admin} - {self.action_type} on {self.target_model}"

class BlogPost(models.Model):
    CATEGORY_CHOICES = (
        ('travel_guides', 'Travel Guides'),
        ('food', 'Food'),
        ('adventure', 'Adventure'),
        ('luxury_travel', 'Luxury Travel'),
        ('budget_travel', 'Budget Travel'),
        ('hidden_gems', 'Hidden Gems'),
    )
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='blog/')
    content = models.TextField()
    excerpt = models.TextField(max_length=400, blank=True)
    is_published = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt:
            self.excerpt = self.content[:300]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class CurrencyRate(models.Model):
    currency = models.CharField(max_length=10, unique=True)
    rate_to_inr = models.DecimalField(max_digits=12, decimal_places=6)
    symbol = models.CharField(max_length=10, default='₹')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['currency']

    def __str__(self):
        return f"{self.currency} ({self.symbol})"
