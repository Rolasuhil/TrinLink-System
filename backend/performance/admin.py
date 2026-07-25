from django.contrib import admin
from .models import SupervisionAssignment, Report, WorkReport, PerformanceReport, DailyAttendance


@admin.register(SupervisionAssignment)
class SupervisionAssignmentAdmin(admin.ModelAdmin):
    list_display = ['supervisor', 'trainee', 'role', 'status', 'assignment_date']
    list_filter = ['status', 'role']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'week_number', 'grade', 'report_date']


@admin.register(WorkReport)
class WorkReportAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'task_title', 'performance_rating', 'submitted_at']


@admin.register(PerformanceReport)
class PerformanceReportAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'company', 'week_number', 'performance_score', 'attendance_confirmed']
    list_filter = ['week_number']


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ['trainee', 'date', 'status', 'check_in_time', 'check_out_time']
    list_filter = ['status']
