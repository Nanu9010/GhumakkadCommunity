from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Destination, Category, CurrencyRate, BlogPost
from tours.models import Tour, Hotel, Restaurant
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Categories
        categories = [
            {'name': 'Beach', 'icon': 'umbrella'},
            {'name': 'Trekking', 'icon': 'signpost-2'},
            {'name': 'Heritage & Culture', 'icon': 'palette'},
            {'name': 'Food', 'icon': 'cup-hot'},
            {'name': 'Hill Station', 'icon': 'tree'},
            {'name': 'Pilgrimage', 'icon': 'heart'},
            {'name': 'Backwaters', 'icon': 'water'},
            {'name': 'Adventure', 'icon': 'lightning'},
        ]
        for cat_data in categories:
            Category.objects.get_or_create(**cat_data)
        self.stdout.write(f'  Created {len(categories)} categories')

        # Currencies
        currencies = [
            {'currency': 'INR', 'rate_to_inr': 1.0, 'symbol': '\u20b9'},
            {'currency': 'USD', 'rate_to_inr': 83.5, 'symbol': '$'},
            {'currency': 'EUR', 'rate_to_inr': 90.2, 'symbol': '\u20ac'},
            {'currency': 'GBP', 'rate_to_inr': 105.0, 'symbol': '\u00a3'},
        ]
        for c in currencies:
            CurrencyRate.objects.get_or_create(currency=c['currency'], defaults=c)
        self.stdout.write('  Created currencies')

        # Destinations
        dests_data = [
            # South India
            {'name': 'Hampi', 'country': 'India', 'description': 'UNESCO World Heritage Site with stunning ruins of the Vijayanagara Empire. Explore ancient temples, boulder-strewn landscapes, and the serene Tungabhadra River.', 'short_description': 'Ancient ruins and boulder landscapes', 'is_featured': True, 'is_popular': True, 'rating': 4.7, 'reviews_count': 4200, 'tours_count': 12, 'price_starting': 1200},
            {'name': 'Kerala Backwaters', 'country': 'India', 'description': 'Serene network of lagoons, lakes, and canals lined with palm trees. Glide through Alleppey houseboats and explore Munnar tea plantations.', 'short_description': 'Houseboats and emerald backwaters', 'is_featured': True, 'is_popular': True, 'rating': 4.8, 'reviews_count': 8500, 'tours_count': 18, 'price_starting': 3000},
            {'name': 'Gokarna', 'country': 'India', 'description': 'A serene temple town with pristine, uncrowded beaches. Trek between Om Beach, Kudle Beach, and Half Moon Beach.', 'short_description': 'Pristine beaches and temple town', 'is_featured': True, 'is_popular': True, 'rating': 4.5, 'reviews_count': 3100, 'tours_count': 8, 'price_starting': 1500},
            {'name': 'Coorg', 'country': 'India', 'description': 'The Scotland of India, draped in coffee plantations and misty hills. Visit Abbey Falls and explore Dubare Elephant Camp.', 'short_description': 'Coffee plantations and misty hills', 'is_featured': False, 'is_popular': True, 'rating': 4.6, 'reviews_count': 3800, 'tours_count': 10, 'price_starting': 2000},
            {'name': 'Pondicherry', 'country': 'India', 'description': 'A French colonial gem on the Coromandel Coast. Stroll through the colorful French Quarter and relax at Serenity Beach.', 'short_description': 'French colony and coastal charm', 'is_featured': False, 'is_popular': True, 'rating': 4.4, 'reviews_count': 2900, 'tours_count': 7, 'price_starting': 1800},
            # West India
            {'name': 'Sahyadri Forts', 'country': 'India', 'description': 'Maharashtra legendary hill forts steeped in Maratha history. Trek to Raigad, Rajgad, and Harihar Fort.', 'short_description': 'Maratha hill forts and history', 'is_featured': True, 'is_popular': True, 'rating': 4.7, 'reviews_count': 5200, 'tours_count': 14, 'price_starting': 1000},
            {'name': 'Kalsubai Trek', 'country': 'India', 'description': 'The highest peak in Maharashtra at 5,400 ft. A challenging trek with panoramic views of the Sahyadri range.', 'short_description': 'Maharashtra highest peak trek', 'is_featured': True, 'is_popular': True, 'rating': 4.6, 'reviews_count': 3500, 'tours_count': 6, 'price_starting': 800},
            {'name': 'Lonavala', 'country': 'India', 'description': 'A charming hill station in the Western Ghats. Visit Tiger Point, Bhushi Dam, and the ancient Karla Caves.', 'short_description': 'Western Ghats hill station', 'is_featured': False, 'is_popular': True, 'rating': 4.3, 'reviews_count': 6100, 'tours_count': 9, 'price_starting': 1500},
            # North India
            {'name': 'Spiti Valley', 'country': 'India', 'description': 'A cold desert mountain valley between India and Tibet. Explore ancient monasteries and camp at Chandratal Lake.', 'short_description': 'Cold desert and ancient monasteries', 'is_featured': True, 'is_popular': True, 'rating': 4.9, 'reviews_count': 4800, 'tours_count': 10, 'price_starting': 5000},
            {'name': 'Himachal Pradesh', 'country': 'India', 'description': 'India adventure capital with snow-capped peaks, pine forests, and vibrant culture from Manali to Shimla.', 'short_description': 'Snow peaks and adventure capital', 'is_featured': True, 'is_popular': True, 'rating': 4.7, 'reviews_count': 9200, 'tours_count': 22, 'price_starting': 3000},
            {'name': 'Kedarnath', 'country': 'India', 'description': 'One of the holiest Hindu pilgrimage sites dedicated to Lord Shiva in the Garhwal Himalayas.', 'short_description': 'Sacred Himalayan pilgrimage', 'is_featured': True, 'is_popular': True, 'rating': 4.8, 'reviews_count': 6500, 'tours_count': 8, 'price_starting': 4000},
            {'name': 'Rishikesh', 'country': 'India', 'description': 'The Yoga Capital of the World on the banks of the Ganges. Experience Ganga Aarti and river rafting.', 'short_description': 'Yoga capital and Ganga spirituality', 'is_featured': False, 'is_popular': True, 'rating': 4.5, 'reviews_count': 7800, 'tours_count': 15, 'price_starting': 2000},
        ]
        categories_list = list(Category.objects.all())
        for dd in dests_data:
            dest, created = Destination.objects.get_or_create(
                name=dd['name'], country=dd['country'],
                defaults={**dd}
            )
            if created and categories_list:
                dest.categories.add(random.choice(categories_list))
        self.stdout.write(f'  Created {len(dests_data)} destinations')

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
