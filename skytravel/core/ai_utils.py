import json, os, logging
from django.conf import settings

logger = logging.getLogger(__name__)

def get_ai_client():
    """Initialize OpenAI client if API key is available, else return None"""
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return None
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        return client
    except ImportError:
        logger.warning('openai package not installed')
        return None
    except Exception as e:
        logger.error(f'Failed to init OpenAI: {e}')
        return None

def generate_itinerary(destination, days, budget, interests, currency='INR'):
    """Generate a travel itinerary using OpenAI"""
    client = get_ai_client()
    if not client:
        return _generate_fallback_itinerary(destination, days, budget, interests, currency)
    try:
        prompt = f"""Create a {days}-day travel itinerary for {destination} with a budget of {budget} {currency}.
Interests: {interests}.
Provide as JSON array with objects: day (number), title, description, activities (array), meals (array), estimated_cost.
Keep it practical and detailed."""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        text = response.choices[0].message.content
        text = text.strip().removeprefix('```json').removeprefix('```').removesuffix('```')
        return json.loads(text)
    except Exception as e:
        logger.error(f'OpenAI itinerary error: {e}')
        return _generate_fallback_itinerary(destination, days, budget, interests, currency)

def _generate_fallback_itinerary(destination, days, budget, interests, currency='INR'):
    """Generate a basic itinerary without AI"""
    import random
    budget_per_day = float(budget) / max(days, 1)
    itineraries = []
    for day in range(1, days + 1):
        itineraries.append({
            'day': day,
            'title': f'Day {day} - Explore {destination}',
            'description': f'Experience the best of {destination}',
            'activities': [f'Morning sightseeing in {destination}', f'Local cuisine tasting', f'Evening cultural show'],
            'meals': ['Breakfast at hotel', 'Local restaurant lunch', 'Dinner at premium restaurant'],
            'estimated_cost': round(budget_per_day, 2)
        })
    return itineraries

def get_recommendations(user, request=None):
    """Get personalized recommendations for a user based on their history"""
    from core.models import RecentlyViewed, Favorite
    from tours.models import Tour
    from django.db.models import Count

    # Get recently viewed tours/destinations
    viewed = RecentlyViewed.objects.filter(user=user).select_related('tour__destination', 'destination')
    viewed_tour_ids = set()
    viewed_dest_ids = set()
    for v in viewed:
        if v.tour_id: viewed_tour_ids.add(v.tour_id)
        if v.destination_id: viewed_dest_ids.add(v.destination_id)

    # Get favorites
    favs = Favorite.objects.filter(user=user)
    fav_tour_ids = set(f.tour_id for f in favs if f.tour_id)

    # Get trending tours in similar categories/destinations
    all_interest_ids = viewed_dest_ids | set()

    # Recommend tours from viewed/favorited destinations
    from tours.models import Tour
    recommendations = Tour.objects.filter(status='published')

    dest_ids = viewed_dest_ids
    if dest_ids:
        from core.models import Destination
        rec_dests = Destination.objects.filter(id__in=dest_ids)
        recommendations = recommendations.filter(destination__in=rec_dests)

    exclude_ids = viewed_tour_ids | fav_tour_ids
    if exclude_ids:
        recommendations = recommendations.exclude(id__in=exclude_ids)

    recommendations = recommendations.order_by('-is_trending', '-rating')[:6]

    # Get popular destinations user hasn't seen
    from core.models import Destination
    popular = Destination.objects.filter(is_popular=True)
    if dest_ids:
        popular = popular.exclude(id__in=dest_ids)
    popular = popular[:4]

    return {
        'recommended_tours': recommendations,
        'popular_destinations': popular,
    }
