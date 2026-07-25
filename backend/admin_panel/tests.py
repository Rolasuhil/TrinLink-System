"""
Unit Tests for admin_panel app
"""
from django.test import TestCase
from accounts.models import Person
from .models import ContentReport


class ContentReportModelTest(TestCase):
    """Unit tests for ContentReport model"""

    def setUp(self):
        self.reporter = Person.objects.create(
            full_name='المبلّغ',
            email='reporter@test.com',
            person_type='trainee',
        )
        self.reviewer = Person.objects.create(
            full_name='المراجع',
            email='reviewer@test.com',
            person_type='admin',
        )

    def test_report_creation(self):
        report = ContentReport.objects.create(
            reported_by=self.reporter,
            content_type='post',
            content_id=1,
            reason='محتوى مخالف',
        )
        self.assertEqual(report.status, 'pending')
        self.assertEqual(report.reason, 'محتوى مخالف')

    def test_report_status_update(self):
        report = ContentReport.objects.create(
            reported_by=self.reporter,
            content_type='comment',
            content_id=5,
            reason='إساءة',
        )
        report.status = 'approved'
        report.reviewed_by = self.reviewer
        report.save()
        report.refresh_from_db()
        self.assertEqual(report.status, 'approved')
        self.assertEqual(report.reviewed_by.full_name, 'المراجع')

    def test_report_status_choices(self):
        for status in ['pending', 'approved', 'removed']:
            ContentReport.objects.create(
                reported_by=self.reporter,
                content_type='post',
                content_id=1,
                reason='سبب',
                status=status,
            )
        self.assertEqual(ContentReport.objects.count(), 3)
