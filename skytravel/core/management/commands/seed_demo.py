import os
import random
from io import BytesIO
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Destination, Category, CurrencyRate, BlogPost, Coupon, Review
from tours.models import Tour, Hotel, Restaurant, RoomType, TourAvailability, TourSlot, CancellationPolicy
from accounts.models import Profile, OperatorProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from datetime import date, time, timedelta
from decimal import Decimal


def make_image(name='demo.jpg', color='blue'):
    buf = BytesIO()
    Image.new('RGB', (800, 600), color).save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type='image/jpeg')


class Command(BaseCommand):
    help = 'Seeds the database with comprehensive demo data for live demo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding comprehensive demo data...'))

        # Categories
        categories_data = [
            {'name': 'Beach', 'icon': 'umbrella'},
            {'name': 'Trekking', 'icon': 'signpost-2'},
            {'name': 'Heritage & Culture', 'icon': 'palette'},
            {'name': 'Food', 'icon': 'cup-hot'},
            {'name': 'Hill Station', 'icon': 'tree'},
            {'name': 'Pilgrimage', 'icon': 'heart'},
            {'name': 'Backwaters', 'icon': 'water'},
            {'name': 'Adventure', 'icon': 'lightning'},
        ]
        cats = []
        for cd in categories_data:
            cat, _ = Category.objects.get_or_create(name=cd['name'], defaults=cd)
            cats.append(cat)
        self.stdout.write(f'  Created {len(cats)} categories')

        # Currencies
        currencies = [
            {'currency': 'INR', 'rate_to_inr': Decimal('1.000000'), 'symbol': '\u20b9'},
            {'currency': 'USD', 'rate_to_inr': Decimal('83.500000'), 'symbol': '$'},
            {'currency': 'EUR', 'rate_to_inr': Decimal('90.200000'), 'symbol': '\u20ac'},
            {'currency': 'GBP', 'rate_to_inr': Decimal('105.000000'), 'symbol': '\u00a3'},
        ]
        for c in currencies:
            CurrencyRate.objects.get_or_create(currency=c['currency'], defaults=c)
        self.stdout.write('  Created currencies')

        # Destinations
        dests_data = [
            # South India
            {'name': 'Hampi', 'country': 'India', 'description': 'UNESCO World Heritage Site with stunning ruins of the Vijayanagara Empire. Explore ancient temples, boulder-strewn landscapes, and the serene Tungabhadra River. A paradise for history buffs and rock climbers alike.', 'short_description': 'Ancient ruins and boulder landscapes', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.7'), 'reviews_count': 4200, 'tours_count': 12, 'price_starting': Decimal('1200'), 'latitude': 15.3350, 'longitude': 76.4600},
            {'name': 'Kerala Backwaters', 'country': 'India', 'description': 'Serene network of lagoons, lakes, and canals lined with palm trees. Glide through Alleppey houseboats, explore Munnar tea plantations, and witness the vibrant Theyyam performances of North Kerala.', 'short_description': 'Houseboats and emerald backwaters', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.8'), 'reviews_count': 8500, 'tours_count': 18, 'price_starting': Decimal('3000'), 'latitude': 9.4981, 'longitude': 76.3388},
            {'name': 'Gokarna', 'country': 'India', 'description': 'A serene temple town with pristine, uncrowded beaches. Trek between Om Beach, Kudle Beach, and Half Moon Beach. Perfect for travelers seeking Goa vibes without the crowds.', 'short_description': 'Pristine beaches and temple town', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.5'), 'reviews_count': 3100, 'tours_count': 8, 'price_starting': Decimal('1500'), 'latitude': 14.5196, 'longitude': 74.3164},
            {'name': 'Coorg', 'country': 'India', 'description': 'The Scotland of India, draped in coffee plantations and misty hills. Visit Abbey Falls, explore Dubare Elephant Camp, and trek to Tadiandamol peak for breathtaking views.', 'short_description': 'Coffee plantations and misty hills', 'is_featured': False, 'is_popular': True, 'rating': Decimal('4.6'), 'reviews_count': 3800, 'tours_count': 10, 'price_starting': Decimal('2000'), 'latitude': 12.3375, 'longitude': 75.8069},
            {'name': 'Pondicherry', 'country': 'India', 'description': 'A French colonial gem on the Coromandel Coast. Stroll through the colorful French Quarter, relax at Serenity Beach, explore Auroville, and savor Franco-Tamil cuisine.', 'short_description': 'French colony and coastal charm', 'is_featured': False, 'is_popular': True, 'rating': Decimal('4.4'), 'reviews_count': 2900, 'tours_count': 7, 'price_starting': Decimal('1800'), 'latitude': 11.9416, 'longitude': 79.8083},
            # West India
            {'name': 'Sahyadri Forts', 'country': 'India', 'description': 'Maharashtra\'s legendary hill forts steeped in Maratha history. Trek to Raigad, the capital of Chhatrapati Shivaji Maharaj, explore the impregnable Rajgad, and hike to the ruins of Harihar Fort.', 'short_description': 'Maratha hill forts and history', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.7'), 'reviews_count': 5200, 'tours_count': 14, 'price_starting': Decimal('1000'), 'latitude': 18.2700, 'longitude': 73.2500},
            {'name': 'Kalsubai Trek', 'country': 'India', 'description': 'The highest peak in Maharashtra at 5,400 ft. A challenging trek through lush green trails, rocky patches, and iron ladders with panoramic views of the Sahyadri range and backwaters of Arthur Lake.', 'short_description': 'Maharashtra\'s highest peak trek', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.6'), 'reviews_count': 3500, 'tours_count': 6, 'price_starting': Decimal('800'), 'latitude': 19.6011, 'longitude': 73.7171},
            {'name': 'Lonavala', 'country': 'India', 'description': 'A charming hill station nestled in the Western Ghats. Visit Tiger Point for valley views, enjoy Bhushi Dam in monsoon, explore Karla and Bhaja Caves, and relish the famous chikki.', 'short_description': 'Western Ghats hill station', 'is_featured': False, 'is_popular': True, 'rating': Decimal('4.3'), 'reviews_count': 6100, 'tours_count': 9, 'price_starting': Decimal('1500'), 'latitude': 18.7537, 'longitude': 73.4068},
            # North India
            {'name': 'Spiti Valley', 'country': 'India', 'description': 'A cold desert mountain valley nestled between India and Tibet. Explore ancient monasteries at Key and Tabo, visit the world\'s highest village Komic, and camp under a million stars at Chandratal Lake.', 'short_description': 'Cold desert and ancient monasteries', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.9'), 'reviews_count': 4800, 'tours_count': 10, 'price_starting': Decimal('5000'), 'latitude': 32.2432, 'longitude': 78.0300},
            {'name': 'Himachal Pradesh', 'country': 'India', 'description': 'India\'s adventure capital with snow-capped peaks, pine forests, and vibrant culture. From the bustling streets of Manali to the colonial charm of Shimla and the daring Rohtang Pass, Himachal has it all.', 'short_description': 'Snow peaks and adventure capital', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.7'), 'reviews_count': 9200, 'tours_count': 22, 'price_starting': Decimal('3000'), 'latitude': 31.1048, 'longitude': 77.1734},
            {'name': 'Kedarnath', 'country': 'India', 'description': 'One of the holiest Hindu pilgrimage sites dedicated to Lord Shiva, nestled at 11,755 ft in the Garhwal Himalayas. The trek through lush meadows and snow-capped peaks is a spiritual and physical journey.', 'short_description': 'Sacred Himalayan pilgrimage', 'is_featured': True, 'is_popular': True, 'rating': Decimal('4.8'), 'reviews_count': 6500, 'tours_count': 8, 'price_starting': Decimal('4000'), 'latitude': 30.7352, 'longitude': 79.0669},
            {'name': 'Rishikesh', 'country': 'India', 'description': 'The Yoga Capital of the World and a spiritual haven on the banks of the Ganges. Experience the mesmerizing Ganga Aarti at Triveni Ghat, go river rafting on rapids, and bungee jump at Mohan Chatti.', 'short_description': 'Yoga capital and Ganga spirituality', 'is_featured': False, 'is_popular': True, 'rating': Decimal('4.5'), 'reviews_count': 7800, 'tours_count': 15, 'price_starting': Decimal('2000'), 'latitude': 30.0869, 'longitude': 78.2676},
        ]
        dests = []
        colors = ['skyblue', 'coral', 'teal', 'gold', 'salmon', 'lavender', 'pink', 'indigo', 'olive', 'turquoise', 'brown', 'crimson']
        for i, dd in enumerate(dests_data):
            dest, created = Destination.objects.get_or_create(
                name=dd['name'], country=dd['country'],
                defaults={**dd, 'image': make_image(f'{dd["name"].lower().replace(" ", "_")}.jpg', colors[i % len(colors)])}
            )
            if created and cats:
                dest.categories.add(cats[i % len(cats)])
            dests.append(dest)
        self.stdout.write(f'  Created {len(dests)} destinations')

        # Admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@ghumakkadcommunity.com', 'admin123')
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.save()
            admin.profile.user_type = 'admin'
            admin.profile.email_verified = True
            admin.profile.save()
            self.stdout.write('  Created admin user (admin / admin123)')

        # Demo traveler
        if not User.objects.filter(username='traveler').exists():
            traveler = User.objects.create_user('traveler', 'traveler@ghumakkadcommunity.com', 'traveler123')
            traveler.first_name = 'Rahul'
            traveler.last_name = 'Sharma'
            traveler.save()
            traveler.profile.phone = '+919876543210'
            traveler.profile.country = 'India'
            traveler.profile.bio = 'Passionate traveler exploring the hidden gems of India.'
            traveler.profile.email_verified = True
            traveler.profile.save()
            self.stdout.write('  Created traveler user (traveler / traveler123)')

        # Demo operator
        if not User.objects.filter(username='operator').exists():
            op_user = User.objects.create_user('operator', 'operator@ghumakkadcommunity.com', 'operator123')
            op_user.first_name = 'Priya'
            op_user.last_name = 'Patel'
            op_user.save()
            op_user.profile.user_type = 'operator'
            op_user.profile.phone = '+919876543211'
            op_user.profile.country = 'India'
            op_user.profile.email_verified = True
            op_user.profile.save()
            OperatorProfile.objects.create(
                user=op_user,
                business_name='Ghumakkad Adventures',
                business_address='42 FC Road, Pune, Maharashtra',
                business_phone='+919876543211',
                business_email='info@ghumakkadadventures.in',
                business_license='LIC-MH-2024-001',
                tax_id='GST-27AABCS1234F1Z5',
                description='Premium tour operator specializing in treks, heritage walks, and offbeat experiences across India.',
                approval_status='approved',
            )
            self.stdout.write('  Created operator user (operator / operator123)')

        operator_user = User.objects.get(username='operator')

        # Tours
        tours_data = [
            # Hampi
            {'title': 'Hampi Heritage Walk', 'dest': 0, 'desc': 'A guided walking tour through the UNESCO ruins of Hampi. Visit the Virupaksha Temple, Vittala Temple with its iconic stone chariot, and the ancient Hazara Rama Temple. Learn about the glorious Vijayanagara Empire.', 'short': 'Guided walk through ancient ruins', 'price': 1500, 'duration': '6 Hours', 'max': 15, 'meeting': 'Virupaksha Temple, Hampi'},
            {'title': 'Hampi Sunrise Bicycle Tour', 'dest': 0, 'desc': 'Cycle through the boulder-strewn landscape at sunrise. Ride past the Matanga Hill, Hemakuta Group of Monuments, and along the Tungabhadra River. Includes breakfast at a local eatery.', 'short': 'Sunrise cycling through ruins', 'price': 1200, 'duration': '4 Hours', 'max': 12, 'meeting': 'Hampi Bazaar'},
            # Kerala
            {'title': 'Kerala Houseboat Experience', 'dest': 1, 'desc': 'Cruise through the tranquil backwaters of Alleppey on a traditional kettuvallam houseboat. Enjoy freshly prepared Kerala cuisine, watch village life go by, and sleep under the stars.', 'short': 'Luxury houseboat cruise through backwaters', 'price': 4500, 'duration': '1 Day', 'max': 8, 'meeting': 'Alleppey Finishing Point'},
            {'title': 'Munnar Tea Plantation Trek', 'dest': 1, 'desc': 'Trek through the emerald green tea plantations of Munnar. Visit a tea factory, walk through Eravikulam National Park to spot the Nilgiri Tahr, and enjoy panoramic views from Top Station.', 'short': 'Tea gardens and mountain trek', 'price': 2500, 'duration': '8 Hours', 'max': 15, 'meeting': 'Munnar Bus Stand'},
            # Gokarna
            {'title': 'Gokarna Beach Trek', 'dest': 2, 'desc': 'Trek along the stunning coastline from Om Beach to Half Moon Beach. Pass through rocky cliffs, hidden coves, and pristine beaches. Includes camping overnight at Kudle Beach with bonfire.', 'short': 'Coastal trek with beach camping', 'price': 1800, 'duration': '2 Days', 'max': 20, 'meeting': 'Gokarna Main Beach'},
            {'title': 'Om Beach Surfing & Camping', 'dest': 2, 'desc': 'Learn to surf at the iconic Om Beach with certified instructors. Evening beach camping with stargazing, storytelling, and fresh seafood BBQ under the stars.', 'short': 'Surfing lessons and beach camping', 'price': 2200, 'duration': '2 Days', 'max': 12, 'meeting': 'Om Beach Parking Area'},
            # Coorg
            {'title': 'Coorg Coffee Trail Trek', 'dest': 3, 'desc': 'Trek through aromatic coffee and spice plantations of Coorg. Visit Abbey Falls, explore the Namdroling Monastery, and enjoy a traditional Coorg meal at a local estate.', 'short': 'Coffee estates and waterfall trek', 'price': 2000, 'duration': '6 Hours', 'max': 10, 'meeting': 'Madikeri Bus Stand'},
            # Pondicherry
            {'title': 'Pondicherry French Colony Walk', 'dest': 4, 'desc': 'Walk through the colorful French Quarter with its colonial architecture, vibrant cafes, and hidden courtyards. Visit the Aurobindo Ashram, French War Memorial, and Serenity Beach.', 'short': 'French heritage and coastal charm', 'price': 1000, 'duration': '4 Hours', 'max': 20, 'meeting': 'White Town, Near Beach Road'},
            # Sahyadri Forts
            {'title': 'Raigad Fort Trek & History Tour', 'dest': 5, 'desc': 'Trek to the capital of Chhatrapati Shivaji Maharaj. Explore the royal palace ruins, Jagdishwar Temple, and the iconic Takmak Tok. Learn about Maratha history from expert guides.', 'short': 'Trek to Shivaji\'s capital fort', 'price': 1500, 'duration': '8 Hours', 'max': 25, 'meeting': 'Raigad Ropeway Base, Pachad'},
            {'title': 'Rajgad Fort Night Trek', 'dest': 5, 'desc': 'An adventurous night trek to the fortress where Shivaji Maharaj spent 25 years. Watch the sunrise from the peak, explore Suvela Machi and Padmavati Temple.', 'short': 'Night trek with sunrise at the fort', 'price': 1800, 'duration': '12 Hours', 'max': 20, 'meeting': 'Gunjavane Base Village'},
            # Kalsubai
            {'title': 'Kalsubai Sunrise Trek', 'dest': 6, 'desc': 'Conquer the highest peak in Maharashtra. Trek through the Kalsubai Harishchandragad Wildlife Sanctuary, climb iron ladders, and witness a breathtaking sunrise from 5,400 ft.', 'short': 'Summit Maharashtra\'s highest peak', 'price': 1200, 'duration': '10 Hours', 'max': 30, 'meeting': 'Bari Village, Base Camp'},
            # Lonavala
            {'title': 'Lonavala Tiger Point & Bhushi Dam', 'dest': 7, 'desc': 'Visit the iconic Tiger Point for panoramic valley views, enjoy the misty Bhushi Dam, explore the ancient Karla Caves, and taste the famous Lonavala chikki.', 'short': 'Hill station highlights tour', 'price': 1500, 'duration': '6 Hours', 'max': 20, 'meeting': 'Lonavala Railway Station'},
            # Spiti
            {'title': 'Spiti Valley Road Trip', 'dest': 8, 'desc': 'An epic 7-day road trip from Manali to Spiti. Visit Key Monastery, the highest village Komic, camp at Chandratal Lake, and explore the ancient Tabo Monastery. An unforgettable Himalayan adventure.', 'short': 'Epic 7-day Himalayan road trip', 'price': 15000, 'duration': '7 Days', 'max': 8, 'meeting': 'Manali Bus Stand'},
            # Himachal
            {'title': 'Manali to Rohtang Pass Tour', 'dest': 9, 'desc': 'Drive from Manali to the stunning Rohtang Pass at 13,051 ft. Enjoy snow activities, breathtaking views of the Pir Panjal range, and visit the scenic Solang Valley.', 'short': 'Snow-capped pass and valley tour', 'price': 3500, 'duration': '2 Days', 'max': 12, 'meeting': 'Manali Mall Road'},
            # Kedarnath
            {'title': 'Kedarnath Yatra Trek', 'dest': 10, 'desc': 'A sacred 16 km trek from Gaurikund to the ancient Kedarnath Temple dedicated to Lord Shiva. Walk through pine forests, glacial streams, and snow-capped peaks on this spiritual journey.', 'short': 'Sacred Himalayan pilgrimage trek', 'price': 8000, 'duration': '3 Days', 'max': 15, 'meeting': 'Gaurikund, Sonprayag'},
            # Rishikesh
            {'title': 'Rishikesh River Rafting & Camping', 'dest': 11, 'desc': 'Experience thrilling white-water rafting on the Ganges rapids (grades I-III). Includes beach camping, bonfire, cliff jumping, and the evening Ganga Aarti at Triveni Ghat.', 'short': 'Rafting on the Ganges and camping', 'price': 3000, 'duration': '2 Days', 'max': 20, 'meeting': 'Marine Drive, Rishikesh'},
        ]
        tour_colors = ['blue', 'green', 'cyan', 'orange', 'purple', 'navy', 'maroon', 'teal', 'brown', 'magenta', 'indigo', 'olive', 'coral', 'gold', 'salmon', 'skyblue']
        tours = []
        for i, td in enumerate(tours_data):
            dest = dests[td['dest']]
            tour, created = Tour.objects.get_or_create(
                title=td['title'],
                defaults={
                    'operator': operator_user,
                    'destination': dest,
                    'short_description': td['short'],
                    'description': td['desc'],
                    'price': Decimal(str(td['price'])),
                    'duration': td['duration'],
                    'max_guests': td['max'],
                    'meeting_point': td['meeting'],
                    'image': make_image(f'tour_{i}.jpg', tour_colors[i % len(tour_colors)]),
                    'status': 'published',
                    'is_featured': i < 6,
                    'is_trending': i < 8,
                    'rating': Decimal(str(round(random.uniform(4.2, 5.0), 1))),
                    'reviews_count': random.randint(50, 500),
                    'booking_count': random.randint(10, 200),
                    'includes': 'Guide, Insurance, Refreshments, Transport',
                    'excludes': 'Personal expenses, Tips, Camera fees',
                }
            )
            if created:
                for day_offset in range(7):
                    avail_date = date.today() + timedelta(days=day_offset + 1)
                    avail, _ = TourAvailability.objects.get_or_create(tour=tour, date=avail_date)
                    TourSlot.objects.get_or_create(
                        availability=avail,
                        start_time=time(6, 0),
                        end_time=time(12, 0),
                        defaults={'capacity': td['max'], 'booked': random.randint(0, 5)},
                    )
                    TourSlot.objects.get_or_create(
                        availability=avail,
                        start_time=time(14, 0),
                        end_time=time(20, 0),
                        defaults={'capacity': td['max'], 'booked': random.randint(0, 3)},
                    )
                CancellationPolicy.objects.get_or_create(
                    content_type='tour', object_id=tour.pk, days_before=30,
                    defaults={'refund_percentage': Decimal('90.00')}
                )
                CancellationPolicy.objects.get_or_create(
                    content_type='tour', object_id=tour.pk, days_before=14,
                    defaults={'refund_percentage': Decimal('50.00')}
                )
                CancellationPolicy.objects.get_or_create(
                    content_type='tour', object_id=tour.pk, days_before=7,
                    defaults={'refund_percentage': Decimal('25.00')}
                )
            tours.append(tour)
        self.stdout.write(f'  Created {len(tours)} tours with availabilities and slots')

        # Hotels
        hotel_data = [
            {'name': 'Evolve Back Hampi', 'dest': 0, 'desc': 'A luxury resort overlooking the Tungabhadra River with stunning views of the Hampi ruins. Features infinity pool, spa, and curated heritage experiences.', 'price': 12000, 'address': 'Evolve Back, Kamalapura, Hampi', 'amenities': 'WiFi, Pool, Spa, Restaurant, Heritage Walks, River View'},
            {'name': 'Kumarakom Lake Resort', 'dest': 1, 'desc': 'Heritage resort on the banks of Lake Vembanad in Kumarakom. Traditional Kerala architecture, Ayurvedic spa, houseboat rides, and authentic Kerala cuisine.', 'price': 10000, 'address': 'Kumarakom, Kottayam, Kerala', 'amenities': 'WiFi, Pool, Spa, Ayurveda, Houseboat, Restaurant, Lake View'},
            {'name': 'SwaSwara Gokarna', 'dest': 2, 'desc': 'A CGH Earth wellness retreat overlooking the Arabian Sea. Yoga, meditation, pottery classes, and organic farm-to-table dining in a serene beachfront setting.', 'price': 8000, 'address': 'Kudle Beach Road, Gokarna, Karnataka', 'amenities': 'WiFi, Beach Access, Yoga, Restaurant, Wellness, Meditation'},
            {'name': 'The Himalayan Spiti', 'dest': 8, 'desc': 'A cozy mountain lodge in Kaza with views of the Spiti River and surrounding peaks. Warm hospitality, local cuisine, and guided monastery tours.', 'price': 4500, 'address': 'Kaza, Spiti Valley, Himachal Pradesh', 'amenities': 'WiFi, Restaurant, Mountain View, Library, Guided Tours'},
            {'name': 'Taj Rishikesh Resort', 'dest': 11, 'desc': 'Luxury resort nestled in the foothills of the Himalayas along the Ganges. Features infinity pool, spa, yoga pavilion, and curated adventure activities.', 'price': 15000, 'address': 'Singthali, Rishikesh, Uttarakhand', 'amenities': 'WiFi, Pool, Spa, Gym, Restaurant, River View, Yoga, Adventure Sports'},
            {'name': 'Fort Jadhavghad', 'dest': 5, 'desc': 'A 17th-century Maratha fort converted into a heritage hotel. Relive the glory of the Maratha Empire with royal suites, fort walks, and traditional Maharashtra dining.', 'price': 9000, 'address': 'Jadhavwadi, Pune-Saswad Road, Maharashtra', 'amenities': 'WiFi, Restaurant, Heritage Walks, Pool, Fort View, Cultural Programs'},
        ]
        hotel_colors = ['gold', 'white', 'coral', 'turquoise', 'silver', 'navy']
        for i, hd in enumerate(hotel_data):
            hotel, created = Hotel.objects.get_or_create(
                name=hd['name'],
                defaults={
                    'destination': dests[hd['dest']],
                    'description': hd['desc'],
                    'price_per_night': Decimal(str(hd['price'])),
                    'address': hd['address'],
                    'amenities': hd['amenities'],
                    'image': make_image(f'hotel_{i}.jpg', hotel_colors[i % len(hotel_colors)]),
                    'rating': Decimal(str(round(random.uniform(4.2, 5.0), 1))),
                    'reviews_count': random.randint(100, 2000),
                    'is_featured': i < 3,
                }
            )
            if created:
                RoomType.objects.get_or_create(
                    hotel=hotel, name='Standard Room',
                    defaults={'price_per_night': hotel.price_per_night, 'capacity': 2, 'total_rooms': 10, 'available_rooms': 10, 'amenities': 'AC, WiFi, TV'}
                )
                RoomType.objects.get_or_create(
                    hotel=hotel, name='Deluxe Suite',
                    defaults={'price_per_night': hotel.price_per_night * Decimal('1.8'), 'capacity': 3, 'total_rooms': 5, 'available_rooms': 5, 'amenities': 'AC, WiFi, TV, Balcony, Mini Bar'}
                )
                RoomType.objects.get_or_create(
                    hotel=hotel, name='Premium Villa',
                    defaults={'price_per_night': hotel.price_per_night * Decimal('3.0'), 'capacity': 4, 'total_rooms': 2, 'available_rooms': 2, 'amenities': 'AC, WiFi, TV, Balcony, Mini Bar, Private Pool, Butler'}
                )
        self.stdout.write(f'  Created {len(hotel_data)} hotels with room types')

        # Restaurants
        rest_data = [
            {'name': 'Mango Tree Restaurant', 'dest': 0, 'desc': 'A beloved Hampi eatery serving authentic Karnataka thali, filter coffee, and North Karnataka specialties. Enjoy meals with a view of the Tungabhadra River.', 'cuisine': 'South Indian, Karnataka', 'price': 'budget', 'address': 'Hampi Bazaar, Hampi, Karnataka'},
            {'name': 'Backwater Cafe', 'dest': 1, 'desc': 'A charming houseboat restaurant serving fresh Kerala cuisine. Karimeen (pearl spot fish), appam with stew, and prawn curry while cruising the backwaters.', 'cuisine': 'Kerala, Seafood', 'price': 'mid', 'address': 'Alleppey Backwaters, Kerala'},
            {'name': 'Namaste Cafe', 'dest': 2, 'desc': 'An iconic beachside cafe in Gokarna serving Indian, Continental, and Israeli cuisine. Famous for its sunset views, live music, and relaxed vibe.', 'cuisine': 'Indian, Continental, Israeli', 'price': 'budget', 'address': 'Om Beach Road, Gokarna, Karnataka'},
            {'name': 'Spiti Kitchen', 'dest': 8, 'desc': 'A cozy eatery in Kaza serving hot Tibetan and Indian food. Try the thukpa, momos, and butter tea after a long day of exploring the cold desert.', 'cuisine': 'Tibetan, Indian, Spiti Local', 'price': 'budget', 'address': 'Kaza Market, Spiti Valley, Himachal Pradesh'},
            {'name': 'Chotiwala Restaurant', 'dest': 11, 'desc': 'A legendary Rishikesh eatery known for its authentic North Indian thali and Ayurvedic food. A must-visit for pilgrims and travelers alike.', 'cuisine': 'North Indian, Ayurvedic', 'price': 'mid', 'address': 'Laxman Jhula Road, Rishikesh, Uttarakhand'},
            {'name': 'Malabar Junction', 'dest': 1, 'desc': 'An elegant restaurant in Kochi serving the best of Malabar cuisine. Hyderabadi biryani, Malabar prawn curry, and traditional Kerala desserts.', 'cuisine': 'Malabar, Seafood, Biryani', 'price': 'premium', 'address': 'Fort Kochi, Kochi, Kerala'},
        ]
        rest_colors = ['red', 'blue', 'green', 'purple', 'orange', 'teal']
        for i, rd in enumerate(rest_data):
            Restaurant.objects.get_or_create(
                name=rd['name'],
                defaults={
                    'destination': dests[rd['dest']],
                    'description': rd['desc'],
                    'cuisine_type': rd['cuisine'],
                    'price_range': rd['price'],
                    'address': rd['address'],
                    'image': make_image(f'rest_{i}.jpg', rest_colors[i % len(rest_colors)]),
                    'rating': Decimal(str(round(random.uniform(4.3, 5.0), 1))),
                    'reviews_count': random.randint(200, 3000),
                    'is_featured': i < 3,
                }
            )
        self.stdout.write(f'  Created {len(rest_data)} restaurants')

        # Coupons
        Coupon.objects.get_or_create(
            code='WELCOME20',
            defaults={
                'description': 'Welcome discount for new users',
                'discount_type': 'percent',
                'discount_value': Decimal('20'),
                'min_cart_amount': Decimal('2000'),
                'max_discount': Decimal('2000'),
                'usage_limit': 100,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=90),
            }
        )
        Coupon.objects.get_or_create(
            code='FLAT500',
            defaults={
                'description': 'Flat 500 off on bookings above 5000',
                'discount_type': 'fixed',
                'discount_value': Decimal('500'),
                'min_cart_amount': Decimal('5000'),
                'usage_limit': 50,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=60),
            }
        )
        self.stdout.write('  Created 2 coupons')

        # Blog posts
        traveler_user = User.objects.get(username='traveler')
        blog_data = [
            {'title': 'Top 10 Treks in the Sahyadri Mountains', 'cat': 'adventure', 'content': 'The Sahyadri range, also known as the Western Ghats, offers some of the most spectacular trekking experiences in India. From the historic Raigad Fort trek to the challenging Kalsubai summit, the mountains are dotted with ancient forts, lush green valleys, and breathtaking waterfalls. The Rajgad-Torna trek is a favorite among history enthusiasts, while the Harishchandragad trek offers stunning views of the Konkan plains. monsoon treks here are magical, with cascading waterfalls and mist-covered peaks. Whether you are a beginner or an experienced trekker, the Sahyadri has something for everyone. Pack your hiking boots and head to Maharashtra for an unforgettable adventure.'},
            {'title': 'Kerala Backwater Houseboat Guide', 'cat': 'travel_guides', 'content': 'The Kerala backwaters are a unique ecosystem of lagoons, lakes, and canals that stretch over 900 km. The best way to experience this magical landscape is on a traditional kettuvallam houseboat. Start your journey from Alleppey, often called the Venice of the East, and cruise through narrow canals lined with coconut palms, paddy fields, and village life. Most houseboats come with bedrooms, a kitchen, and a deck for watching the sunset. Do not miss the freshly prepared Kerala cuisine on board, including karimeen pollichathu, prawn curry, and appam with stew. The monsoon season from June to September offers the most dramatic scenery, while the winter months from November to February are ideal for a relaxing cruise.'},
            {'title': 'Spiti Valley Road Trip: A Complete Itinerary', 'cat': 'travel_guides', 'content': 'Spiti Valley, nestled between India and Tibet, is one of the most remote and breathtaking regions in the Himalayas. Start your road trip from Manali and cross the Rohtang Pass and Atal Tunnel to reach Keylong. From there, drive through the dramatic landscapes of Sarchu, More Plains, and the iconic monasteries of Key and Tabo. Visit Komic, the highest village in the world connected by road, and camp under a million stars at Chandratal Lake. The best time to visit is from June to September when the roads are open. Pack warm clothes, sunscreen, and an adventurous spirit. Spiti is not just a destination; it is a transformation.'},
            {'title': 'Weekend Getaways from Mumbai and Pune', 'cat': 'hidden_gems', 'content': 'Mumbai and Pune are surrounded by incredible weekend destinations. Lonavala and Khandala offer misty hill views and ancient caves just 2 hours from Mumbai. For beach lovers, Alibaug and Kashid provide pristine shores and water sports. Adventure seekers can head to the Sahyadri forts like Raigad, Rajgad, or the challenging Kalsubai trek. Nature lovers will enjoy the coffee plantations of Coorg or the backwaters of Goa. If you want something offbeat, explore the Kaas Plateau during the monsoon or the ancient temples of Ajanta and Ellora. Each destination offers a unique escape from the city, and most are just a few hours drive away.'},
        ]
        for i, bd in enumerate(blog_data):
            BlogPost.objects.get_or_create(
                title=bd['title'],
                defaults={
                    'author': traveler_user,
                    'category': bd['cat'],
                    'image': make_image(f'blog_{i}.jpg', ['teal', 'orange', 'green', 'purple'][i]),
                    'content': bd['content'],
                    'is_published': True,
                }
            )
        self.stdout.write('  Created 4 blog posts')

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('\n--- DEMO ACCOUNTS ---'))
        self.stdout.write(self.style.SUCCESS('Admin:      admin / admin123'))
        self.stdout.write(self.style.SUCCESS('Traveler:   traveler / traveler123'))
        self.stdout.write(self.style.SUCCESS('Operator:   operator / operator123'))
        self.stdout.write(self.style.SUCCESS('---------------------'))
