import os
import datetime
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from tours.models import Booking, Payment


def generate_invoice(booking):
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'razorpay_order_id': f'MANUAL-{booking.id}',
            'amount': booking.total,
            'currency': booking.tour.currency,
            'status': 'paid' if booking.status == 'confirmed' else 'created',
        }
    )

    filename = f'invoice_{booking.id}_{datetime.date.today()}.pdf'
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)
    filepath = os.path.join(invoices_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm,
                            leftMargin=20*mm, rightMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'InvoiceTitle', parent=styles['Heading1'],
        fontSize=24, spaceAfter=20, alignment=1
    )
    normal = styles['Normal']
    bold_style = ParagraphStyle('BoldText', parent=normal, fontSize=10, spaceAfter=4)

    elements = []

    elements.append(Paragraph('INVOICE', title_style))
    elements.append(Spacer(1, 10*mm))

    booking_date = getattr(booking.booking_date, 'date', lambda: booking.booking_date)()
    elements.append(Paragraph(
        f'Invoice #: INV-{booking.id:05d}<br/>'
        f'Date: {booking_date.strftime("%d %b %Y") if hasattr(booking_date, "strftime") else datetime.date.today().strftime("%d %b %Y")}',
        bold_style
    ))
    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph(
        '<b>Ghumakkad Community</b><br/>'
        'Let\'s Explore Together<br/>'
        'contact@ghumakkadcommunity.com',
        normal
    ))
    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph(
        f'<b>Bill To:</b><br/>'
        f'{booking.user.get_full_name() or booking.user.email}<br/>'
        f'Email: {booking.contact_email}<br/>'
        f'Phone: {booking.contact_phone or "N/A"}',
        normal
    ))
    elements.append(Spacer(1, 8*mm))

    rate = booking.subtotal / booking.travelers if booking.travelers else 0
    currency = booking.tour.currency

    data = [
        ['Description', 'Qty', 'Rate', 'Amount'],
        [Paragraph(booking.tour.title, normal),
         str(booking.travelers),
         f'{currency} {rate:.2f}',
         f'{currency} {booking.subtotal:.2f}'],
    ]

    if booking.discount and booking.discount > 0:
        data.append(['Discount', '', '',
                     f'-{currency} {booking.discount:.2f}'])

    data.append(['Tax', '', '',
                 f'{currency} {booking.tax:.2f}'])
    data.append(['Total', '', '',
                 f'{currency} {booking.total:.2f}'])

    col_widths = [250, 50, 100, 100]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph(
        f'<b>Payment Status:</b> {payment.get_status_display()}<br/>'
        f'<b>Booking Status:</b> {booking.get_status_display()}',
        normal
    ))
    elements.append(Spacer(1, 15*mm))

    elements.append(Paragraph(
        'Thank you for booking with Ghumakkad Community!',
        ParagraphStyle('Footer', parent=normal,
                       fontSize=10, alignment=1, textColor=colors.HexColor('#2C3E50'))
    ))

    doc.build(elements)

    payment.invoice_pdf = f'invoices/{filename}'
    payment.save()

    return payment


def generate_hotel_invoice(hotel_booking):
    filename = f'hotel_invoice_{hotel_booking.id}_{datetime.date.today()}.pdf'
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)
    filepath = os.path.join(invoices_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm,
                            leftMargin=20*mm, rightMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'InvoiceTitle', parent=styles['Heading1'],
        fontSize=24, spaceAfter=20, alignment=1
    )
    normal = styles['Normal']
    bold_style = ParagraphStyle('BoldText', parent=normal, fontSize=10, spaceAfter=4)

    elements = []

    elements.append(Paragraph('HOTEL INVOICE', title_style))
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph(
        f'Invoice #: HINV-{hotel_booking.id:05d}<br/>'
        f'Date: {hotel_booking.created_at.strftime("%d %b %Y")}<br/>'
        f'Check-in: {hotel_booking.check_in.strftime("%d %b %Y")}<br/>'
        f'Check-out: {hotel_booking.check_out.strftime("%d %b %Y")}<br/>'
        f'Nights: {hotel_booking.nights}',
        bold_style
    ))
    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph(
        '<b>Ghumakkad Community</b><br/>'
        'Let\'s Explore Together<br/>'
        'contact@ghumakkadcommunity.com',
        normal
    ))
    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph(
        f'<b>Bill To:</b><br/>'
        f'{hotel_booking.user.get_full_name() or hotel_booking.user.email}<br/>'
        f'Email: {hotel_booking.contact_email}<br/>'
        f'Phone: {hotel_booking.contact_phone or "N/A"}',
        normal
    ))
    elements.append(Spacer(1, 8*mm))

    currency = hotel_booking.hotel.currency
    rate = hotel_booking.subtotal / hotel_booking.rooms if hotel_booking.rooms else 0

    data = [
        ['Description', 'Qty', 'Rate', 'Amount'],
        [Paragraph(f'{hotel_booking.hotel.name}', normal),
         str(hotel_booking.rooms),
         f'{currency} {rate:.2f}',
         f'{currency} {hotel_booking.subtotal:.2f}'],
    ]

    data.append(['Tax', '', '',
                 f'{currency} {hotel_booking.tax:.2f}'])
    data.append(['Total', '', '',
                 f'{currency} {hotel_booking.total:.2f}'])

    col_widths = [250, 50, 100, 100]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 6*mm))

    elements.append(Paragraph(
        f'<b>Booking Status:</b> {hotel_booking.get_status_display()}',
        normal
    ))
    elements.append(Spacer(1, 15*mm))

    elements.append(Paragraph(
        'Thank you for booking with Ghumakkad Community!',
        ParagraphStyle('Footer', parent=normal,
                       fontSize=10, alignment=1, textColor=colors.HexColor('#2C3E50'))
    ))

    doc.build(elements)

    return f'invoices/{filename}'
