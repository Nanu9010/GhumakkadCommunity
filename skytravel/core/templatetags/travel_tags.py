from django import template
from django.db.models import Avg, Count
from core.models import Review
import math

register = template.Library()

@register.filter
def star_range(rating):
    rating = float(rating)
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return {'full': range(full), 'half': range(half), 'empty': range(empty)}

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def subtract(value, arg):
    return float(value) - float(arg)

@register.filter
def percentage(value, arg):
    if float(arg) == 0:
        return 0
    return round((float(value) / float(arg)) * 100)

@register.filter
def get_avg_rating(obj):
    reviews = Review.objects.filter(**{f'{obj._meta.model_name}': obj, 'is_approved': True})
    avg = reviews.aggregate(avg=Avg('rating'))['avg']
    return round(avg, 1) if avg else 0

@register.filter
def get_review_count(obj):
    return Review.objects.filter(**{f'{obj._meta.model_name}': obj, 'is_approved': True}).count()

@register.simple_tag
def currency_symbol(code):
    symbols = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£'}
    return symbols.get(code, '₹')
