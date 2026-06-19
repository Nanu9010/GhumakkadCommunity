from decimal import Decimal
from django.conf import settings
from .models import Category, Notification, CurrencyRate


def convert_currency(amount, from_currency, to_currency):
    """Convert amount from one currency to another using CurrencyRate model"""
    if from_currency == to_currency:
        return amount
    try:
        from_rate = CurrencyRate.objects.get(currency=from_currency, is_active=True)
        to_rate = CurrencyRate.objects.get(currency=to_currency, is_active=True)
        amount_in_inr = Decimal(str(amount)) * from_rate.rate_to_inr
        return amount_in_inr / to_rate.rate_to_inr
    except CurrencyRate.DoesNotExist:
        return amount


def site_settings(request):
    categories = Category.objects.all()
    currencies = CurrencyRate.objects.filter(is_active=True)
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

    selected_currency_code = request.session.get('selected_currency', 'INR')
    try:
        selected_currency = CurrencyRate.objects.get(currency=selected_currency_code, is_active=True)
    except CurrencyRate.DoesNotExist:
        selected_currency = CurrencyRate.objects.filter(is_active=True).first()

    context = {
        'brand': {
            'name': 'Ghumakkad Community',
            'short_name': 'Ghumakkad',
            'tagline': "Let's Explore Together",
            'subtagline': 'Making Memories off the Map',
            'description': 'Ghumakkad Community is a Pune and Mumbai based travel community creating guided trips, shared adventures, and memorable journeys across India.',
            'location': 'Pune, Mumbai',
            'whatsapp_primary': '8468929062',
            'whatsapp_secondary': '9529792536',
            'whatsapp_display': '8468929062 / 9529792536',
            'instagram_handle': 'ghumakkad_community_official',
            'instagram_url': 'https://www.instagram.com/ghumakkad_community_official/',
            'logo': 'images/brand/ghumakkad-logo.png',
            'founders': [
                {
                    'name': 'Ranjeet Dalave',
                    'handle': 'ranjeetdalave_',
                    'image': 'images/brand/ranjeetdalave.jpg',
                    'bio': 'Founder of Ghumakkad Community and a mountain-loving trip host who helps travelers find their next story.',
                },
                {
                    'name': 'Vatsaru',
                    'handle': 'the_vatsaru',
                    'image': 'images/brand/the-vatsaru.jpg',
                    'bio': 'Founder of Ghumakkad Community, bringing people together through treks, trails, and offbeat escapes.',
                },
            ],
        },
        'categories': categories,
        'currencies': currencies,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        'unread_notifications': unread_notifications,
        'selected_currency': selected_currency,
        'currency_rate': selected_currency.rate_to_inr if selected_currency else Decimal('1'),
        'convert_price': lambda amount, from_cur='INR': (
            convert_currency(amount, from_cur, selected_currency.currency) if selected_currency else amount
        ),
    }
    return context
