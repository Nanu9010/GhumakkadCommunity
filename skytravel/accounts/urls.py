from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_update, name='profile_update'),
    path('operator/register/', views.operator_register, name='operator_register'),
    path('operator/dashboard/', views.operator_dashboard, name='operator_dashboard'),
    path('operator/tours/create/', views.operator_tour_create, name='operator_tour_create'),
    path('operator/tours/<int:pk>/edit/', views.operator_tour_edit, name='operator_tour_edit'),
    path('operator/tours/<int:pk>/', views.operator_tour_detail, name='operator_tour_detail'),
    path('operator/tours/', views.operator_tour_list, name='operator_tour_list'),
    path('operator/availability/<int:tour_id>/', views.operator_availability, name='operator_availability'),
    path('operator/bookings/', views.operator_bookings, name='operator_bookings'),
]
