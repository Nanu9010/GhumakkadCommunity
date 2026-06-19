from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from .models import (
    Category, Destination, Review, Favorite, RecentlyViewed,
    Coupon, Notification, ActivityLog, AdminActionLog, BlogPost, CurrencyRate
)


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        cat = Category.objects.create(name='Adventure', icon='hiking')
        self.assertEqual(cat.name, 'Adventure')
        self.assertEqual(cat.slug, 'adventure')

    def test_category_slug_auto_generated(self):
        cat = Category.objects.create(name='Beach Paradise')
        self.assertEqual(cat.slug, 'beach-paradise')

    def test_category_str(self):
        cat = Category.objects.create(name='Food & Dining')
        self.assertEqual(str(cat), 'Food & Dining')

    def test_category_ordering(self):
        Category.objects.create(name='Zebra')
        Category.objects.create(name='Apple')
        categories = list(Category.objects.values_list('name', flat=True))
        self.assertEqual(categories, ['Apple', 'Zebra'])


class DestinationModelTest(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile('test.jpg', b'fake image content', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa',
            country='India',
            description='Beautiful beaches',
            image=self.destination.image if hasattr(self, 'destination') and self.destination else self.image,
            is_featured=True,
            is_popular=True,
        )

    def test_destination_creation(self):
        self.assertEqual(self.destination.name, 'Goa')
        self.assertEqual(self.destination.country, 'India')

    def test_destination_slug_auto(self):
        dest = Destination(
            name='Manali', country='India', description='Mountain paradise', image=self.image
        )
        dest.save()
        self.assertEqual(dest.slug, 'manali-india')

    def test_destination_str(self):
        self.assertEqual(str(self.destination), 'Goa, India')

    def test_destination_get_absolute_url(self):
        url = self.destination.get_absolute_url()
        self.assertIn(self.destination.slug, url)

    def test_destination_ordering(self):
        Destination.objects.all().delete()
        d1 = Destination.objects.create(name='B', country='X', description='d', image=self.image, is_featured=False, is_popular=False)
        d2 = Destination.objects.create(name='A', country='Y', description='d', image=self.image, is_featured=True, is_popular=True)
        dests = list(Destination.objects.values_list('name', flat=True))
        self.assertEqual(dests[0], 'A')


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reviewer@example.com', username='reviewer', password='testpass123'
        )
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Manali', country='India', description='Snow capped mountains', image=self.image
        )

    def test_review_creation(self):
        review = Review.objects.create(
            user=self.user,
            destination=self.destination,
            rating=5,
            title='Amazing place!',
            content='Absolutely loved the mountains.',
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, 'Amazing place!')

    def test_review_str(self):
        review = Review.objects.create(
            user=self.user, destination=self.destination, rating=4, content='Great!'
        )
        self.assertIn('reviewer@example.com', str(review))

    def test_review_ordering(self):
        Review.objects.create(user=self.user, destination=self.destination, rating=3, content='Ok')
        Review.objects.create(user=self.user, destination=self.destination, rating=5, content='Amazing')
        reviews = list(Review.objects.values_list('rating', flat=True))
        self.assertEqual(reviews, [5, 3])


class FavoriteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', username='user', password='testpass123'
        )
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Paris', country='France', description='City of lights', image=self.image
        )

    def test_favorite_creation(self):
        fav = Favorite.objects.create(user=self.user, destination=self.destination)
        self.assertEqual(fav.user, self.user)

    def test_favorite_str(self):
        fav = Favorite.objects.create(user=self.user, destination=self.destination)
        self.assertIn('Paris', str(fav))


class RecentlyViewedModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', username='user', password='testpass123'
        )
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Tokyo', country='Japan', description='Land of rising sun', image=self.image
        )

    def test_recently_viewed_creation(self):
        rv = RecentlyViewed.objects.create(user=self.user, destination=self.destination)
        self.assertEqual(rv.user, self.user)
        self.assertEqual(rv.destination, self.destination)


class CouponModelTest(TestCase):
    def test_coupon_creation(self):
        coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percent',
            discount_value=Decimal('20'),
            min_cart_amount=Decimal('100'),
            usage_limit=10,
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
        )
        self.assertEqual(coupon.code, 'SAVE20')

    def test_coupon_str(self):
        coupon = Coupon.objects.create(
            code='FLAT50',
            discount_type='fixed',
            discount_value=Decimal('50'),
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
        )
        self.assertEqual(str(coupon), 'FLAT50')


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com', username='user', password='testpass123'
        )

    def test_notification_creation(self):
        notif = Notification.objects.create(
            user=self.user,
            notif_type='booking_confirmed',
            title='Booking Confirmed',
            message='Your booking is confirmed.',
        )
        self.assertFalse(notif.is_read)

    def test_notification_str(self):
        notif = Notification.objects.create(
            user=self.user,
            notif_type='payment_success',
            title='Payment Received',
            message='Payment successful.',
        )
        self.assertIn('Payment Successful', str(notif))


class ActivityLogModelTest(TestCase):
    def test_activity_log_creation(self):
        log = ActivityLog.objects.create(
            action='Login',
            details='User logged in',
            ip_address='127.0.0.1',
        )
        self.assertEqual(log.action, 'Login')


class BlogPostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='author@example.com', username='author', password='testpass123'
        )
        self.image = SimpleUploadedFile('blog.jpg', b'fake image', content_type='image/jpeg')

    def test_blog_post_creation(self):
        post = BlogPost.objects.create(
            title='Top 10 Travel Destinations',
            author=self.user,
            category='travel_guides',
            image=self.image,
            content='Discover the best places to visit this year.',
            is_published=True,
        )
        self.assertEqual(post.slug, 'top-10-travel-destinations')
        self.assertTrue(post.is_published)

    def test_blog_post_excerpt_auto(self):
        post = BlogPost.objects.create(
            title='Test Post',
            author=self.user,
            category='food',
            image=self.image,
            content='A' * 500,
        )
        self.assertEqual(len(post.excerpt), 300)

    def test_blog_post_str(self):
        post = BlogPost.objects.create(
            title='Amazing Travel Blog',
            author=self.user,
            category='hidden_gems',
            image=self.image,
            content='Content here',
        )
        self.assertEqual(str(post), 'Amazing Travel Blog')


class CurrencyRateModelTest(TestCase):
    def test_currency_rate_creation(self):
        cr = CurrencyRate.objects.create(
            currency='USD',
            rate_to_inr=Decimal('83.500000'),
            symbol='$',
        )
        self.assertEqual(cr.currency, 'USD')
        self.assertEqual(cr.symbol, '$')

    def test_currency_rate_str(self):
        cr = CurrencyRate.objects.create(
            currency='EUR',
            rate_to_inr=Decimal('90.500000'),
            symbol='€',
        )
        self.assertIn('EUR', str(cr))


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')

    def test_home_page_status(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        response = self.client.get(reverse('core:home'))
        self.assertTemplateUsed(response, 'core/home.html')

    def test_home_page_context(self):
        response = self.client.get(reverse('core:home'))
        self.assertIn('featured_destinations', response.context)
        self.assertIn('popular_destinations', response.context)
        self.assertIn('categories', response.context)


class DestinationListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.dest = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )

    def test_destination_list_status(self):
        response = self.client.get(reverse('core:destination_list'))
        self.assertEqual(response.status_code, 200)

    def test_destination_list_with_category_filter(self):
        cat = Category.objects.create(name='Beach')
        self.dest.categories.add(cat)
        response = self.client.get(reverse('core:destination_list') + '?category=beach')
        self.assertEqual(response.status_code, 200)

    def test_destination_list_sort_by_rating(self):
        response = self.client.get(reverse('core:destination_list') + '?sort=rating')
        self.assertEqual(response.status_code, 200)

    def test_destination_list_sort_by_popular(self):
        response = self.client.get(reverse('core:destination_list') + '?sort=popular')
        self.assertEqual(response.status_code, 200)


class DestinationDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.dest = Destination.objects.create(
            name='Manali', country='India', description='Mountains', image=self.image
        )

    def test_destination_detail_status(self):
        response = self.client.get(reverse('core:destination_detail', args=[self.dest.slug]))
        self.assertEqual(response.status_code, 200)

    def test_destination_detail_404(self):
        response = self.client.get(reverse('core:destination_detail', args=['nonexistent']))
        self.assertEqual(response.status_code, 404)

    def test_destination_detail_creates_recently_viewed(self):
        user = User.objects.create_user(email='user@test.com', username='user', password='pass')
        self.client.login(username='user', password='pass')
        self.client.get(reverse('core:destination_detail', args=[self.dest.slug]))
        self.assertTrue(RecentlyViewed.objects.filter(user=user, destination=self.dest).exists())


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )

    def test_search_empty(self):
        response = self.client.get(reverse('core:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_query(self):
        response = self.client.get(reverse('core:search') + '?q=Goa')
        self.assertEqual(response.status_code, 200)

    def test_search_with_price_filter(self):
        response = self.client.get(reverse('core:search') + '?min_price=1000&max_price=5000')
        self.assertEqual(response.status_code, 200)


class ReviewViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='reviewer@test.com', username='reviewer', password='pass123'
        )
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Paris', country='France', description='Romantic city', image=self.image
        )
        self.client.login(username='reviewer', password='pass123')

    def test_review_create_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('core:review_create', args=['destination', self.destination.pk]))
        self.assertNotEqual(response.status_code, 200)

    def test_review_create_get(self):
        response = self.client.get(reverse('core:review_create', args=['destination', self.destination.pk]))
        self.assertEqual(response.status_code, 200)

    def test_review_create_post(self):
        response = self.client.post(reverse('core:review_create', args=['destination', self.destination.pk]), {
            'rating': 5,
            'title': 'Amazing!',
            'content': 'Best trip ever.',
        })
        self.assertTrue(Review.objects.filter(user=self.user, destination=self.destination).exists())

    def test_review_edit(self):
        review = Review.objects.create(
            user=self.user, destination=self.destination, rating=4, content='Good'
        )
        response = self.client.post(reverse('core:review_edit', args=[review.pk]), {
            'rating': 5,
            'title': 'Updated',
            'content': 'Updated review',
        })
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)

    def test_review_delete(self):
        review = Review.objects.create(
            user=self.user, destination=self.destination, rating=3, content='Ok'
        )
        response = self.client.post(reverse('core:review_delete', args=[review.pk]))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_review_helpful(self):
        review = Review.objects.create(
            user=self.user, destination=self.destination, rating=5, content='Great'
        )
        response = self.client.get(reverse('core:review_helpful', args=[review.pk]))
        review.refresh_from_db()
        self.assertEqual(review.helpful_votes, 1)


class WishlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Tokyo', country='Japan', description='Amazing', image=self.image
        )
        self.client.login(username='user', password='pass123')

    def test_wishlist_empty(self):
        response = self.client.get(reverse('core:wishlist'))
        self.assertEqual(response.status_code, 200)

    def test_wishlist_toggle_add(self):
        response = self.client.post(reverse('core:wishlist_toggle', args=['destination', self.destination.pk]))
        self.assertTrue(Favorite.objects.filter(user=self.user, destination=self.destination).exists())

    def test_wishlist_toggle_remove(self):
        Favorite.objects.create(user=self.user, destination=self.destination)
        response = self.client.post(reverse('core:wishlist_toggle', args=['destination', self.destination.pk]))
        self.assertFalse(Favorite.objects.filter(user=self.user, destination=self.destination).exists())


class BlogViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='author@test.com', username='author', password='pass123'
        )
        self.image = SimpleUploadedFile('blog.jpg', b'fake image', content_type='image/jpeg')
        self.post = BlogPost.objects.create(
            title='Travel Tips',
            author=self.user,
            category='travel_guides',
            image=self.image,
            content='Useful tips for travelers.',
            is_published=True,
        )

    def test_blog_list(self):
        response = self.client.get(reverse('core:blog_list'))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail(self):
        response = self.client.get(reverse('core:blog_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_404_unpublished(self):
        self.post.is_published = False
        self.post.save()
        response = self.client.get(reverse('core:blog_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 404)

    def test_blog_filter_by_category(self):
        response = self.client.get(reverse('core:blog_list') + '?category=travel_guides')
        self.assertEqual(response.status_code, 200)


class HotelViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.dest = Destination.objects.create(
            name='Mumbai', country='India', description='City', image=self.image
        )
        self.hotel = MagicMock()
        self.hotel.__class__.__name__ = 'Hotel'
        from tours.models import Hotel
        self.hotel = Hotel.objects.create(
            name='Taj Hotel',
            destination=self.dest,
            description='Luxury stay',
            price_per_night=Decimal('5000'),
            address='Nariman Point',
            image=self.image,
        )

    def test_hotel_list(self):
        response = self.client.get(reverse('core:hotel_list'))
        self.assertEqual(response.status_code, 200)

    def test_hotel_detail(self):
        response = self.client.get(reverse('core:hotel_detail', args=[self.hotel.slug]))
        self.assertEqual(response.status_code, 200)


class RestaurantViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')
        self.dest = Destination.objects.create(
            name='Delhi', country='India', description='Capital', image=self.image
        )
        from tours.models import Restaurant
        self.restaurant = Restaurant.objects.create(
            name='Karim\'s',
            destination=self.dest,
            description='Mughlai food',
            cuisine_type='Mughlai',
            price_range='mid',
            address='Jama Masjid',
            image=self.image,
        )

    def test_restaurant_list(self):
        response = self.client.get(reverse('core:restaurant_list'))
        self.assertEqual(response.status_code, 200)

    def test_restaurant_detail(self):
        response = self.client.get(reverse('core:restaurant_detail', args=[self.restaurant.slug]))
        self.assertEqual(response.status_code, 200)


class NotificationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.client.login(username='user', password='pass123')

    def test_notifications_list(self):
        response = self.client.get(reverse('core:notifications'))
        self.assertEqual(response.status_code, 200)

    def test_notification_read(self):
        notif = Notification.objects.create(
            user=self.user,
            notif_type='booking_confirmed',
            title='Test',
            message='Test message',
        )
        response = self.client.get(reverse('core:notification_read', args=[notif.pk]))
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)


class TemplateTagsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.image = SimpleUploadedFile('test.jpg', b'fake image', content_type='image/jpeg')

    def test_star_range_filter(self):
        from .templatetags.travel_tags import star_range
        result = star_range(3.5)
        self.assertEqual(result['full'], range(3))
        self.assertEqual(result['half'], range(1))
        self.assertEqual(result['empty'], range(1))

    def test_multiply_filter(self):
        from .templatetags.travel_tags import multiply
        self.assertEqual(multiply(10, 5), 50.0)

    def test_subtract_filter(self):
        from .templatetags.travel_tags import subtract
        self.assertEqual(subtract(10, 3), 7.0)

    def test_percentage_filter(self):
        from .templatetags.travel_tags import percentage
        self.assertEqual(percentage(50, 200), 25)
        self.assertEqual(percentage(50, 0), 0)

    def test_currency_symbol(self):
        from .templatetags.travel_tags import currency_symbol
        self.assertEqual(currency_symbol('INR'), '₹')
        self.assertEqual(currency_symbol('USD'), '$')
        self.assertEqual(currency_symbol('EUR'), '€')
        self.assertEqual(currency_symbol('GBP'), '£')
        self.assertEqual(currency_symbol('XYZ'), '₹')


class ContextProcessorTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_site_settings_context(self):
        from .context_processors import site_settings
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = MagicMock()
        request.user.is_authenticated = False
        request.session = {}
        context = site_settings(request)
        self.assertIn('categories', context)
        self.assertIn('currencies', context)
        self.assertIn('RAZORPAY_KEY_ID', context)

    def test_convert_currency_same(self):
        from .context_processors import convert_currency
        result = convert_currency(100, 'INR', 'INR')
        self.assertEqual(result, 100)

    def test_convert_currency_different(self):
        from .context_processors import convert_currency
        CurrencyRate.objects.create(currency='USD', rate_to_inr=Decimal('83.500000'), symbol='$')
        CurrencyRate.objects.create(currency='INR', rate_to_inr=Decimal('1.000000'), symbol='₹')
        result = convert_currency(100, 'USD', 'INR')
        self.assertEqual(result, Decimal('8350.000000'))

    def test_convert_currency_missing_rate(self):
        from .context_processors import convert_currency
        result = convert_currency(100, 'XYZ', 'INR')
        self.assertEqual(result, 100)


class CouponApplyFormTest(TestCase):
    def test_coupon_apply_form_valid(self):
        from .forms import CouponApplyForm
        form = CouponApplyForm(data={'code': 'SAVE20'})
        self.assertTrue(form.is_valid())

    def test_coupon_apply_form_empty(self):
        from .forms import CouponApplyForm
        form = CouponApplyForm(data={'code': ''})
        self.assertFalse(form.is_valid())


class SearchFormTest(TestCase):
    def test_search_form_valid(self):
        from .forms import SearchForm
        form = SearchForm(data={'q': 'Goa'})
        self.assertTrue(form.is_valid())

    def test_search_form_optional_fields(self):
        from .forms import SearchForm
        form = SearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_search_form_with_price(self):
        from .forms import SearchForm
        form = SearchForm(data={'q': '', 'min_price': 1000, 'max_price': 5000})
        self.assertTrue(form.is_valid())


class ReviewFormTest(TestCase):
    def test_review_form_valid(self):
        from .forms import ReviewForm
        form = ReviewForm(data={'rating': 5, 'title': 'Great', 'content': 'Amazing experience'})
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_no_content(self):
        from .forms import ReviewForm
        form = ReviewForm(data={'rating': 5, 'title': 'Great', 'content': ''})
        self.assertFalse(form.is_valid())
