from django.contrib import admin
from .models import Category, Destination, Review, Favorite, RecentlyViewed, Coupon, Notification, ActivityLog, AdminActionLog, CurrencyRate, BlogPost

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'icon', 'created_at']

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', 'country')}
    list_display = ['name', 'country', 'rating', 'reviews_count', 'tours_count', 'is_featured', 'is_popular']
    list_filter = ['country', 'is_featured', 'is_popular', 'categories']
    search_fields = ['name', 'country', 'description']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'destination', 'tour', 'is_verified', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified']
    search_fields = ['user__email', 'content']
    actions = ['approve_reviews', 'unapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_reviews.short_description = "Unapprove selected reviews"

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'tour', 'created_at']

@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'tour', 'viewed_at']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_cart_amount', 'usage_limit', 'used_count', 'is_active']
    list_filter = ['discount_type', 'is_active']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notif_type', 'title', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'created_at']
    list_filter = ['action']

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ['admin', 'action_type', 'target_model', 'created_at']
    list_filter = ['action_type']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published']

@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate_to_inr', 'symbol', 'is_active']
