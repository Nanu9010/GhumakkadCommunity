from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from .models import Profile, OperatorProfile, VerificationDocument

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    user_type = forms.ChoiceField(choices=[('traveler', 'Traveler'), ('operator', 'Tour Operator')], label='I want to')

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        profile = Profile.objects.get(user=user)
        profile.user_type = self.cleaned_data['user_type']
        profile.save()
        if self.cleaned_data['user_type'] == 'operator':
            OperatorProfile.objects.create(
                user=user,
                business_name=f"{user.first_name} {user.last_name}'s Business"
            )
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar', 'bio', 'country', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class OperatorProfileForm(forms.ModelForm):
    class Meta:
        model = OperatorProfile
        fields = ['business_name', 'business_address', 'business_phone', 'business_email',
                   'business_license', 'tax_id', 'website', 'description']
        widgets = {
            'business_address': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class VerificationDocumentForm(forms.ModelForm):
    class Meta:
        model = VerificationDocument
        fields = ['doc_type', 'document']
