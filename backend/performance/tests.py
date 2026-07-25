"""
Unit Tests for performance app
"""
from django.test import TestCase
from accounts.models import Person, Trainee, CompanyProfile, SupervisorProfile
from .models import SupervisionAssignment, Report, WorkReport, PerformanceReport, DailyAttendance


class SupervisionAssignmentTest(TestCase):
    """Unit tests for SupervisionAssignment model"""

    def setUp(self):
        self.supervisor_person = Person.objects.create(
            full_name='مشرف تجريبي',
            email='supervisor@test.com',
            person_type='supervisor',
        )
        self.supervisor = SupervisorProfile.objects.create(
            person=self.supervisor_person,
            department='ال计算机',
            job_title='مشرف أكاديمي',
        )
        self.trainee_person = Person.objects.create(
            full_name='متدرب الأداء',
            email='performancetrainee@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.trainee_person)

    def test_assignment_creation(self):
        assignment = SupervisionAssignment.objects.create(
            supervisor=self.supervisor,
            trainee=self.trainee,
            role='academic',
        )
        self.assertEqual(assignment.status, 'active')
        self.assertEqual(assignment.role, 'academic')

    def test_assignment_status_choices(self):
        assignment = SupervisionAssignment.objects.create(
            supervisor=self.supervisor,
            trainee=self.trainee,
            status='completed',
        )
        self.assertIn(assignment.status, ['active', 'completed', 'cancelled'])


class DailyAttendanceTest(TestCase):
    """Unit tests for DailyAttendance model"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='حاضرة تجريبية',
            email='attendance@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.person)

    def test_attendance_creation(self):
        attendance = DailyAttendance.objects.create(
            trainee=self.trainee,
            date='2026-07-25',
            status='present',
        )
        self.assertEqual(attendance.status, 'present')

    def test_attendance_status_choices(self):
        for i, status in enumerate(['present', 'absent', 'late']):
            DailyAttendance.objects.create(
                trainee=self.trainee,
                date=f'2026-07-{25+i}',
                status=status,
            )
        self.assertEqual(self.trainee.attendance.count(), 3)

    def test_check_in_out(self):
        from django.utils import timezone
        attendance = DailyAttendance.objects.create(
            trainee=self.trainee,
            date='2026-07-25',
            check_in_time=timezone.now(),
            status='present',
        )
        self.assertIsNotNone(attendance.check_in_time)
        attendance.check_out_time = timezone.now()
        attendance.save()
        self.assertIsNotNone(attendance.check_out_time)


class WorkReportTest(TestCase):
    """Unit tests for WorkReport model"""

    def setUp(self):
        self.person = Person.objects.create(
            full_name='متدرب تقارير',
            email='workreport@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.person)

    def test_work_report_creation(self):
        report = WorkReport.objects.create(
            trainee=self.trainee,
            task_title='تطوير واجهة المستخدم',
            description='عملت على صفحة تسجيل الدخول',
        )
        self.assertEqual(report.task_title, 'تطوير واجهة المستخدم')
        self.assertEqual(report.performance_rating, 0)

    def test_work_report_feedback(self):
        report = WorkReport.objects.create(
            trainee=self.trainee,
            task_title='مهمة تجريبية',
            description='وصف المهمة',
        )
        report.company_feedback = 'عمل ممتاز'
        report.performance_rating = 4
        report.save()
        report.refresh_from_db()
        self.assertEqual(report.company_feedback, 'عمل ممتاز')
        self.assertEqual(report.performance_rating, 4)


class PerformanceReportTest(TestCase):
    """Unit tests for PerformanceReport model"""

    def setUp(self):
        self.trainee_person = Person.objects.create(
            full_name='تقرير أداء',
            email='perfreport@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.trainee_person)
        self.company_person = Person.objects.create(
            full_name='شركة الأداء',
            email='perfcompany@test.com',
            person_type='company',
        )
        self.company = CompanyProfile.objects.create(
            person=self.company_person,
            company_name='شركة الأداء',
        )

    def test_performance_report_creation(self):
        report = PerformanceReport.objects.create(
            trainee=self.trainee,
            company=self.company,
            week_number=1,
            performance_score=85.5,
            comments='أداء جيد',
        )
        self.assertEqual(report.week_number, 1)
        self.assertEqual(report.performance_score, 85.5)
        self.assertFalse(report.attendance_confirmed)

    def test_ai_summary_field(self):
        report = PerformanceReport.objects.create(
            trainee=self.trainee,
            company=self.company,
            week_number=2,
        )
        report.ai_summary = 'ملاحظات الذكاء الاصطناعي'
        report.ai_rating = 'ممتاز'
        report.save()
        report.refresh_from_db()
        self.assertEqual(report.ai_summary, 'ملاحظات الذكاء الاصطناعي')


class ReportModelTest(TestCase):
    """Unit tests for Report (Supervisor Report) model"""

    def setUp(self):
        self.supervisor_person = Person.objects.create(
            full_name='مشرف التقارير',
            email='reportsuper@test.com',
            person_type='supervisor',
        )
        self.supervisor = SupervisorProfile.objects.create(
            person=self.supervisor_person,
            department='هندسة',
        )
        self.trainee_person = Person.objects.create(
            full_name='متدرب التقرير',
            email='reporttrainee@test.com',
            person_type='trainee',
        )
        self.trainee = Trainee.objects.create(person=self.trainee_person)
        self.assignment = SupervisionAssignment.objects.create(
            supervisor=self.supervisor,
            trainee=self.trainee,
        )

    def test_report_creation(self):
        report = Report.objects.create(
            assignment=self.assignment,
            grade=88.0,
            feedback='أداء ممتاز هذا الأسبوع',
            week_number=1,
        )
        self.assertEqual(report.grade, 88.0)
        self.assertEqual(report.week_number, 1)

    def test_report_default_grade(self):
        report = Report.objects.create(
            assignment=self.assignment,
            week_number=2,
        )
        self.assertEqual(report.grade, 0.0)
