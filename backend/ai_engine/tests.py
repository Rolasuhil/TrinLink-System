"""
Unit Tests for ai_engine app
"""
from django.test import TestCase
from accounts.models import Person, Trainee, CV
from internships.models import Category, Internship, CompanyProfile
from .models import AIMatchingResult, CVAnalysis


class AIMatchingResultTest(TestCase):
    """Unit tests for AIMatchingResult model"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='متدرب AI',
            email='aitrainee@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.person)
        self.cv = CV.objects.create(
            trainee=self.trainee,
            is_primary=True,
        )
        self.company_person = Person.objects.create(
            full_name='AI Corp',
            email='aicorp@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.company_person,
            company_name='AI Corp',
        )
        self.internship = Internship.objects.create(
            company=self.company,
            title='مطور AI',
            description='فرصة ذكاء اصطناعي',
            deadline='2026-12-31',
            location='غزة',
            start_date='2026-09-01',
            end_date='2026-12-01',
        )

    def test_matching_result_creation(self):
        result = AIMatchingResult.objects.create(
            trainee=self.trainee,
            internship=self.internship,
            match_score=87.5,
            reason='مطابقة ممتازة بناءً على المهارات',
        )
        self.assertEqual(result.match_score, 87.5)
        self.assertIn('مطابقة', result.reason)

    def test_matching_result_score_range(self):
        result = AIMatchingResult.objects.create(
            trainee=self.trainee,
            internship=self.internship,
            match_score=95.0,
        )
        self.assertGreaterEqual(result.match_score, 0)
        self.assertLessEqual(result.match_score, 100)


class CVAnalysisTest(TestCase):
    """Unit tests for CVAnalysis model"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='محلل CV',
            email='cvanalyst@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.person)
        self.cv = CV.objects.create(
            trainee=self.trainee,
            is_primary=True,
        )

    def test_cv_analysis_creation(self):
        analysis = CVAnalysis.objects.create(
            cv=self.cv,
            overall_score=82.0,
            sections_score={
                'education': 90,
                'experience': 75,
                'skills': 85,
            },
            suggestions=[
                'أضف مشاريع عملية',
                'حسّن ملخص الخبرات',
            ],
            strengths=['تعليم قوي', 'مهارات تقنية'],
            weaknesses=['خبرة عملية محدودة'],
        )
        self.assertEqual(analysis.overall_score, 82.0)
        self.assertIsNotNone(analysis.sections_score)

    def test_cv_analysis_default_score(self):
        analysis = CVAnalysis.objects.create(cv=self.cv)
        self.assertEqual(analysis.overall_score, 0.0)

    def test_cv_analysis_one_to_one(self):
        CVAnalysis.objects.create(cv=self.cv, overall_score=70.0)
        with self.assertRaises(Exception):
            CVAnalysis.objects.create(cv=self.cv, overall_score=80.0)
