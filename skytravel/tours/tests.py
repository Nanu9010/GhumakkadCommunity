from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from core.models import Destination, Coupon, Notification, ActivityLog
from .models import (
    Tour, TourAvailability, TourSlot, Booking, Payment,
    Hotel, Restaurant, RoomType, HotelBooking, RestaurantBooking,
    CancellationPolicy
)


class TourModelTest(TestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            email='operator@test.com', username='operator', password='pass123'
        )
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Paradise Tour',
            short_description='Enjoy the beaches',
            description='Full tour description',
            price=Decimal('2500'),
            duration='6 Hours',
            max_guests=20,
            image=self.image,
            status='published',
        )

    def test_tour_creation(self):
        self.assertEqual(self.tour.title, 'Beach Paradise Tour')
        self.assertEqual(self.tour.status, 'published')

    def test_tour_slug_auto(self):
        self.assertIn('beach-paradise-tour', self.tour.slug)

    def test_tour_str(self):
        self.assertEqual(str(self.tour), 'Beach Paradise Tour')

    def test_tour_get_absolute_url(self):
        url = self.tour.get_absolute_url()
        self.assertIn(self.tour.slug, url)

    def test_tour_default_values(self):
        tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='New Tour',
            short_description='Short desc',
            description='Description',
            price=Decimal('1000'),
            duration='3 Hours',
            image=self.image,
        )
        self.assertEqual(tour.status, 'draft')
        self.assertFalse(tour.is_featured)
        self.assertFalse(tour.is_trending)
        self.assertEqual(tour.reviews_count, 0)
        self.assertEqual(tour.booking_count, 0)


class TourAvailabilityModelTest(TestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            email='operator@test.com', username='operator', password='pass123'
        )
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Test Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('1000'),
            duration='4 Hours',
            image=self.image,
        )

    def test_availability_creation(self):
        avail = TourAvailability.objects.create(
            tour=self.tour,
            date=date.today() + timedelta(days=7),
        )
        self.assertTrue(avail.is_available)

    def test_availability_str(self):
        avail = TourAvailability.objects.create(
            tour=self.tour,
            date=date(2025, 12, 25),
        )
        self.assertIn('Test Tour', str(avail))

    def test_unique_together_constraint(self):
        d = date(2025, 6, 15)
        TourAvailability.objects.create(tour=self.tour, date=d)
        with self.assertRaises(Exception):
            TourAvailability.objects.create(tour=self.tour, date=d)


class TourSlotModelTest(TestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            email='operator@test.com', username='operator', password='pass123'
        )
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Test Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('1000'),
            duration='4 Hours',
            image=self.image,
        )
        self.availability = TourAvailability.objects.create(
            tour=self.tour,
            date=date.today() + timedelta(days=7),
        )

    def test_slot_creation(self):
        slot = TourSlot.objects.create(
            availability=self.availability,
            start_time=time(9, 0),
            end_time=time(15, 0),
            capacity=15,
        )
        self.assertEqual(slot.capacity, 15)
        self.assertEqual(slot.booked, 0)

    def test_slot_available_property(self):
        slot = TourSlot.objects.create(
            availability=self.availability,
            start_time=time(9, 0),
            end_time=time(15, 0),
            capacity=15,
            booked=5,
        )
        self.assertEqual(slot.available, 10)

    def test_slot_str(self):
        slot = TourSlot.objects.create(
            availability=self.availability,
            start_time=time(10, 0),
            end_time=time(16, 0),
            capacity=10,
        )
        self.assertIn('Test Tour', str(slot))


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.operator = User.objects.create_user(
            email='operator@test.com', username='operator', password='pass123'
        )
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('2000'),
            duration='5 Hours',
            image=self.image,
            status='published',
        )

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            tour=self.tour,
            travel_date=date.today() + timedelta(days=14),
            travelers=2,
            subtotal=Decimal('4000'),
            discount=Decimal('0'),
            tax=Decimal('200'),
            total=Decimal('4200'),
            contact_email='user@test.com',
            status='pending',
        )
        self.assertEqual(booking.travelers, 2)
        self.assertEqual(booking.status, 'pending')

    def test_booking_str(self):
        booking = Booking.objects.create(
            user=self.user,
            tour=self.tour,
            travel_date=date(2025, 8, 15),
            travelers=1,
            subtotal=Decimal('2000'),
            total=Decimal('2100'),
            contact_email='user@test.com',
        )
        self.assertIn('user@test.com', str(booking))


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.operator = User.objects.create_user(
            email='operator@test.com', username='operator', password='pass123'
        )
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('2000'),
            duration='5 Hours',
            image=self.image,
        )
        self.booking = Booking.objects.create(
            user=self.user,
            tour=self.tour,
            travel_date=date.today() + timedelta(days=14),
            travelers=1,
            subtotal=Decimal('2000'),
            total=Decimal('2100'),
            contact_email='user@test.com',
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            booking=self.booking,
            razorpay_order_id='order_123',
            amount=Decimal('2100'),
            status='created',
        )
        self.assertEqual(payment.status, 'created')

    def test_payment_str(self):
        payment = Payment.objects.create(
            booking=self.booking,
            razorpay_order_id='order_456',
            amount=Decimal('2100'),
        )
        self.assertIn('order_456', str(payment))


class HotelModelTest(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile('hotel.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Mumbai', country='India', description='City', image=self.image
        )

    def test_hotel_creation(self):
        hotel = Hotel.objects.create(
            name='Taj Hotel',
            destination=self.destination,
            description='Luxury stay',
            price_per_night=Decimal('8000'),
            address='Nariman Point',
            image=self.image,
        )
        self.assertEqual(hotel.name, 'Taj Hotel')
        self.assertIn('taj-hotel', hotel.slug)

    def test_hotel_str(self):
        hotel = Hotel.objects.create(
            name='Leela Palace',
            destination=self.destination,
            description='Premium',
            price_per_night=Decimal('12000'),
            address='BKC',
            image=self.image,
        )
        self.assertEqual(str(hotel), 'Leela Palace')


class RestaurantModelTest(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile('rest.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Delhi', country='India', description='Capital', image=self.image
        )

    def test_restaurant_creation(self):
        restaurant = Restaurant.objects.create(
            name='Bukhara',
            destination=self.destination,
            description='North Indian',
            cuisine_type='Mughlai, North Indian',
            price_range='premium',
            address='ITC Maurya',
            image=self.image,
        )
        self.assertEqual(restaurant.name, 'Bukhara')
        self.assertEqual(restaurant.price_range, 'premium')

    def test_restaurant_str(self):
        restaurant = Restaurant.objects.create(
            name='Karims',
            destination=self.destination,
            description='Mughlai',
            cuisine_type='Mughlai',
            price_range='budget',
            address='Jama Masjid',
            image=self.image,
        )
        self.assertEqual(str(restaurant), 'Karims')


class RoomTypeModelTest(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile('hotel.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.hotel = Hotel.objects.create(
            name='Taj Goa',
            destination=self.destination,
            description='Beach resort',
            price_per_night=Decimal('10000'),
            address='Candolim',
            image=self.image,
        )

    def test_room_type_creation(self):
        rt = RoomType.objects.create(
            hotel=self.hotel,
            name='Deluxe Suite',
            price_per_night=Decimal('12000'),
            capacity=3,
            total_rooms=10,
            available_rooms=8,
        )
        self.assertEqual(rt.name, 'Deluxe Suite')
        self.assertEqual(rt.available_rooms, 8)

    def test_room_type_str(self):
        rt = RoomType.objects.create(
            hotel=self.hotel,
            name='Standard Room',
            price_per_night=Decimal('6000'),
            capacity=2,
        )
        self.assertIn('Taj Goa', str(rt))
        self.assertIn('Standard Room', str(rt))


class HotelBookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='guest@test.com', username='guest', password='pass123'
        )
        self.image = SimpleUploadedFile('hotel.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.hotel = Hotel.objects.create(
            name='Taj Goa',
            destination=self.destination,
            description='Resort',
            price_per_night=Decimal('10000'),
            address='Candolim',
            image=self.image,
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            name='Suite',
            price_per_night=Decimal('15000'),
            capacity=3,
            total_rooms=5,
        )

    def test_hotel_booking_creation(self):
        booking = HotelBooking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type=self.room_type,
            check_in=date(2025, 8, 1),
            check_out=date(2025, 8, 4),
            rooms=1,
            guests=2,
            subtotal=Decimal('45000'),
            tax=Decimal('2250'),
            total=Decimal('47250'),
            contact_email='guest@test.com',
        )
        self.assertEqual(booking.status, 'pending')

    def test_hotel_booking_nights(self):
        booking = HotelBooking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type=self.room_type,
            check_in=date(2025, 8, 1),
            check_out=date(2025, 8, 4),
            rooms=1,
            guests=2,
            subtotal=Decimal('45000'),
            tax=Decimal('2250'),
            total=Decimal('47250'),
            contact_email='guest@test.com',
        )
        self.assertEqual(booking.nights, 3)

    def test_hotel_booking_str(self):
        booking = HotelBooking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type=self.room_type,
            check_in=date(2025, 9, 1),
            check_out=date(2025, 9, 3),
            rooms=1,
            guests=2,
            subtotal=Decimal('30000'),
            total=Decimal('31500'),
            contact_email='guest@test.com',
        )
        self.assertIn('guest@test.com', str(booking))


class RestaurantBookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='diner@test.com', username='diner', password='pass123'
        )
        self.image = SimpleUploadedFile('rest.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Delhi', country='India', description='Capital', image=self.image
        )
        self.restaurant = Restaurant.objects.create(
            name='Bukhara',
            destination=self.destination,
            description='North Indian',
            cuisine_type='Mughlai',
            price_range='premium',
            address='ITC Maurya',
            image=self.image,
        )

    def test_restaurant_booking_creation(self):
        booking = RestaurantBooking.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            booking_date=date(2025, 8, 15),
            booking_time=time(19, 30),
            meal_time='dinner',
            guests=4,
            contact_email='diner@test.com',
        )
        self.assertEqual(booking.meal_time, 'dinner')
        self.assertEqual(booking.status, 'pending')

    def test_restaurant_booking_str(self):
        booking = RestaurantBooking.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            booking_date=date(2025, 12, 25),
            booking_time=time(20, 0),
            meal_time='dinner',
            guests=2,
            contact_email='diner@test.com',
        )
        self.assertIn('diner@test.com', str(booking))


class CancellationPolicyModelTest(TestCase):
    def test_cancellation_policy_creation(self):
        policy = CancellationPolicy.objects.create(
            content_type='tour',
            object_id=1,
            days_before=7,
            refund_percentage=Decimal('50.00'),
        )
        self.assertEqual(policy.days_before, 7)
        self.assertEqual(policy.refund_percentage, Decimal('50.00'))

    def test_cancellation_policy_str(self):
        policy = CancellationPolicy.objects.create(
            content_type='tour',
            object_id=1,
            days_before=3,
            refund_percentage=Decimal('25.00'),
        )
        self.assertIn('25.00%', str(policy))


class TourListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.operator = User.objects.create_user(
            email='op@test.com', username='op', password='pass123'
        )
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('2000'),
            duration='5 Hours',
            image=self.image,
            status='published',
        )

    def test_tour_list_status(self):
        response = self.client.get(reverse('tours:tour_list'))
        self.assertEqual(response.status_code, 200)

    def test_tour_list_filter_by_destination(self):
        response = self.client.get(reverse('tours:tour_list') + f'?destination={self.destination.slug}')
        self.assertEqual(response.status_code, 200)

    def test_tour_list_filter_by_price(self):
        response = self.client.get(reverse('tours:tour_list') + '?min_price=1000&max_price=5000')
        self.assertEqual(response.status_code, 200)

    def test_tour_list_sort_price_low(self):
        response = self.client.get(reverse('tours:tour_list') + '?sort=price_low')
        self.assertEqual(response.status_code, 200)

    def test_tour_list_sort_price_high(self):
        response = self.client.get(reverse('tours:tour_list') + '?sort=price_high')
        self.assertEqual(response.status_code, 200)

    def test_tour_list_sort_rating(self):
        response = self.client.get(reverse('tours:tour_list') + '?sort=rating')
        self.assertEqual(response.status_code, 200)


class TourDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.operator = User.objects.create_user(
            email='op@test.com', username='op', password='pass123'
        )
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('2000'),
            duration='5 Hours',
            image=self.image,
            status='published',
        )

    def test_tour_detail_status(self):
        response = self.client.get(reverse('tours:tour_detail', args=[self.tour.slug]))
        self.assertEqual(response.status_code, 200)

    def test_tour_detail_404_draft(self):
        self.tour.status = 'draft'
        self.tour.save()
        response = self.client.get(reverse('tours:tour_detail', args=[self.tour.slug]))
        self.assertEqual(response.status_code, 404)

    def test_tour_detail_creates_recently_viewed(self):
        user = User.objects.create_user(email='u@test.com', username='u', password='pass')
        self.client.login(username='u', password='pass')
        self.client.get(reverse('tours:tour_detail', args=[self.tour.slug]))
        from core.models import RecentlyViewed
        self.assertTrue(RecentlyViewed.objects.filter(user=user, tour=self.tour).exists())


class BookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.operator = User.objects.create_user(
            email='op@test.com', username='op', password='pass123'
        )
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('2000'),
            duration='5 Hours',
            image=self.image,
            status='published',
        )
        self.availability = TourAvailability.objects.create(
            tour=self.tour,
            date=date.today() + timedelta(days=14),
        )
        self.slot = TourSlot.objects.create(
            availability=self.availability,
            start_time=time(9, 0),
            end_time=time(15, 0),
            capacity=10,
        )
        self.client.login(username='user', password='pass123')

    @patch('tours.views.razorpay_client')
    def test_booking_create_with_slot(self, mock_razorpay):
        mock_razorpay.order.create.return_value = {'id': 'order_test123'}
        response = self.client.post(reverse('tours:booking_create', args=[self.tour.slug]), {
            'travel_date': (date.today() + timedelta(days=14)).isoformat(),
            'travelers': 2,
            'contact_email': 'user@test.com',
            'contact_phone': '+911234567890',
            'slot_id': self.slot.pk,
        })
        self.assertTrue(Booking.objects.filter(user=self.user, tour=self.tour).exists())

    def test_booking_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('tours:booking_create', args=[self.tour.slug]))
        self.assertNotEqual(response.status_code, 200)

    def test_booking_cancel(self):
        self.slot.booked = 2
        self.slot.save()
        booking = Booking.objects.create(
            user=self.user,
            tour=self.tour,
            slot=self.slot,
            travel_date=date.today() + timedelta(days=14),
            travelers=2,
            subtotal=Decimal('4000'),
            total=Decimal('4200'),
            contact_email='user@test.com',
            status='confirmed',
        )
        response = self.client.post(reverse('tours:booking_cancel', args=[booking.pk]))
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')

    def test_my_bookings(self):
        response = self.client.get(reverse('tours:my_bookings'))
        self.assertEqual(response.status_code, 200)


class TourCompareViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.operator = User.objects.create_user(
            email='op@test.com', username='op', password='pass123'
        )
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )

    def test_compare_empty(self):
        response = self.client.get(reverse('tours:tour_compare'))
        self.assertEqual(response.status_code, 200)

    def test_compare_with_ids(self):
        t1 = Tour.objects.create(
            operator=self.operator, destination=self.destination,
            title='Tour 1', short_description='S1', description='D1',
            price=Decimal('1000'), duration='3h', image=self.image, status='published'
        )
        t2 = Tour.objects.create(
            operator=self.operator, destination=self.destination,
            title='Tour 2', short_description='S2', description='D2',
            price=Decimal('2000'), duration='5h', image=self.image, status='published'
        )
        response = self.client.get(reverse('tours:tour_compare') + f'?ids={t1.pk}&ids={t2.pk}')
        self.assertEqual(response.status_code, 200)


class HotelBookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('hotel.jpg', b'fake image', content_type='image/jpeg')
        self.user = User.objects.create_user(
            email='guest@test.com', username='guest', password='pass123'
        )
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.hotel = Hotel.objects.create(
            name='Taj Goa',
            destination=self.destination,
            description='Resort',
            price_per_night=Decimal('10000'),
            address='Candolim',
            image=self.image,
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            name='Deluxe',
            price_per_night=Decimal('10000'),
            capacity=2,
            total_rooms=5,
            available_rooms=5,
        )
        self.client.login(username='guest', password='pass123')

    def test_hotel_room_list(self):
        response = self.client.get(reverse('tours:hotel_room_list', args=[self.hotel.slug]))
        self.assertEqual(response.status_code, 200)

    def test_hotel_booking_create(self):
        response = self.client.post(reverse('tours:hotel_booking_create', args=[self.hotel.slug]), {
            'room_type_id': self.room_type.pk,
            'check_in': '2025-08-01',
            'check_out': '2025-08-03',
            'rooms': 1,
            'guests': 2,
            'contact_email': 'guest@test.com',
        })
        self.assertTrue(HotelBooking.objects.filter(user=self.user, hotel=self.hotel).exists())
        self.room_type.refresh_from_db()
        self.assertEqual(self.room_type.available_rooms, 4)

    def test_hotel_booking_cancel(self):
        self.room_type.available_rooms = 4
        self.room_type.save()
        booking = HotelBooking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type=self.room_type,
            check_in=date(2025, 8, 1),
            check_out=date(2025, 8, 3),
            rooms=1,
            guests=2,
            subtotal=Decimal('20000'),
            tax=Decimal('1000'),
            total=Decimal('21000'),
            contact_email='guest@test.com',
            status='confirmed',
        )
        response = self.client.post(reverse('tours:hotel_booking_cancel', args=[booking.pk]))
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.room_type.refresh_from_db()
        self.assertEqual(self.room_type.available_rooms, 5)

    def test_my_hotel_bookings(self):
        response = self.client.get(reverse('tours:my_hotel_bookings'))
        self.assertEqual(response.status_code, 200)


class RestaurantBookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('rest.jpg', b'fake image', content_type='image/jpeg')
        self.user = User.objects.create_user(
            email='diner@test.com', username='diner', password='pass123'
        )
        self.destination = Destination.objects.create(
            name='Delhi', country='India', description='Capital', image=self.image
        )
        self.restaurant = Restaurant.objects.create(
            name='Bukhara',
            destination=self.destination,
            description='North Indian',
            cuisine_type='Mughlai',
            price_range='premium',
            address='ITC Maurya',
            image=self.image,
        )
        self.client.login(username='diner', password='pass123')

    def test_restaurant_booking_create(self):
        response = self.client.post(reverse('tours:restaurant_booking_create', args=[self.restaurant.slug]), {
            'booking_date': '2025-08-15',
            'booking_time': '19:30',
            'meal_time': 'dinner',
            'guests': 4,
            'contact_email': 'diner@test.com',
        })
        self.assertTrue(RestaurantBooking.objects.filter(user=self.user, restaurant=self.restaurant).exists())

    def test_my_restaurant_bookings(self):
        response = self.client.get(reverse('tours:my_restaurant_bookings'))
        self.assertEqual(response.status_code, 200)


class PaymentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.operator = User.objects.create_user(
            email='op@test.com', username='op', password='pass123'
        )
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('2000'),
            duration='5 Hours',
            image=self.image,
            status='published',
        )
        self.booking = Booking.objects.create(
            user=self.user,
            tour=self.tour,
            travel_date=date.today() + timedelta(days=14),
            travelers=2,
            subtotal=Decimal('4000'),
            total=Decimal('4200'),
            contact_email='user@test.com',
            status='pending',
        )
        self.client.login(username='user', password='pass123')

    @patch('tours.views.razorpay_client')
    def test_payment_page(self, mock_razorpay):
        mock_razorpay.order.create.return_value = {'id': 'order_test123'}
        response = self.client.get(reverse('tours:payment_page', args=[self.booking.pk]))
        self.assertEqual(response.status_code, 200)

    def test_payment_page_already_paid(self):
        Payment.objects.create(
            booking=self.booking,
            razorpay_order_id='order_existing',
            amount=Decimal('4200'),
            status='paid',
        )
        response = self.client.get(reverse('tours:payment_page', args=[self.booking.pk]))
        self.assertNotEqual(response.status_code, 200)


class WebhookViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_webhook_invalid_method(self):
        response = self.client.get(reverse('tours:razorpay_webhook'))
        self.assertEqual(response.status_code, 400)

    def test_webhook_post(self):
        response = self.client.post(reverse('tours:razorpay_webhook'))
        self.assertEqual(response.status_code, 200)


class BookingFormTest(TestCase):
    def test_booking_form_valid(self):
        from .forms import BookingForm
        form = BookingForm(data={
            'travel_date': date.today() + timedelta(days=14),
            'travelers': 2,
            'contact_email': 'test@test.com',
        })
        self.assertTrue(form.is_valid())

    def test_booking_form_invalid(self):
        from .forms import BookingForm
        form = BookingForm(data={})
        self.assertFalse(form.is_valid())


class TourFormTest(TestCase):
    def test_tour_form_valid(self):
        from .forms import TourForm
        from io import BytesIO
        from PIL import Image
        buf = BytesIO()
        Image.new('RGB', (100, 100), 'blue').save(buf, format='JPEG')
        buf.seek(0)
        dest_image = SimpleUploadedFile('test.jpg', buf.read(), content_type='image/jpeg')
        dest = Destination.objects.create(
            name='Goa', country='India', description='Beaches',
            image=dest_image
        )
        buf.seek(0)
        tour_image = SimpleUploadedFile('tour.jpg', buf.read(), content_type='image/jpeg')
        form = TourForm(data={
            'destination': dest.pk,
            'title': 'Test Tour',
            'short_description': 'Short desc',
            'description': 'Full description',
            'price': 2000,
            'discount_price': '',
            'duration': '5 Hours',
            'max_guests': 10,
            'meeting_point': 'City Center',
        }, files={'image': tour_image})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")


class InvoiceGenerationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', username='user', password='pass123'
        )
        self.operator = User.objects.create_user(
            email='op@test.com', username='op', password='pass123'
        )
        self.image = SimpleUploadedFile('tour.jpg', b'fake image', content_type='image/jpeg')
        self.destination = Destination.objects.create(
            name='Goa', country='India', description='Beaches', image=self.image
        )
        self.tour = Tour.objects.create(
            operator=self.operator,
            destination=self.destination,
            title='Beach Tour',
            short_description='Short',
            description='Desc',
            price=Decimal('2000'),
            duration='5 Hours',
            image=self.image,
        )
        self.booking = Booking.objects.create(
            user=self.user,
            tour=self.tour,
            travel_date=date.today() + timedelta(days=14),
            travelers=2,
            subtotal=Decimal('4000'),
            discount=Decimal('0'),
            tax=Decimal('200'),
            total=Decimal('4200'),
            contact_email='user@test.com',
            status='confirmed',
        )

    def test_generate_invoice(self):
        from core.invoice import generate_invoice
        payment = generate_invoice(self.booking)
        self.assertIsNotNone(payment)
        self.assertTrue(payment.invoice_pdf)

    def test_generate_hotel_invoice(self):
        from core.invoice import generate_hotel_invoice
        hotel = Hotel.objects.create(
            name='Test Hotel',
            destination=self.destination,
            description='Hotel',
            price_per_night=Decimal('5000'),
            address='Test Address',
            image=self.image,
        )
        room_type = RoomType.objects.create(
            hotel=hotel,
            name='Standard',
            price_per_night=Decimal('5000'),
            capacity=2,
        )
        hotel_booking = HotelBooking.objects.create(
            user=self.user,
            hotel=hotel,
            room_type=room_type,
            check_in=date(2025, 8, 1),
            check_out=date(2025, 8, 3),
            rooms=1,
            guests=2,
            subtotal=Decimal('10000'),
            tax=Decimal('500'),
            total=Decimal('10500'),
            contact_email='user@test.com',
        )
        result = generate_hotel_invoice(hotel_booking)
        self.assertTrue(result)
