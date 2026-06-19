from django.contrib import admin
from .models import Profile, OperatorProfile, VerificationDocument

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'country', 'email_verified', 'created_at']
    list_filter = ['user_type', 'email_verified', 'country']
    search_fields = ['user__email', 'user__username', 'phone']

@admin.register(OperatorProfile)
class OperatorProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'approval_status', 'created_at']
    list_filter = ['approval_status']
    search_fields = ['business_name', 'user__email', 'business_email']
    actions = ['approve_operators', 'reject_operators']

    def approve_operators(self, request, queryset):
        from django.utils import timezone
        queryset.update(approval_status='approved', reviewed_by=request.user, reviewed_at=timezone.now())
    approve_operators.short_description = "Approve selected operators"

    def reject_operators(self, request, queryset):
        from django.utils import timezone
        queryset.update(approval_status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())
    reject_operators.short_description = "Reject selected operators"

@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ['operator', 'doc_type', 'uploaded_at', 'is_verified']
    list_filter = ['doc_type', 'is_verified']
