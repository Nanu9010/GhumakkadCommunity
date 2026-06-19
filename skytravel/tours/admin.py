from django.contrib import admin
from .models import Tour, TourAvailability, TourSlot, Booking, Payment, Hotel, Restaurant, RoomType, HotelBooking, RestaurantBooking, CancellationPolicy

class TourSlotInline(admin.TabularInline):
    model = TourSlot
    extra = 1

class TourAvailabilityInline(admin.TabularInline):
    model = TourAvailability
    extra = 1
    show_change_link = True

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'operator', 'destination', 'price', 'status', 'rating', 'is_featured', 'is_trending', 'created_at']
    list_filter = ['status', 'is_featured', 'is_trending', 'destination']
    search_fields = ['title', 'operator__email', 'description']
    actions = ['approve_tours', 'reject_tours']

    def approve_tours(self, request, queryset):
        queryset.update(status='published')
    approve_tours.short_description = "Publish selected tours"

    def reject_tours(self, request, queryset):
        queryset.update(status='rejected')
    reject_tours.short_description = "Reject selected tours"

@admin.register(TourAvailability)
class TourAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['tour', 'date', 'is_available']
    list_filter = ['is_available']
    inlines = [TourSlotInline]

@admin.register(TourSlot)
class TourSlotAdmin(admin.ModelAdmin):
    list_display = ['availability', 'start_time', 'end_time', 'capacity', 'booked', 'available']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'tour', 'travel_date', 'travelers', 'total', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'tour__title']
    readonly_fields = ['booking_date']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'razorpay_order_id', 'amount', 'status', 'payment_method', 'paid_at']
    list_filter = ['status', 'payment_method']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'destination', 'price_per_night', 'rating', 'is_featured']
    list_filter = ['destination', 'is_featured']

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'destination', 'cuisine_type', 'price_range', 'rating']
    list_filter = ['cuisine_type', 'price_range', 'destination']

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'name', 'price_per_night', 'capacity', 'total_rooms', 'available_rooms']
    list_filter = ['hotel']

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'room_type', 'check_in', 'check_out', 'total', 'status']
    list_filter = ['status']
    search_fields = ['user__email', 'hotel__name']

@admin.register(RestaurantBooking)
class RestaurantBookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'booking_date', 'booking_time', 'meal_time', 'guests', 'status']
    list_filter = ['status', 'meal_time']
    search_fields = ['user__email', 'restaurant__name']

@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'days_before', 'refund_percentage']
    list_filter = ['content_type']
