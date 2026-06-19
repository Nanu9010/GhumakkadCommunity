from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from datetime import date, time, timedelta
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
import json, hashlib, hmac, razorpay
from .models import Tour, TourAvailability, TourSlot, Booking, Payment, Hotel, Restaurant, RoomType, HotelBooking, RestaurantBooking, CancellationPolicy
from .forms import BookingForm
from core.models import Coupon, Notification, ActivityLog
from core.invoice import generate_invoice

if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
else:
    razorpay_client = None

def tour_list(request):
    tours = Tour.objects.filter(status='published')
    destination = request.GET.get('destination')
    min_p = request.GET.get('min_price')
    max_p = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')
    if destination: tours = tours.filter(destination__slug=destination)
    if min_p: tours = tours.filter(price__gte=min_p)
    if max_p: tours = tours.filter(price__lte=max_p)
    if sort == 'price_low': tours = tours.order_by('price')
    elif sort == 'price_high': tours = tours.order_by('-price')
    elif sort == 'rating': tours = tours.order_by('-rating')
    else: tours = tours.order_by('-created_at')
    paginator = Paginator(tours, 9)
    page = request.GET.get('page')
    tours = paginator.get_page(page)
    return render(request, 'tours/tour_list.html', {'tours': tours, 'sort': sort})

def tour_detail(request, slug):
    tour = get_object_or_404(Tour, slug=slug, status='published')
    reviews = tour.reviews.filter(is_approved=True)
    available_dates = TourAvailability.objects.filter(tour=tour, date__gte=tour.created_at, is_available=True)[:30]
    similar_tours = Tour.objects.filter(destination=tour.destination, status='published').exclude(pk=tour.pk)[:4]
    if request.user.is_authenticated:
        from core.models import RecentlyViewed
        RecentlyViewed.objects.create(user=request.user, tour=tour)
    context = {
        'tour': tour,
        'reviews': reviews,
        'available_dates': available_dates,
        'similar_tours': similar_tours,
    }
    return render(request, 'tours/tour_detail.html', context)

@login_required
def booking_create(request, slug):
    tour = get_object_or_404(Tour, slug=slug, status='published')
    if request.method == 'POST':
        form = BookingForm(request.POST)
        slot_id = request.POST.get('slot_id')
        coupon_code = request.POST.get('coupon_code')
        if form.is_valid():
            slot = get_object_or_404(TourSlot, pk=slot_id, availability__tour=tour)
            travelers = form.cleaned_data['travelers']
            if slot.available < travelers:
                messages.error(request, f'Only {slot.available} spots left!')
                return redirect('tours:tour_detail', slug=slug)
            subtotal = tour.price * travelers
            discount = Decimal('0')
            coupon = None
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
                    if coupon.used_count >= coupon.usage_limit > 0:
                        messages.warning(request, 'Coupon usage limit reached')
                    elif subtotal < coupon.min_cart_amount:
                        messages.warning(request, f'Min cart amount is {coupon.min_cart_amount}')
                    else:
                        if coupon.discount_type == 'percent':
                            discount = subtotal * coupon.discount_value / 100
                            if coupon.max_discount:
                                discount = min(discount, coupon.max_discount)
                        else:
                            discount = coupon.discount_value
                        coupon.used_count += 1
                        coupon.save()
                except Coupon.DoesNotExist:
                    messages.warning(request, 'Invalid coupon code')
            taxable = subtotal - discount
            tax = taxable * Decimal('0.05')
            total = taxable + tax
            booking = form.save(commit=False)
            booking.user = request.user
            booking.tour = tour
            booking.slot = slot
            booking.subtotal = subtotal
            booking.discount = discount
            booking.tax = tax
            booking.total = total
            booking.coupon = coupon
            booking.status = 'pending'
            booking.save()
            slot.booked += travelers
            slot.save()
            ActivityLog.objects.create(
                user=request.user,
                action=f'Created booking #{booking.pk} for {tour.title}',
            )
            return redirect('tours:payment_page', booking_id=booking.pk)
    else:
        form = BookingForm(initial={'contact_email': request.user.email})
    return redirect('tours:tour_detail', slug=slug)

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'tours/booking_detail.html', {'booking': booking})

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()
        if booking.slot:
            booking.slot.booked -= booking.travelers
            booking.slot.save()
        Notification.objects.create(
            user=request.user,
            notif_type='refund_processed',
            title=f'Booking #{booking.pk} cancelled',
            message='Your cancellation has been processed. Refund will be initiated shortly.'
        )
        messages.success(request, 'Booking cancelled.')
    return redirect('tours:my_bookings')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tours/my_bookings.html', {'bookings': bookings})

@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if hasattr(booking, 'payment') and booking.payment.status == 'paid':
        messages.info(request, 'This booking is already paid.')
        return redirect('tours:booking_detail', pk=booking.pk)
    currency = 'INR'
    amount_paise = int(booking.total * 100)
    razorpay_order = razorpay_client.order.create({
        'amount': amount_paise,
        'currency': currency,
        'payment_capture': '1',
        'notes': {'booking_id': str(booking.pk)}
    })
    Payment.objects.update_or_create(
        booking=booking,
        defaults={
            'razorpay_order_id': razorpay_order['id'],
            'amount': booking.total,
            'currency': currency,
            'status': 'created',
        }
    )
    context = {
        'booking': booking,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount_paise,
        'currency': currency,
        'user': request.user,
    }
    return render(request, 'tours/payment.html', context)

@login_required
def payment_success(request):
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_signature = request.GET.get('razorpay_signature')
    if not razorpay_order_id:
        messages.error(request, 'Payment verification failed.')
        return redirect('/')
    try:
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
        return redirect('/')
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature,
    }
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = 'paid'
        payment.save()
        booking = payment.booking
        booking.status = 'confirmed'
        booking.save()
        try:
            generate_invoice(booking)
        except Exception:
            pass
        Notification.objects.create(
            user=booking.tour.operator,
            notif_type='booking_confirmed',
            title=f'New booking for {booking.tour.title}',
            message=f'{booking.user.email} booked {booking.travelers} spot(s) on {booking.travel_date}',
            link=f'/accounts/operator/bookings/'
        )
        Notification.objects.create(
            user=booking.user,
            notif_type='booking_confirmed',
            title=f'Booking #{booking.pk} confirmed!',
            message=f'Your booking for {booking.tour.title} is confirmed.',
            link=f'/tours/booking/{booking.pk}/'
        )
        messages.success(request, 'Payment successful! Booking confirmed.')
        return redirect('tours:booking_detail', pk=booking.pk)
    except razorpay.errors.SignatureVerificationError:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('tours:booking_detail', pk=payment.booking.pk)

@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        webhook_secret = settings.RAZORPAY_KEY_SECRET
        body = request.body
        signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        expected_sig = hmac.new(
            webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        if signature == expected_sig:
            data = json.loads(body)
            event = data.get('event')
            if event == 'payment.captured':
                payload = data.get('payload', {}).get('payment', {}).get('entity', {})
                order_id = payload.get('order_id')
                payment_id = payload.get('id')
                try:
                    payment = Payment.objects.get(razorpay_order_id=order_id)
                    payment.razorpay_payment_id = payment_id
                    payment.status = 'paid'
                    payment.save()
                    booking = payment.booking
                    booking.status = 'confirmed'
                    booking.save()
                except Payment.DoesNotExist:
                    pass
            elif event == 'payment.failed':
                payload = data.get('payload', {}).get('payment', {}).get('entity', {})
                order_id = payload.get('order_id')
                try:
                    payment = Payment.objects.get(razorpay_order_id=order_id)
                    payment.status = 'failed'
                    payment.save()
                except Payment.DoesNotExist:
                    pass
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'invalid'}, status=400)

def tour_compare(request):
    ids = request.GET.getlist('ids')
    tours = Tour.objects.filter(pk__in=ids, status='published') if ids else []
    return render(request, 'tours/tour_compare.html', {'tours': tours})

def hotel_room_list(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug)
    room_types = RoomType.objects.filter(hotel=hotel)
    return render(request, 'tours/hotel_room_list.html', {'hotel': hotel, 'room_types': room_types})

@login_required
def hotel_booking_create(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug)
    if request.method == 'POST':
        room_type_id = request.POST.get('room_type_id')
        check_in_str = request.POST.get('check_in')
        check_out_str = request.POST.get('check_out')
        rooms = int(request.POST.get('rooms', 1))
        guests = int(request.POST.get('guests', 1))
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone', '')
        special_requests = request.POST.get('special_requests', '')
        room_type = get_object_or_404(RoomType, pk=room_type_id, hotel=hotel)
        if room_type.available_rooms < rooms:
            messages.error(request, f'Only {room_type.available_rooms} rooms available.')
            return redirect('tours:hotel_room_list', slug=slug)
        check_in = date.fromisoformat(check_in_str)
        check_out = date.fromisoformat(check_out_str)
        nights = (check_out - check_in).days
        if nights < 1:
            messages.error(request, 'Check-out must be after check-in.')
            return redirect('tours:hotel_room_list', slug=slug)
        subtotal = room_type.price_per_night * nights * rooms
        tax = subtotal * Decimal('0.05')
        total = subtotal + tax
        booking = HotelBooking.objects.create(
            user=request.user,
            hotel=hotel,
            room_type=room_type,
            check_in=check_in,
            check_out=check_out,
            rooms=rooms,
            guests=guests,
            subtotal=subtotal,
            tax=tax,
            total=total,
            contact_email=contact_email,
            contact_phone=contact_phone,
            special_requests=special_requests,
            status='pending',
        )
        room_type.available_rooms -= rooms
        room_type.save()
        Notification.objects.create(
            user=request.user,
            notif_type='booking_confirmed',
            title=f'Hotel booking #{booking.pk} created',
            message=f'Your booking at {hotel.name} is pending confirmation.',
        )
        ActivityLog.objects.create(
            user=request.user,
            action=f'Created hotel booking #{booking.pk} for {hotel.name}',
        )
        messages.success(request, 'Hotel booking created successfully.')
        return redirect('tours:hotel_booking_detail', pk=booking.pk)
    return redirect('tours:hotel_room_list', slug=slug)

@login_required
def hotel_booking_detail(request, pk):
    booking = get_object_or_404(HotelBooking, pk=pk, user=request.user)
    return render(request, 'tours/hotel_booking_detail.html', {'booking': booking})

@login_required
def hotel_booking_cancel(request, pk):
    booking = get_object_or_404(HotelBooking, pk=pk, user=request.user)
    if booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()
        booking.room_type.available_rooms += booking.rooms
        booking.room_type.save()
        Notification.objects.create(
            user=request.user,
            notif_type='refund_processed',
            title=f'Hotel booking #{booking.pk} cancelled',
            message='Your hotel cancellation has been processed.',
        )
        messages.success(request, 'Hotel booking cancelled.')
    return redirect('tours:my_hotel_bookings')

@login_required
def my_hotel_bookings(request):
    bookings = HotelBooking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tours/my_hotel_bookings.html', {'bookings': bookings})

@login_required
def restaurant_booking_create(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    if request.method == 'POST':
        booking_date_str = request.POST.get('booking_date')
        booking_time_str = request.POST.get('booking_time')
        meal_time = request.POST.get('meal_time')
        guests = int(request.POST.get('guests', 2))
        contact_email = request.POST.get('contact_email')
        contact_phone = request.POST.get('contact_phone', '')
        special_requests = request.POST.get('special_requests', '')
        booking_date = date.fromisoformat(booking_date_str)
        hour, minute = map(int, booking_time_str.split(':'))
        booking_time = time(hour, minute)
        booking = RestaurantBooking.objects.create(
            user=request.user,
            restaurant=restaurant,
            booking_date=booking_date,
            booking_time=booking_time,
            meal_time=meal_time,
            guests=guests,
            contact_email=contact_email,
            contact_phone=contact_phone,
            special_requests=special_requests,
            status='pending',
        )
        Notification.objects.create(
            user=request.user,
            notif_type='booking_confirmed',
            title=f'Restaurant booking #{booking.pk} created',
            message=f'Your booking at {restaurant.name} is pending confirmation.',
        )
        ActivityLog.objects.create(
            user=request.user,
            action=f'Created restaurant booking #{booking.pk} for {restaurant.name}',
        )
        messages.success(request, 'Restaurant booking created successfully.')
        return redirect('tours:restaurant_booking_detail', pk=booking.pk)
    return redirect('tours:tour_detail', slug=slug)

@login_required
def restaurant_booking_detail(request, pk):
    booking = get_object_or_404(RestaurantBooking, pk=pk, user=request.user)
    return render(request, 'tours/restaurant_booking_detail.html', {'booking': booking})

@login_required
def my_restaurant_bookings(request):
    bookings = RestaurantBooking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tours/my_restaurant_bookings.html', {'bookings': bookings})

@login_required
def invoice_download(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    payment = generate_invoice(booking)
    if payment.invoice_pdf:
        return redirect(payment.invoice_pdf.url)
    messages.error(request, 'Invoice not available.')
    return redirect('tours:booking_detail', pk=booking.pk)

@login_required
def cancel_booking_with_refund(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status in ('confirmed', 'pending'):
        days_until_travel = (booking.travel_date - date.today()).days
        policies = CancellationPolicy.objects.filter(
            content_type='tour',
            object_id=booking.tour.pk,
            days_before__lte=days_until_travel
        ).order_by('-days_before')
        refund_percentage = Decimal('0')
        if policies.exists():
            policy = policies.first()
            refund_percentage = policy.refund_percentage
        refund_amount = booking.total * refund_percentage / Decimal('100')
        if refund_amount > 0:
            booking.status = 'refunded'
            if hasattr(booking, 'payment') and booking.payment.status == 'paid':
                booking.payment.status = 'refunded'
                booking.payment.save()
        else:
            booking.status = 'cancelled'
        booking.save()
        if booking.slot:
            booking.slot.booked -= booking.travelers
            booking.slot.save()
        Notification.objects.create(
            user=request.user,
            notif_type='refund_processed',
            title=f'Booking #{booking.pk} cancelled',
            message=f'Refund of ₹{refund_amount} processed.' if refund_amount > 0 else 'Booking cancelled (no refund).',
        )
        if refund_amount > 0:
            messages.success(request, f'Booking cancelled. Refund of ₹{refund_amount} initiated.')
        else:
            messages.success(request, 'Booking cancelled.')
    return redirect('tours:my_bookings')
