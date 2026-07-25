"""
Unit Tests for internships app
White Box Testing: Testing internal logic of models, serializers, and views
"""
from django.test import TestCase
from accounts.models import Person, Trainee, CompanyProfile
from .models import Category, Internship, Application, SavedInternship, AcceptedTrainee


class CategoryModelTest(TestCase):
    """Unit tests for Category model"""

    def setUp(self):
        self.category = Category.objects.create(
            name='تطوير الويب',
            description='فرص تطوير المواقع الإلكترونية',
            icon='ti-code',
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'تطوير الويب')
        self.assertEqual(self.category.icon, 'ti-code')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'تطوير الويب')


class InternshipModelTest(TestCase):
    """Unit tests for Internship model"""

    def setUp(self):
        self.company_person = Person.objects.create(
            full_name='TechCorp',
            email='techcorp@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.company_person,
            company_name='TechCorp',
            industry='تكنولوجيا',
        )
        self.category = Category.objects.create(name='تطوير')
        self.internship = Internship.objects.create(
            company=self.company,
            category=self.category,
            title='مطور Frontend',
            description='فرصة تدريب في تطوير واجهات المستخدم',
            requirements='خبرة في HTML CSS JS',
            deadline='2026-12-31',
            available_positions=3,
            location='غزة',
            internship_type='onsite',
            start_date='2026-09-01',
            end_date='2026-12-01',
            status='open',
        )

    def test_internship_creation(self):
        self.assertEqual(self.internship.title, 'مطور Frontend')
        self.assertEqual(self.internship.status, 'open')
        self.assertEqual(self.internship.available_positions, 3)

    def test_internship_company_link(self):
        self.assertEqual(self.internship.company.company_name, 'TechCorp')

    def test_internship_category_link(self):
        self.assertEqual(self.internship.category.name, 'تطوير')

    def test_internship_type_choices(self):
        self.assertIn(self.internship.internship_type, ['onsite', 'remote', 'hybrid'])

    def test_internship_status_default(self):
        internship2 = Internship.objects.create(
            company=self.company,
            title='مطور Backend',
            description='Test',
            deadline='2026-12-31',
            location='remote',
            internship_type='remote',
            start_date='2026-09-01',
            end_date='2026-12-01',
        )
        self.assertEqual(internship2.status, 'open')


class ApplicationModelTest(TestCase):
    """Unit tests for Application model"""

    def setUp(self):
        self.company_person = Person.objects.create(
            full_name='AppTest Corp',
            email='apptest@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.company_person,
            company_name='AppTest Corp',
        )
        self.internship = Internship.objects.create(
            company=self.company,
            title='Test Position',
            description='Test',
            deadline='2026-12-31',
            location='غزة',
            start_date='2026-09-01',
            end_date='2026-12-01',
        )
        self.trainee_person = Person.objects.create(
            full_name='متدرب تجريبي',
            email='trainee@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.trainee_person)
        self.application = Application.objects.create(
            internship=self.internship,
            trainee=self.trainee,
            status='pending',
        )

    def test_application_creation(self):
        self.assertEqual(self.application.status, 'pending')
        self.assertEqual(self.application.internship.title, 'Test Position')

    def test_application_status_choices(self):
        self.assertIn(self.application.status, ['pending', 'accepted', 'rejected'])

    def test_application_trainee_link(self):
        self.assertEqual(self.application.trainee.person.full_name, 'متدرب تجريبي')

    def test_multiple_applications_same_internship(self):
        trainee2_person = Person.objects.create(
            full_name='متدرب آخر',
            email='trainee2@test.com',
            person_type='trainee',
        )
        trainee2 = Trainee.objects.create(person=trainee2_person)
        app2 = Application.objects.create(
            internship=self.internship,
            trainee=trainee2,
            status='pending',
        )
        self.assertEqual(self.internship.applications.count(), 2)


class SavedInternshipModelTest(TestCase):
    """Unit tests for SavedInternship model"""

    def setUp(self):
        self.company_person = Person.objects.create(
            full_name='SaveTest Corp',
            email='savetest@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.company_person,
            company_name='SaveTest Corp',
        )
        self.internship = Internship.objects.create(
            company=self.company,
            title='Saved Position',
            description='Test',
            deadline='2026-12-31',
            location='غزة',
            start_date='2026-09-01',
            end_date='2026-12-01',
        )
        self.trainee_person = Person.objects.create(
            full_name='Save Tester',
            email='savetrainee@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.trainee_person)

    def test_save_internship(self):
        saved = SavedInternship.objects.create(
            trainee=self.trainee,
            internship=self.internship,
        )
        self.assertIsNotNone(saved.saved_at)

    def test_unique_save(self):
        SavedInternship.objects.create(
            trainee=self.trainee,
            internship=self.internship,
        )
        with self.assertRaises(Exception):
            SavedInternship.objects.create(
                trainee=self.trainee,
                internship=self.internship,
            )


class AcceptedTraineeModelTest(TestCase):
    """Unit tests for AcceptedTrainee model"""

    def setUp(self):
        self.company_person = Person.objects.create(
            full_name='Accept Corp',
            email='accept@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.company_person,
            company_name='Accept Corp',
        )
        self.internship = Internship.objects.create(
            company=self.company,
            title='Accepted Position',
            description='Test',
            deadline='2026-12-31',
            location='غزة',
            start_date='2026-09-01',
            end_date='2026-12-01',
        )
        self.trainee_person = Person.objects.create(
            full_name='Accepted Trainee',
            email='accepted@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.trainee_person)
        self.application = Application.objects.create(
            internship=self.internship,
            trainee=self.trainee,
            status='accepted',
        )

    def test_accepted_trainee_creation(self):
        accepted = AcceptedTrainee.objects.create(
            application=self.application,
            department='Frontend',
            joining_date='2026-09-01',
        )
        self.assertEqual(accepted.department, 'Frontend')
