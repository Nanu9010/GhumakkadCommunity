from django import forms
from .models import Tour, TourAvailability, TourSlot, Booking, Hotel, Restaurant

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['destination', 'title', 'short_description', 'description', 'price',
                   'discount_price', 'duration', 'max_guests', 'meeting_point',
                   'latitude', 'longitude', 'includes', 'excludes', 'what_to_bring',
                   'image', 'image_2', 'image_3', 'image_4', 'image_5']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'includes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Hotel pickup, Lunch, Guide...'}),
            'excludes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Personal expenses, Tips...'}),
            'what_to_bring': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comfortable shoes, Sunscreen...'}),
        }

class TourAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TourAvailability
        fields = ['date', 'is_available']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class TourSlotForm(forms.ModelForm):
    class Meta:
        model = TourSlot
        fields = ['start_time', 'end_time', 'capacity']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['travel_date', 'travelers', 'special_requests', 'contact_email', 'contact_phone']
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'travelers': forms.NumberInput(attrs={'min': 1, 'max': 20, 'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'destination', 'description', 'price_per_night', 'address',
                   'latitude', 'longitude', 'amenities', 'image', 'image_2', 'image_3']

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'destination', 'description', 'cuisine_type', 'price_range',
                   'address', 'latitude', 'longitude', 'image', 'menu_preview']
