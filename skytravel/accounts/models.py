from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Profile(models.Model):
    USER_TYPES = (
        ('traveler', 'Traveler'),
        ('operator', 'Tour Operator'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='traveler')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='profiles/', blank=True, default='profiles/default.jpg')
    bio = models.TextField(max_length=500, blank=True)
    country = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.get_user_type_display()}"

class OperatorProfile(models.Model):
    APPROVAL_STATUS = (
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operator_profile')
    business_name = models.CharField(max_length=200)
    business_address = models.TextField(blank=True, default='')
    business_phone = models.CharField(max_length=20, blank=True, default='')
    business_email = models.EmailField(blank=True, default='')
    business_license = models.CharField(max_length=100, blank=True, help_text="License or registration number")
    tax_id = models.CharField(max_length=100, blank=True, help_text="GST/PAN/Tax ID")
    website = models.URLField(blank=True)
    description = models.TextField(max_length=1000, blank=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='operator_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} ({self.get_approval_status_display()})"

class VerificationDocument(models.Model):
    DOC_TYPES = (
        ('id_proof', 'ID Proof'),
        ('business_license', 'Business License'),
        ('tax_document', 'Tax Document'),
        ('insurance', 'Insurance Certificate'),
        ('other', 'Other'),
    )
    operator = models.ForeignKey(OperatorProfile, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.operator.business_name} - {self.get_doc_type_display()}"
