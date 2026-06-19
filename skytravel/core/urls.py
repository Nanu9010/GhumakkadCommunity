from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations/', views.destination_list, name='destination_list'),
    path('destination/<slug:slug>/', views.destination_detail, name='destination_detail'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<str:content_type>/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('reviews/create/<str:content_type>/<int:pk>/', views.review_create, name='review_create'),
    path('reviews/<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('review/<int:pk>/helpful/', views.review_helpful, name='review_helpful'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotel/<slug:slug>/', views.hotel_detail, name='hotel_detail'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<slug:slug>/', views.restaurant_detail, name='restaurant_detail'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:pk>/', views.notification_read, name='notification_read'),
    path('recently-viewed/', views.recently_viewed, name='recently_viewed'),
]
