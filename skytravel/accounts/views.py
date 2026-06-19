from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, OperatorProfile, VerificationDocument
from .forms import ProfileUpdateForm, UserUpdateForm, OperatorProfileForm, VerificationDocumentForm
from tours.models import Tour, Booking
from core.models import Review, Notification

@login_required
def dashboard(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    bookings = Booking.objects.filter(user=user)[:5]
    reviews = Review.objects.filter(user=user)[:5]
    favorites = user.favorites.all()[:5]
    unread_notifs = Notification.objects.filter(user=user, is_read=False).count()
    context = {
        'profile': profile,
        'bookings': bookings,
        'reviews': reviews,
        'favorites': favorites,
        'unread_notifications': unread_notifs,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated!')
            return redirect('accounts:dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'accounts/profile_form.html', {'u_form': u_form, 'p_form': p_form})

@login_required
def operator_register(request):
    profile = request.user.profile
    if profile.user_type != 'operator':
        profile.user_type = 'operator'
        profile.save()
    operator_profile, created = OperatorProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OperatorProfileForm(request.POST, instance=operator_profile)
        doc_form = VerificationDocumentForm(request.POST, request.FILES)
        if form.is_valid() and doc_form.is_valid():
            form.save()
            doc = doc_form.save(commit=False)
            doc.operator = operator_profile
            doc.save()
            Notification.objects.create(
                user=request.user,
                notif_type='tour_approved',
                title='Verification documents submitted',
                message='Your documents are under review. We will notify you once verified.'
            )
            messages.success(request, 'Application submitted! Wait for admin verification.')
            return redirect('accounts:operator_dashboard')
    else:
        form = OperatorProfileForm(instance=operator_profile)
        doc_form = VerificationDocumentForm()
    return render(request, 'accounts/operator_register.html', {'form': form, 'doc_form': doc_form})

@login_required
def operator_dashboard(request):
    operator_profile = get_object_or_404(OperatorProfile, user=request.user)
    tours = Tour.objects.filter(operator=request.user)
    bookings = Booking.objects.filter(tour__in=tours)
    total_revenue = sum(b.total for b in bookings.filter(status='confirmed'))
    context = {
        'operator_profile': operator_profile,
        'tours': tours,
        'total_tours': tours.count(),
        'total_bookings': bookings.count(),
        'total_revenue': total_revenue,
        'recent_bookings': bookings.order_by('-created_at')[:10],
    }
    return render(request, 'accounts/operator_dashboard.html', context)

@login_required
def operator_tour_list(request):
    tours = Tour.objects.filter(operator=request.user)
    return render(request, 'accounts/operator_tour_list.html', {'tours': tours})

@login_required
def operator_tour_create(request):
    if request.method == 'POST':
        from tours.forms import TourForm
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.operator = request.user
            tour.save()
            messages.success(request, 'Tour created! Submit for review.')
            return redirect('accounts:operator_tour_detail', pk=tour.pk)
    else:
        from tours.forms import TourForm
        form = TourForm()
    return render(request, 'accounts/operator_tour_form.html', {'form': form, 'edit': False})

@login_required
def operator_tour_edit(request, pk):
    tour = get_object_or_404(Tour, pk=pk, operator=request.user)
    if request.method == 'POST':
        from tours.forms import TourForm
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour updated!')
            return redirect('accounts:operator_tour_detail', pk=tour.pk)
    else:
        from tours.forms import TourForm
        form = TourForm(instance=tour)
    return render(request, 'accounts/operator_tour_form.html', {'form': form, 'edit': True, 'tour': tour})

@login_required
def operator_tour_detail(request, pk):
    tour = get_object_or_404(Tour, pk=pk, operator=request.user)
    return render(request, 'accounts/operator_tour_detail.html', {'tour': tour})

@login_required
def operator_availability(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id, operator=request.user)
    from tours.forms import TourAvailabilityForm, TourSlotForm
    if request.method == 'POST':
        form = TourAvailabilityForm(request.POST)
        slot_form = TourSlotForm(request.POST)
        if form.is_valid() and slot_form.is_valid():
            availability = form.save(commit=False)
            availability.tour = tour
            availability.save()
            slot = slot_form.save(commit=False)
            slot.availability = availability
            slot.save()
            messages.success(request, 'Availability added!')
            return redirect('accounts:operator_availability', tour_id=tour_id)
    else:
        form = TourAvailabilityForm()
        slot_form = TourSlotForm()
    availabilities = tour.availabilities.all()
    return render(request, 'accounts/operator_availability.html', {
        'tour': tour, 'form': form, 'slot_form': slot_form, 'availabilities': availabilities
    })

@login_required
def operator_bookings(request):
    tours = Tour.objects.filter(operator=request.user)
    bookings = Booking.objects.filter(tour__in=tours).order_by('-created_at')
    return render(request, 'accounts/operator_bookings.html', {'bookings': bookings})
