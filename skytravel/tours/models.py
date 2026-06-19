from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from core.models import Destination, Coupon

class Tour(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    )
    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tours')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='tours')
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='INR')
    duration = models.CharField(max_length=100, help_text="e.g. 3 Hours, 2 Days")
    max_guests = models.PositiveIntegerField(default=10)
    meeting_point = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    includes = models.TextField(blank=True, help_text="Comma separated")
    excludes = models.TextField(blank=True, help_text="Comma separated")
    what_to_bring = models.TextField(blank=True)
    image = models.ImageField(upload_to='tours/')
    image_2 = models.ImageField(upload_to='tours/', blank=True)
    image_3 = models.ImageField(upload_to='tours/', blank=True)
    image_4 = models.ImageField(upload_to='tours/', blank=True)
    image_5 = models.ImageField(upload_to='tours/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-is_trending', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.destination.name}-{self.pk or ''}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tours:tour_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class TourAvailability(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['tour', 'date']
        verbose_name_plural = 'Tour availabilities'
        ordering = ['date']

    def __str__(self):
        return f"{self.tour.title} - {self.date}"

class TourSlot(models.Model):
    availability = models.ForeignKey(TourAvailability, on_delete=models.CASCADE, related_name='slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=10)
    booked = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['start_time']

    @property
    def available(self):
        return self.capacity - self.booked

    def __str__(self):
        return f"{self.availability.tour.title} - {self.availability.date} {self.start_time}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(TourSlot, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField()
    travelers = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.tour.title} ({self.travel_date})"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    )
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    invoice_pdf = models.FileField(upload_to='invoices/', blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking} - {self.razorpay_order_id}"

class Hotel(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    amenities = models.TextField(blank=True, help_text="Comma separated: WiFi, Pool, Gym, etc.")
    image = models.ImageField(upload_to='tours/')
    image_2 = models.ImageField(upload_to='tours/', blank=True)
    image_3 = models.ImageField(upload_to='tours/', blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-rating']
        verbose_name_plural = 'Hotels'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.destination.name}")
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

    @property
    def amenities_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()] if self.amenities else []


class Restaurant(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='restaurants')
    description = models.TextField()
    cuisine_type = models.CharField(max_length=200, help_text="Comma separated")
    price_range = models.CharField(max_length=20, choices=[
        ('budget', 'Budget'), ('mid', 'Mid-Range'), ('premium', 'Premium'), ('luxury', 'Luxury')
    ], default='mid')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='tours/')
    menu_preview = models.TextField(blank=True, help_text="Comma separated signature dishes")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-rating']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.destination.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=200, help_text="e.g. Deluxe Room, Suite, Penthouse")
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2, help_text="Max guests")
    total_rooms = models.PositiveIntegerField(default=5)
    available_rooms = models.PositiveIntegerField(default=5)
    amenities = models.TextField(blank=True, help_text="Comma separated: AC, WiFi, TV, etc.")
    image = models.ImageField(upload_to='room_types/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price_per_night']

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class HotelBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    rooms = models.PositiveIntegerField(default=1)
    guests = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.hotel.name} ({self.check_in})"

    @property
    def nights(self):
        return (self.check_out - self.check_in).days


class RestaurantBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    MEAL_TIMES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurant_bookings')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    meal_time = models.CharField(max_length=20, choices=MEAL_TIMES)
    guests = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Restaurant bookings'

    def __str__(self):
        return f"{self.user.email} - {self.restaurant.name} ({self.booking_date})"


class CancellationPolicy(models.Model):
    TOUR = 'tour'
    HOTEL = 'hotel'
    CONTENT_TYPES = (
        (TOUR, 'Tour'),
        (HOTEL, 'Hotel'),
    )
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.PositiveIntegerField()
    days_before = models.PositiveIntegerField(help_text="Cancel this many days before to get this refund")
    refund_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-days_before']
        verbose_name_plural = 'Cancellation policies'

    def __str__(self):
        return f"{self.get_content_type_display()} #{self.object_id} - {self.days_before}d = {self.refund_percentage}%"
