from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
from .models import Profile, OperatorProfile, VerificationDocument


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', username='testuser', password='testpass123'
        )

    def test_profile_created_on_user_creation(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_profile_default_type_is_traveler(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.user_type, 'traveler')

    def test_profile_str(self):
        profile = Profile.objects.get(user=self.user)
        self.assertIn('test@example.com', str(profile))

    def test_profile_str_with_operator_type(self):
        profile = Profile.objects.get(user=self.user)
        profile.user_type = 'operator'
        profile.save()
        self.assertIn('Tour Operator', str(profile))

    def test_profile_update_fields(self):
        profile = Profile.objects.get(user=self.user)
        profile.phone = '+911234567890'
        profile.country = 'India'
        profile.bio = 'Travel enthusiast'
        profile.date_of_birth = date(1995, 6, 15)
        profile.save()
        profile.refresh_from_db()
        self.assertEqual(profile.phone, '+911234567890')
        self.assertEqual(profile.country, 'India')
        self.assertEqual(profile.bio, 'Travel enthusiast')
        self.assertEqual(profile.date_of_birth, date(1995, 6, 15))

    def test_profile_email_verified_default_false(self):
        profile = Profile.objects.get(user=self.user)
        self.assertFalse(profile.email_verified)

    def test_profile_user_type_choices(self):
        profile = Profile.objects.get(user=self.user)
        valid_types = [choice[0] for choice in Profile.USER_TYPES]
        for ut in ['traveler', 'operator', 'admin']:
            self.assertIn(ut, valid_types)


class OperatorProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='operator@example.com', username='operator', password='testpass123'
        )
        self.operator_profile = OperatorProfile.objects.create(
            user=self.user,
            business_name='Adventure Tours',
            business_address='123 Main St',
            business_phone='+911234567890',
            business_email='business@adventure.com',
            business_license='LIC-12345',
            tax_id='TAX-67890',
        )

    def test_operator_profile_str(self):
        self.assertIn('Adventure Tours', str(self.operator_profile))

    def test_approval_status_default_pending(self):
        self.assertEqual(self.operator_profile.approval_status, 'pending')

    def test_operator_profile_approval_workflow(self):
        self.operator_profile.approval_status = 'approved'
        self.operator_profile.save()
        self.assertEqual(self.operator_profile.approval_status, 'approved')

    def test_operator_profile_rejection(self):
        self.operator_profile.approval_status = 'rejected'
        self.operator_profile.rejection_reason = 'Invalid documents'
        self.operator_profile.save()
        self.assertEqual(self.operator_profile.approval_status, 'rejected')
        self.assertEqual(self.operator_profile.rejection_reason, 'Invalid documents')


class VerificationDocumentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='operator@example.com', username='operator', password='testpass123'
        )
        self.operator_profile = OperatorProfile.objects.create(
            user=self.user,
            business_name='Adventure Tours',
            business_address='123 Main St',
            business_phone='+911234567890',
            business_email='business@adventure.com',
        )

    def test_verification_document_creation(self):
        doc_file = SimpleUploadedFile('test_doc.pdf', b'fake pdf content', content_type='application/pdf')
        doc = VerificationDocument.objects.create(
            operator=self.operator_profile,
            doc_type='id_proof',
            document=doc_file,
        )
        self.assertEqual(doc.doc_type, 'id_proof')
        self.assertFalse(doc.is_verified)

    def test_verification_document_str(self):
        doc_file = SimpleUploadedFile('test_doc.pdf', b'fake pdf content', content_type='application/pdf')
        doc = VerificationDocument.objects.create(
            operator=self.operator_profile,
            doc_type='business_license',
            document=doc_file,
        )
        self.assertIn('Adventure Tours', str(doc))
        self.assertIn('Business License', str(doc))


class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com', username='testuser', password='testpass123'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_dashboard_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertIn('profile', response.context)
        self.assertIn('bookings', response.context)
        self.assertIn('reviews', response.context)


class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com', username='testuser', password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_update_get(self):
        response = self.client.get(reverse('accounts:profile_update'))
        self.assertEqual(response.status_code, 200)

    def test_profile_update_post(self):
        response = self.client.post(reverse('accounts:profile_update'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com',
            'phone': '+911234567890',
            'bio': 'Travel lover',
            'country': 'India',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')


class OperatorRegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='operator@example.com', username='operator', password='testpass123'
        )
        self.client.login(username='operator', password='testpass123')

    def test_operator_register_get(self):
        response = self.client.get(reverse('accounts:operator_register'))
        self.assertEqual(response.status_code, 200)

    def test_operator_register_post(self):
        doc_file = SimpleUploadedFile('test_doc.pdf', b'fake pdf content', content_type='application/pdf')
        response = self.client.post(reverse('accounts:operator_register'), {
            'business_name': 'Adventure Tours',
            'business_address': '123 Main St',
            'business_phone': '+911234567890',
            'business_email': 'business@adventure.com',
            'doc_type': 'id_proof',
            'document': doc_file,
        })
        self.assertTrue(OperatorProfile.objects.filter(user=self.user).exists())
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.user_type, 'operator')


class OperatorDashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='operator@example.com', username='operator', password='testpass123'
        )
        self.operator_profile = OperatorProfile.objects.create(
            user=self.user,
            business_name='Adventure Tours',
            business_address='123 Main St',
            business_phone='+911234567890',
            business_email='business@adventure.com',
        )
        self.client.login(username='operator', password='testpass123')

    def test_operator_dashboard(self):
        response = self.client.get(reverse('accounts:operator_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_operator_dashboard_context(self):
        response = self.client.get(reverse('accounts:operator_dashboard'))
        self.assertIn('operator_profile', response.context)
        self.assertIn('tours', response.context)
        self.assertIn('total_revenue', response.context)


class OperatorTourListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='operator@example.com', username='operator', password='testpass123'
        )
        self.client.login(username='operator', password='testpass123')

    def test_operator_tour_list(self):
        response = self.client.get(reverse('accounts:operator_tour_list'))
        self.assertEqual(response.status_code, 200)

    def test_operator_tour_list_context(self):
        response = self.client.get(reverse('accounts:operator_tour_list'))
        self.assertIn('tours', response.context)
