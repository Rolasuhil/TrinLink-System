"""
Unit Tests for accounts app
White Box Testing: Testing internal logic of models, serializers, and views
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Person, Trainee, CompanyProfile, SupervisorProfile, OTPVerification, CV
from .serializers import (
    LoginSerializer, RegisterTraineeSerializer, RegisterCompanySerializer,
    RegisterSupervisorSerializer, OTPVerifySerializer, PersonSerializer
)

Person = get_user_model()


class PersonModelTest(TestCase):
    """Unit tests for Person model (Custom User)"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='أحمد محمد',
            email='ahmed@test.com',
            phone_number='0599123456',
            person_type='trainee',
            is_verified=True,
        )

    def test_person_creation(self):
        self.assertEqual(self.person.full_name, 'أحمد محمد')
        self.assertEqual(self.person.email, 'ahmed@test.com')
        self.assertEqual(self.person.person_type, 'trainee')
        self.assertTrue(self.person.is_verified)

    def test_person_user_id_auto_generated(self):
        self.assertIsNotNone(self.person.user_id)
        self.assertTrue(self.person.user_id.startswith('TR'))

    def test_person_email_unique(self):
        with self.assertRaises(Exception):
            Person.objects.create(
                full_name='Duplicate',
                email='ahmed@test.com',
                person_type='trainee',
            )

    def test_person_str(self):
        self.assertEqual(str(self.person), 'أحمد محمد (متدرب)')

    def test_person_default_values(self):
        self.assertTrue(self.person.is_active)
        self.assertFalse(self.person.is_staff)


class TraineeModelTest(TestCase):
    """Unit tests for Trainee profile model"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='سارة علي',
            email='sara@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(
            person=self.person,
            university='الجامعة الإسلامية',
            major='هندسة برمجيات',
            gpa=3.8,
            year_of_study=3,
        )

    def test_trainee_creation(self):
        self.assertEqual(self.trainee.university, 'الجامعة الإسلامية')
        self.assertEqual(self.trainee.gpa, 3.8)

    def test_trainee_person_link(self):
        self.assertEqual(self.trainee.person.full_name, 'سارة علي')

    def test_trainee_default_values(self):
        self.assertFalse(self.trainee.is_graduate)
        self.assertEqual(self.trainee.year_of_study, 3)


class CompanyProfileModelTest(TestCase):
    """Unit tests for CompanyProfile model"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='TechPal',
            email='company@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.person,
            company_name='TechPal',
            industry='تكنولوجيا',
            location='غزة',
        )

    def test_company_creation(self):
        self.assertEqual(self.company.company_name, 'TechPal')
        self.assertEqual(self.company.industry, 'تكنولوجيا')

    def test_company_person_link(self):
        self.assertEqual(self.company.person.email, 'company@test.com')

    def test_company_default_verified(self):
        self.assertFalse(self.company.is_verified)


class OTPVerificationTest(TestCase):
    """Unit tests for OTP verification model"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='test',
            email='otp@test.com',
            person_type='trainee',
        )
        self.otp = OTPVerification.objects.create(
            person=self.person,
            otp_code='123456',
            purpose='registration',
            expires_at=timezone.now() + timedelta(minutes=10),
        )

    def test_otp_creation(self):
        self.assertEqual(self.otp.otp_code, '123456')
        self.assertEqual(self.otp.purpose, 'registration')

    def test_otp_not_used_by_default(self):
        self.assertFalse(self.otp.is_used)

    def test_otp_expires(self):
        self.assertIsNotNone(self.otp.expires_at)


class LoginSerializerTest(TestCase):
    """Unit tests for LoginSerializer"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='Login Test',
            email='login@test.com',
            person_type='trainee',
        )
        self.person.set_password('testpass123')
        self.person.save()

    def test_valid_login(self):
        serializer = LoginSerializer(data={
            'email': 'login@test.com',
            'password': 'testpass123',
            'user_type': 'trainee',
        })
        self.assertTrue(serializer.is_valid())

    def test_invalid_email(self):
        serializer = LoginSerializer(data={
            'email': 'wrong@test.com',
            'password': 'testpass123',
            'user_type': 'trainee',
        })
        self.assertFalse(serializer.is_valid())

    def test_missing_fields(self):
        serializer = LoginSerializer(data={})
        self.assertFalse(serializer.is_valid())


class RegisterTraineeSerializerTest(TestCase):
    """Unit tests for RegisterTraineeSerializer"""

    def test_valid_registration(self):
        serializer = RegisterTraineeSerializer(data={
            'full_name': 'متدرّب جديد',
            'email': 'new@test.com',
            'password': 'securepass123',
            'university': 'الجامعة الإسلامية',
            'major': '计算机科学',
        })
        self.assertTrue(serializer.is_valid())

    def test_missing_required_fields(self):
        serializer = RegisterTraineeSerializer(data={})
        self.assertFalse(serializer.is_valid())


class RegisterCompanySerializerTest(TestCase):
    """Unit tests for RegisterCompanySerializer"""

    def test_valid_registration(self):
        serializer = RegisterCompanySerializer(data={
            'company_name': 'شركة تك',
            'email': 'tech@test.com',
            'password': 'securepass123',
        })
        self.assertTrue(serializer.is_valid())

    def test_missing_company_name(self):
        serializer = RegisterCompanySerializer(data={
            'email': 'tech@test.com',
            'password': 'securepass123',
        })
        self.assertFalse(serializer.is_valid())


class PersonSerializerTest(TestCase):
    """Unit tests for PersonSerializer"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='.Serial Test',
            email='serial@test.com',
            person_type='trainee',
        )

    def test_serializer_fields(self):
        serializer = PersonSerializer(self.person)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('full_name', data)
        self.assertIn('email', data)
        self.assertIn('person_type', data)
        self.assertIn('trainee_id', data)
        self.assertIn('company_id', data)

    def test_trainee_id_none_for_company(self):
        person = Person.objects.create(
            full_name='Company User',
            email='company2@test.com',
            person_type='company',
        )
        serializer = PersonSerializer(person)
        self.assertIsNone(serializer.data['trainee_id'])

    def test_company_name_none_for_trainee(self):
        serializer = PersonSerializer(self.person)
        self.assertIsNone(serializer.data['company_name'])
