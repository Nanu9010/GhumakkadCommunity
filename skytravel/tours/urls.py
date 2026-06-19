from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.tour_list, name='tour_list'),
    path('compare/', views.tour_compare, name='tour_compare'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-hotel-bookings/', views.my_hotel_bookings, name='my_hotel_bookings'),
    path('my-restaurant-bookings/', views.my_restaurant_bookings, name='my_restaurant_bookings'),
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('booking/<int:booking_id>/invoice/', views.invoice_download, name='invoice_download'),
    path('booking/<int:pk>/cancel-refund/', views.cancel_booking_with_refund, name='cancel_booking_with_refund'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('hotel/<slug:slug>/rooms/', views.hotel_room_list, name='hotel_room_list'),
    path('hotel/<slug:slug>/book/', views.hotel_booking_create, name='hotel_booking_create'),
    path('hotel/booking/<int:pk>/', views.hotel_booking_detail, name='hotel_booking_detail'),
    path('hotel/booking/<int:pk>/cancel/', views.hotel_booking_cancel, name='hotel_booking_cancel'),
    path('restaurant/<slug:slug>/book/', views.restaurant_booking_create, name='restaurant_booking_create'),
    path('restaurant/booking/<int:pk>/', views.restaurant_booking_detail, name='restaurant_booking_detail'),
    path('<slug:slug>/', views.tour_detail, name='tour_detail'),
    path('<slug:slug>/book/', views.booking_create, name='booking_create'),
]
