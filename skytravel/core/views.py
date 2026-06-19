from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import Destination, Category, Review, Favorite, RecentlyViewed, Coupon, Notification
from .forms import ReviewForm, SearchForm
from tours.models import Tour, Hotel, Restaurant, Booking
from django.contrib.auth.models import User
from django.utils.text import slugify
import json

def home(request):
    featured_destinations = Destination.objects.filter(is_featured=True)[:8]
    popular_destinations = Destination.objects.filter(is_popular=True)[:10]
    trending_tours = Tour.objects.filter(is_trending=True, status='published')[:6]
    categories = Category.objects.all()
    context = {
        'featured_destinations': featured_destinations,
        'popular_destinations': popular_destinations,
        'trending_tours': trending_tours,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)

def destination_list(request):
    destinations = Destination.objects.all()
    category_slug = request.GET.get('category')
    if category_slug:
        destinations = destinations.filter(categories__slug=category_slug)
    sort = request.GET.get('sort', 'name')
    if sort == 'rating':
        destinations = destinations.order_by('-rating')
    elif sort == 'popular':
        destinations = destinations.order_by('-reviews_count')
    else:
        destinations = destinations.order_by('name')
    paginator = Paginator(destinations, 12)
    page = request.GET.get('page')
    destinations = paginator.get_page(page)
    categories = Category.objects.all()
    return render(request, 'core/destination_list.html', {
        'destinations': destinations, 'categories': categories, 'sort': sort
    })

def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    tours = Tour.objects.filter(destination=destination, status='published')
    hotels = Hotel.objects.filter(destination=destination)
    restaurants = Restaurant.objects.filter(destination=destination)
    reviews = Review.objects.filter(destination=destination, is_approved=True)
    if request.user.is_authenticated:
        RecentlyViewed.objects.create(user=request.user, destination=destination)
    context = {
        'destination': destination,
        'tours': tours,
        'hotels': hotels,
        'restaurants': restaurants,
        'reviews': reviews,
    }
    return render(request, 'core/destination_detail.html', context)

def search(request):
    form = SearchForm(request.GET or None)
    destinations = Destination.objects.all()
    tours = Tour.objects.filter(status='published')
    hotels = Hotel.objects.all()
    restaurants = Restaurant.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            destinations = destinations.filter(
                Q(name__icontains=q) | Q(country__icontains=q) | Q(description__icontains=q)
            )
            tours = tours.filter(
                Q(title__icontains=q) | Q(short_description__icontains=q) | Q(description__icontains=q)
            )
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        if min_price:
            tours = tours.filter(price__gte=min_price)
        if max_price:
            tours = tours.filter(price__lte=max_price)

    return render(request, 'core/search.html', {
        'form': form, 'destinations': destinations,
        'tours': tours, 'hotels': hotels, 'restaurants': restaurants
    })

@login_required
def recently_viewed(request):
    items = RecentlyViewed.objects.filter(user=request.user)[:30]
    return render(request, 'core/recently_viewed.html', {'items': items})

@login_required
def wishlist(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'core/wishlist.html', {'favorites': favorites})

@login_required
def wishlist_toggle(request, content_type, pk):
    model_map = {'destination': Destination, 'tour': Tour, 'hotel': Hotel, 'restaurant': Restaurant}
    model = model_map.get(content_type)
    if not model:
        messages.error(request, 'Invalid content type')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    obj = get_object_or_404(model, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        **{f'{content_type}': obj}
    )
    if not created:
        favorite.delete()
        messages.success(request, f'Removed from wishlist')
    else:
        messages.success(request, f'Added to wishlist')
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def review_create(request, content_type, pk):
    model_map = {'destination': Destination, 'tour': Tour, 'hotel': Hotel, 'restaurant': Restaurant}
    model = model_map.get(content_type)
    if not model:
        messages.error(request, 'Invalid content type')
        return redirect('/')
    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            setattr(review, content_type, obj)
            review.save()
            Notification.objects.create(
                user=obj.operator if hasattr(obj, 'operator') else request.user,
                notif_type='review_received',
                title=f'New review on {obj}',
                message=review.content[:200],
            )
            messages.success(request, 'Review submitted successfully!')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = ReviewForm()
    return render(request, 'core/review_form.html', {'form': form, 'obj': obj})

@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated!')
            return redirect('/')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'core/review_form.html', {'form': form, 'obj': review, 'edit': True})

@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect(request.META.get('HTTP_REFERER', '/'))

def review_helpful(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.helpful_votes += 1
    review.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

def blog_list(request):
    from .models import BlogPost
    posts = BlogPost.objects.filter(is_published=True)
    category = request.GET.get('category')
    if category:
        posts = posts.filter(category__iexact=category)
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    categories = BlogPost.CATEGORY_CHOICES
    return render(request, 'core/blog_list.html', {'posts': posts, 'categories': categories})

def blog_detail(request, slug):
    from .models import BlogPost
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3]
    return render(request, 'core/blog_detail.html', {'post': post, 'recent_posts': recent_posts})

def hotel_list(request):
    hotels = Hotel.objects.all()
    dest = request.GET.get('destination')
    min_p = request.GET.get('min_price')
    max_p = request.GET.get('max_price')
    if dest: hotels = hotels.filter(destination__slug=dest)
    if min_p: hotels = hotels.filter(price_per_night__gte=min_p)
    if max_p: hotels = hotels.filter(price_per_night__lte=max_p)
    return render(request, 'core/hotel_list.html', {'hotels': hotels})

def hotel_detail(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug)
    reviews = Review.objects.filter(hotel=hotel, is_approved=True)
    return render(request, 'core/hotel_detail.html', {'hotel': hotel, 'reviews': reviews})

def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'core/restaurant_list.html', {'restaurants': restaurants})

def restaurant_detail(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    reviews = Review.objects.filter(restaurant=restaurant, is_approved=True)
    return render(request, 'core/restaurant_detail.html', {'restaurant': restaurant, 'reviews': reviews})

@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user)
    return render(request, 'core/notifications.html', {'notifications': notifs})

@login_required
def notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('core:notifications')
