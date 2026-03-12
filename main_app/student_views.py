import math
from datetime import datetime
from itertools import groupby

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import FeedbackStudentForm, LeaveReportStudentForm, StudentEditForm
from .models import (
    Attendance,
    AttendanceReport,
    Course,
    FeedbackStudent,
    LeaveReportStudent,
    NotificationStudent,
    Student,
    StudentResult,
    Subject,
)


def _save_profile_picture(uploaded_file):
    if not uploaded_file:
        return None
    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)
    return fs.url(filename)


def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present / total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)

    subject_name = []
    data_present = []
    data_absent = []
    subjects = Subject.objects.filter(course=student.course)
    for subject in subjects:
        attendance = Attendance.objects.filter(subject=subject)
        present_count = AttendanceReport.objects.filter(attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(attendance__in=attendance, status=False, student=student).count()
        subject_name.append(subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)

    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'recent_notifications': NotificationStudent.objects.filter(
            student=student,
            hide_from_dashboard=False,
        ).order_by('-created_at')[:5],
        'recent_leave_requests': LeaveReportStudent.objects.filter(student=student).order_by('-created_at')[:5],
        'page_title': 'Student Homepage',
    }
    return render(request, 'student_template/home_content.html', context)


@csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        course = get_object_or_404(Course, id=student.course.id)
        context = {
            'subjects': Subject.objects.filter(course=course),
            'page_title': 'View Attendance',
        }
        return render(request, 'student_template/student_view_attendance.html', context)

    subject = get_object_or_404(Subject, id=request.POST.get('subject'))
    start_date = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d")
    end_date = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d")
    attendance = Attendance.objects.filter(date__range=(start_date, end_date), subject=subject)
    attendance_reports = AttendanceReport.objects.filter(attendance__in=attendance, student=student)
    json_data = [{"date": str(report.attendance.date), "status": report.status} for report in attendance_reports]
    return JsonResponse(json_data, safe=False)


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave',
    }
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = student
            obj.save()
            messages.success(request, "Application for leave has been submitted for review")
            return redirect(reverse('student_apply_leave'))
        messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback',
    }
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = student
            obj.save()
            messages.success(request, "Feedback submitted for review")
            return redirect(reverse('student_feedback'))
        messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None, instance=student)
    context = {'form': form, 'page_title': 'View/Edit Profile'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                admin = student.admin
                profile_pic = _save_profile_picture(request.FILES.get('profile_pic'))
                if form.cleaned_data.get('password'):
                    admin.set_password(form.cleaned_data['password'])
                if profile_pic:
                    admin.profile_pic = profile_pic
                admin.first_name = form.cleaned_data['first_name']
                admin.last_name = form.cleaned_data['last_name']
                admin.email = form.cleaned_data['email']
                admin.address = form.cleaned_data['address']
                admin.gender = form.cleaned_data['gender']
                student.roll_number = form.cleaned_data['roll_number']
                admin.save()
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            except Exception as e:
                messages.error(request, f"Error Occured While Updating Profile {e}")
        else:
            messages.error(request, "Invalid Data Provided")

    return render(request, "student_template/student_view_profile.html", context)


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    context = {
        'notifications': NotificationStudent.objects.filter(student=student),
        'page_title': "View Notifications",
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_clear_notifications(request):
    if request.method == 'POST':
        student = get_object_or_404(Student, admin=request.user)
        NotificationStudent.objects.filter(student=student, hide_from_dashboard=False).update(hide_from_dashboard=True)
        messages.success(request, "Student dashboard notifications cleared.")
    return redirect(reverse('student_home'))


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    context = {
        'results': StudentResult.objects.filter(student=student).exclude(result_type='semester').order_by('subject__name', 'result_type', 'assessment_name'),
        'page_title': "Unit and Mid Results",
    }
    return render(request, "student_template/student_view_result.html", context)


def student_view_semester_result(request):
    student = get_object_or_404(Student, admin=request.user)
    semester_results = StudentResult.objects.filter(
        student=student,
        result_type='semester',
    ).order_by('assessment_name', 'subject__name')
    grouped_results = [
        {'semester_name': semester_name, 'results': list(results)}
        for semester_name, results in groupby(semester_results, key=lambda result: result.assessment_name)
    ]
    context = {
        'semester_groups': grouped_results,
        'page_title': "Semester Results",
    }
    return render(request, "student_template/student_view_semester_result.html", context)
