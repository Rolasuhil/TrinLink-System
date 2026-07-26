# ملف إدارة لوحة تحكمjango لأداء النظام
# يسجل جميع نماذج الأداء في لوحة التحكم لإدارة الإشراف والتقارير والحضور

from django.contrib import admin
from .models import SupervisionAssignment, Report, WorkReport, PerformanceReport, DailyAttendance


@admin.register(SupervisionAssignment)
class SupervisionAssignmentAdmin(admin.ModelAdmin):
    """إدارة عمليات الإشراف في لوحة التحكم
    يعرض المشرف والمتدرب ونوع الإشراف والحالة وتاريخ التعيين
    """

    # الأعمدة المعروضة في قائمة التعيينات
    list_display = ['supervisor', 'trainee', 'role', 'status', 'assignment_date']
    # فلتر حسب الحالة ونوع الإشراف
    list_filter = ['status', 'role']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """إدارة التقارير الإشرافية في لوحة التحكم
    يعرض عملية الإشراف ورقم الأسبوع والدرجة وتاريخ التقرير
    """

    # الأعمدة المعروضة في قائمة التقارير
    list_display = ['assignment', 'week_number', 'grade', 'report_date']


@admin.register(WorkReport)
class WorkReportAdmin(admin.ModelAdmin):
    """إدارة التقارير اليومية في لوحة التحكم
    يعرض المتدرب وعنوان المهمة وتقييم الأداء وتاريخ التسليم
    """

    # الأعمدة المعروضة في قائمة التقارير اليومية
    list_display = ['trainee', 'task_title', 'performance_rating', 'submitted_at']


@admin.register(PerformanceReport)
class PerformanceReportAdmin(admin.ModelAdmin):
    """إدارة تقارير الأداء الأسبوعية في لوحة التحكم
    يعرض المتدرب والشركة ورقم الأسبوع ودرجة الأداء وتأكيد الحضور
    """

    # الأعمدة المعروضة في قائمة تقارير الأداء
    list_display = ['trainee', 'company', 'week_number', 'performance_score', 'attendance_confirmed']
    # فلتر حسب رقم الأسبوع
    list_filter = ['week_number']


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    """إدارة سجلات الحضور في لوحة التحكم
    يعرض المتدرب والتاريخ والحالة ووقتي الحضور والانصراف
    """

    # الأعمدة المعروضة في قائمة سجلات الحضور
    list_display = ['trainee', 'date', 'status', 'check_in_time', 'check_out_time']
    # فلتر حسب حالة الحضور
    list_filter = ['status']
