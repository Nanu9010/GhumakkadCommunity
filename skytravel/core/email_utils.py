import os
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from tours.models import Booking
from core.models import Notification


def send_notification_email(user, subject, message, link=None):
    Notification.objects.create(
        user=user,
        notif_type='booking_confirmed',
        title=subject,
        message=message,
        link=link or '',
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_booking_confirmation(booking):
    Notification.objects.create(
        user=booking.user,
        notif_type='booking_confirmed',
        title=f'Booking Confirmed - {booking.tour.title}',
        message=f'Your booking #{booking.id} for {booking.tour.title} on '
                f'{booking.travel_date} has been confirmed. '
                f'Travelers: {booking.travelers}, Total: {booking.tour.currency} {booking.total}',
        link=f'/bookings/{booking.id}/',
    )

    subject = f'Booking Confirmed - {booking.tour.title}'
    message = (
        f'Dear {booking.user.get_full_name() or booking.user.email},\n\n'
        f'Your booking has been confirmed!\n\n'
        f'Booking ID: {booking.id}\n'
        f'Tour: {booking.tour.title}\n'
        f'Date: {booking.travel_date}\n'
        f'Travelers: {booking.travelers}\n'
        f'Total Amount: {booking.tour.currency} {booking.total}\n\n'
        f'Thank you for choosing Ghumakkad Community!'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.contact_email],
        fail_silently=True,
    )

    operator_subject = f'New Booking - {booking.tour.title}'
    operator_message = (
        f'A new booking has been received.\n\n'
        f'Booking ID: {booking.id}\n'
        f'Tour: {booking.tour.title}\n'
        f'Customer: {booking.user.get_full_name() or booking.user.email}\n'
        f'Email: {booking.contact_email}\n'
        f'Phone: {booking.contact_phone}\n'
        f'Date: {booking.travel_date}\n'
        f'Travelers: {booking.travelers}\n'
        f'Total Amount: {booking.tour.currency} {booking.total}\n'
        f'Special Requests: {booking.special_requests or "None"}'
    )
    send_mail(
        operator_subject,
        operator_message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.tour.operator.email],
        fail_silently=True,
    )


def send_payment_receipt(payment):
    booking = payment.booking
    Notification.objects.create(
        user=booking.user,
        notif_type='payment_success',
        title=f'Payment Received - {booking.tour.title}',
        message=f'Payment of {payment.currency} {payment.amount} for '
                f'{booking.tour.title} has been received successfully.',
        link=f'/bookings/{booking.id}/',
    )

    subject = f'Payment Receipt - {booking.tour.title}'
    message = (
        f'Dear {booking.user.get_full_name() or booking.user.email},\n\n'
        f'Your payment has been received successfully.\n\n'
        f'Booking ID: {booking.id}\n'
        f'Tour: {booking.tour.title}\n'
        f'Amount Paid: {payment.currency} {payment.amount}\n'
        f'Payment ID: {payment.razorpay_payment_id or "N/A"}\n'
        f'Status: {payment.get_status_display()}\n\n'
        f'Thank you for your payment!'
    )

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.contact_email],
    )

    if payment.invoice_pdf:
        invoice_path = os.path.join(settings.MEDIA_ROOT, str(payment.invoice_pdf))
        if os.path.exists(invoice_path):
            with open(invoice_path, 'rb') as f:
                email.attach(os.path.basename(invoice_path), f.read(), 'application/pdf')

    email.send(fail_silently=True)


def send_hotel_booking_confirmation(hotel_booking):
    Notification.objects.create(
        user=hotel_booking.user,
        notif_type='booking_confirmed',
        title=f'Hotel Booking Confirmed - {hotel_booking.hotel.name}',
        message=f'Your hotel booking #{hotel_booking.id} at {hotel_booking.hotel.name} '
                f'from {hotel_booking.check_in} to {hotel_booking.check_out} has been confirmed. '
                f'Total: {hotel_booking.hotel.currency} {hotel_booking.total}',
        link=f'/hotel-bookings/{hotel_booking.id}/',
    )

    subject = f'Hotel Booking Confirmed - {hotel_booking.hotel.name}'
    message = (
        f'Dear {hotel_booking.user.get_full_name() or hotel_booking.user.email},\n\n'
        f'Your hotel booking has been confirmed!\n\n'
        f'Booking ID: {hotel_booking.id}\n'
        f'Hotel: {hotel_booking.hotel.name}\n'
        f'Room Type: {hotel_booking.room_type.name}\n'
        f'Check-in: {hotel_booking.check_in}\n'
        f'Check-out: {hotel_booking.check_out}\n'
        f'Nights: {hotel_booking.nights}\n'
        f'Rooms: {hotel_booking.rooms}\n'
        f'Guests: {hotel_booking.guests}\n'
        f'Total Amount: {hotel_booking.hotel.currency} {hotel_booking.total}\n\n'
        f'Thank you for choosing Ghumakkad Community!'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [hotel_booking.contact_email],
        fail_silently=True,
    )
