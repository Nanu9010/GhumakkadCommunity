from django import forms
from .models import Review, Coupon

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content', 'image']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'star-rating'}),
            'title': forms.TextInput(attrs={'placeholder': 'Summarize your experience'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell others about your experience...'}),
        }

class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=50, label='Coupon Code',
                           widget=forms.TextInput(attrs={'placeholder': 'Enter coupon code'}))

class SearchForm(forms.Form):
    q = forms.CharField(max_length=200, required=False,
                        widget=forms.TextInput(attrs={'placeholder': 'Search destinations, tours, hotels...'}))
    category = forms.CharField(max_length=100, required=False)
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Max'}))
    rating = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'min': 1, 'max': 5}))
