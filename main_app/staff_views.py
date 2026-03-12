import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import FeedbackStaffForm, LeaveReportStaffForm, StaffEditForm
from .models import (
    Attendance,
    AttendanceReport,
    CustomUser,
    FeedbackStaff,
    LeaveReportStaff,
    NotificationParent,
    NotificationStudent,
    NotificationStaff,
    Parent,
    Session,
    Staff,
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


def _notify_parents_for_student(student, message):
    notifications = [
        NotificationParent(parent=parent, message=message)
        for parent in Parent.objects.filter(student=student)
    ]
    if notifications:
        NotificationParent.objects.bulk_create(notifications)


def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    context = {
        'page_title': f'Staff Panel - {staff.admin.last_name} ({staff.course})',
        'total_students': Student.objects.filter(course=staff.course).count(),
        'total_attendance': Attendance.objects.filter(subject__in=subjects).count(),
        'total_leave': LeaveReportStaff.objects.filter(staff=staff).count(),
        'total_subject': subjects.count(),
        'subject_list': [subject.name for subject in subjects],
        'attendance_list': [Attendance.objects.filter(subject=subject).count() for subject in subjects],
        'recent_notifications': NotificationStaff.objects.filter(
            staff=staff,
            hide_from_dashboard=False,
        ).order_by('-created_at')[:5],
        'recent_leave_requests': LeaveReportStaff.objects.filter(staff=staff).order_by('-created_at')[:5],
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    context = {
        'subjects': Subject.objects.filter(staff=staff),
        'sessions': Session.objects.all(),
        'page_title': 'Attendance Desk',
        'attendance_mode': request.GET.get('mode', 'take'),
    }
    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject = get_object_or_404(Subject, id=request.POST.get('subject'))
    session = get_object_or_404(Session, id=request.POST.get('session'))
    students = Student.objects.filter(
        course=subject.course,
        session=session,
        is_suspended=False,
        admin__is_active=True,
    ).select_related('admin')
    student_data = [
        {"id": student.id, "name": f"{student.roll_number} - {student.admin.last_name} {student.admin.first_name}"}
        for student in students
    ]
    return JsonResponse(student_data, safe=False)


@csrf_exempt
def save_attendance(request):
    students = json.loads(request.POST.get('student_ids'))
    session = get_object_or_404(Session, id=request.POST.get('session'))
    subject = get_object_or_404(Subject, id=request.POST.get('subject'))
    attendance, _ = Attendance.objects.get_or_create(
        session=session,
        subject=subject,
        date=request.POST.get('date'),
    )

    allowed_students = {
        student.id: student
        for student in Student.objects.filter(
            course=subject.course,
            session=session,
            is_suspended=False,
            admin__is_active=True,
        ).select_related('admin')
    }

    for student_dict in students:
        student = allowed_students.get(int(student_dict.get('id')))
        if student is None:
            continue
        AttendanceReport.objects.update_or_create(
            student=student,
            attendance=attendance,
            defaults={'status': bool(student_dict.get('status'))},
        )
        status_text = "Present" if student_dict.get('status') else "Absent"
        _notify_parents_for_student(
            student,
            f"Attendance update for {student.roll_number} on {attendance.date}: {status_text}",
        )

    return HttpResponse("OK")


def staff_update_attendance(request):
    return redirect(f"{reverse('staff_take_attendance')}?mode=update")


@csrf_exempt
def get_student_attendance(request):
    attendance = get_object_or_404(Attendance, id=request.POST.get('attendance_date_id'))
    attendance_data = AttendanceReport.objects.filter(
        attendance=attendance,
        student__is_suspended=False,
        student__admin__is_active=True,
    ).select_related('student__admin')
    student_data = [
        {
            "id": row.student.admin.id,
            "name": f"{row.student.roll_number} - {row.student.admin.last_name} {row.student.admin.first_name}",
            "status": row.status,
        }
        for row in attendance_data
    ]
    return JsonResponse(student_data, safe=False)


@csrf_exempt
def update_attendance(request):
    students = json.loads(request.POST.get('student_ids'))
    attendance = get_object_or_404(Attendance, id=request.POST.get('date'))

    for student_dict in students:
        student = Student.objects.filter(
            admin_id=student_dict.get('id'),
            is_suspended=False,
            admin__is_active=True,
        ).first()
        if student is None:
            continue
        attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
        attendance_report.status = bool(student_dict.get('status'))
        attendance_report.save()
        status_text = "Present" if attendance_report.status else "Absent"
        _notify_parents_for_student(
            student,
            f"Attendance update for {student.roll_number} on {attendance.date}: {status_text}",
        )

    return HttpResponse("OK")


def staff_apply_leave(request):
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    form = LeaveReportStaffForm(request.POST or None, staff=staff)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff).select_related('substitute_staff__admin'),
        'page_title': 'Apply for Leave',
    }
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.staff = staff
            obj.save()
            NotificationStaff.objects.create(
                staff=obj.substitute_staff,
                message=(
                    f"{staff.admin.get_full_name() or staff.admin.email} requested you as substitute teacher "
                    f"for leave on {obj.date}. Review it in your notifications."
                ),
            )
            messages.success(
                request,
                "Leave request submitted. The selected substitute teacher must accept it before HOD review.",
            )
            return redirect(reverse('staff_apply_leave'))
        messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback',
    }
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.staff = staff
            obj.save()
            messages.success(request, "Feedback submitted for review")
            return redirect(reverse('staff_feedback'))
        messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None, instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                admin = staff.admin
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
                admin.save()
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            except Exception as e:
                messages.error(request, f"Error Occured While Updating Profile {e}")
        else:
            messages.error(request, "Invalid Data Provided")

    return render(request, "staff_template/staff_view_profile.html", context)


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    context = {
        'notifications': NotificationStaff.objects.filter(staff=staff).order_by('-created_at'),
        'substitute_leave_requests': LeaveReportStaff.objects.filter(
            substitute_staff=staff,
            substitute_status=0,
            status=0,
        ).select_related('staff__admin', 'staff__course'),
        'page_title': "View Notifications",
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_notifications(request):
    staff = get_object_or_404(Staff, admin=request.user)
    students = CustomUser.objects.filter(
        user_type='3',
        student__course=staff.course,
    ).select_related('student')
    parents = CustomUser.objects.filter(
        user_type='4',
        parent__student__course=staff.course,
    ).select_related('parent', 'parent__student')
    context = {
        'page_title': 'Notifications',
        'students': students,
        'parents': parents,
    }
    return render(request, 'staff_template/notifications.html', context)


def staff_respond_leave_substitution(request, leave_id, response):
    if request.method != 'POST':
        return redirect(reverse('staff_view_notification'))

    staff = get_object_or_404(Staff, admin=request.user)
    leave = get_object_or_404(
        LeaveReportStaff.objects.select_related('staff__admin', 'substitute_staff__admin'),
        id=leave_id,
        substitute_staff=staff,
        status=0,
    )

    if leave.substitute_status != 0:
        messages.info(request, "You have already responded to this substitute request.")
        return redirect(reverse('staff_view_notification'))

    if response == 'accept':
        leave.substitute_status = 1
        leave.save(update_fields=['substitute_status', 'updated_at'])
        NotificationStaff.objects.create(
            staff=leave.staff,
            message=(
                f"{staff.admin.get_full_name() or staff.admin.email} accepted your substitute request "
                f"for leave on {leave.date}. The leave is now ready for HOD review."
            ),
        )
        messages.success(request, "Substitute request accepted and forwarded for HOD review.")
    else:
        leave.substitute_status = -1
        leave.save(update_fields=['substitute_status', 'updated_at'])
        NotificationStaff.objects.create(
            staff=leave.staff,
            message=(
                f"{staff.admin.get_full_name() or staff.admin.email} declined your substitute request "
                f"for leave on {leave.date}. Please submit a new leave request with another substitute teacher."
            ),
        )
        messages.success(request, "Substitute request declined. HOD review will not proceed for this request.")

    return redirect(reverse('staff_view_notification'))


def staff_clear_notifications(request):
    if request.method == 'POST':
        staff = get_object_or_404(Staff, admin=request.user)
        NotificationStaff.objects.filter(staff=staff, hide_from_dashboard=False).update(hide_from_dashboard=True)
        messages.success(request, "Staff dashboard notifications cleared.")
    return redirect(reverse('staff_home'))


@csrf_exempt
def staff_send_student_notification(request):
    if request.method != 'POST':
        return HttpResponse("False")

    staff = get_object_or_404(Staff, admin=request.user)
    student = get_object_or_404(Student, admin_id=request.POST.get('id'))
    if student.course_id != staff.course_id:
        return HttpResponse("False")
    message = request.POST.get('message')
    if not message:
        return HttpResponse("False")
    NotificationStudent.objects.create(student=student, message=message)
    _notify_parents_for_student(student, f"Message from staff for {student.roll_number}: {message}")
    return HttpResponse("True")


@csrf_exempt
def staff_send_student_notification_to_all(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    staff = get_object_or_404(Staff, admin=request.user)
    message = (request.POST.get('message') or '').strip()
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required.'}, status=400)

    students = Student.objects.filter(course=staff.course, is_suspended=False, admin__is_active=True)
    student_notifications = [NotificationStudent(student=student, message=message) for student in students]
    if student_notifications:
        NotificationStudent.objects.bulk_create(student_notifications)
        for student in students:
            _notify_parents_for_student(student, f"Message from staff for {student.roll_number}: {message}")

    return JsonResponse(
        {
            'success': True,
            'message': f'Notification sent to {students.count()} students and their linked parents.',
        }
    )


@csrf_exempt
def staff_send_notification_to_everyone(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    staff = get_object_or_404(Staff, admin=request.user)
    message = (request.POST.get('message') or '').strip()
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required.'}, status=400)

    students = list(
        Student.objects.filter(course=staff.course, is_suspended=False, admin__is_active=True).select_related('admin')
    )
    student_notifications = [NotificationStudent(student=student, message=message) for student in students]
    parent_notifications = []

    for student in students:
        parent_notifications.extend(
            NotificationParent(parent=parent, message=f"Message from staff for {student.roll_number}: {message}")
            for parent in Parent.objects.filter(student=student)
        )

    if student_notifications:
        NotificationStudent.objects.bulk_create(student_notifications)
    if parent_notifications:
        NotificationParent.objects.bulk_create(parent_notifications)

    return JsonResponse(
        {
            'success': True,
            'student_count': len(student_notifications),
            'parent_count': len(parent_notifications),
            'message': 'Notification sent to all students and parents.',
        }
    )


@csrf_exempt
def staff_send_parent_notification(request):
    if request.method != 'POST':
        return HttpResponse("False")

    staff = get_object_or_404(Staff, admin=request.user)
    parent = get_object_or_404(Parent, admin_id=request.POST.get('id'))
    if parent.student is None or parent.student.course_id != staff.course_id:
        return HttpResponse("False")

    message = (request.POST.get('message') or '').strip()
    if not message:
        return HttpResponse("False")

    NotificationParent.objects.create(parent=parent, message=message)
    return HttpResponse("True")


@csrf_exempt
def staff_send_parent_notification_to_all(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    staff = get_object_or_404(Staff, admin=request.user)
    message = (request.POST.get('message') or '').strip()
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required.'}, status=400)

    parents = Parent.objects.filter(student__course=staff.course).select_related('admin')
    notifications = [NotificationParent(parent=parent, message=message) for parent in parents]
    if notifications:
        NotificationParent.objects.bulk_create(notifications)

    return JsonResponse(
        {
            'success': True,
            'message': f'Notification sent to {parents.count()} parents.',
        }
    )


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    context = {
        'page_title': 'Result Desk',
        'subjects': subjects,
        'sessions': Session.objects.all(),
        'result_mode': request.GET.get('mode', 'add'),
    }
    if request.method == 'POST':
        try:
            mode = request.POST.get('result_mode', 'add')
            student = get_object_or_404(
                Student,
                id=request.POST.get('student') or request.POST.get('student_list'),
            )
            subject = get_object_or_404(Subject, id=request.POST.get('subject'), staff=staff)
            result_type = request.POST.get('result_type')
            assessment_name = (request.POST.get('assessment_name') or '').strip()
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            if result_type not in {'unit', 'mid'} or not assessment_name:
                raise ValueError("Assessment type and name are required")

            if mode == 'edit':
                result = StudentResult.objects.get(
                    student=student,
                    subject=subject,
                    result_type=result_type,
                    assessment_name=assessment_name,
                )
                result.test = test
                result.exam = exam
                result.save()
                created = False
            else:
                result, created = StudentResult.objects.update_or_create(
                    student=student,
                    subject=subject,
                    result_type=result_type,
                    assessment_name=assessment_name,
                    defaults={'test': test, 'exam': exam},
                )
            notification_text = (
                f"{result.get_result_type_display()} {result.assessment_name} updated for {student.roll_number} in {subject.name}. "
                f"Internal: {result.test}, External: {result.exam}"
            )
            NotificationStudent.objects.create(student=student, message=notification_text)
            _notify_parents_for_student(student, notification_text)
            messages.success(request, "Scores Saved" if created else "Scores Updated")
            return redirect(f"{reverse('staff_add_result')}?mode={mode}")
        except StudentResult.DoesNotExist:
            messages.warning(request, "No matching result exists to update")
        except Exception:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    student = get_object_or_404(Student, id=request.POST.get('student'))
    subject = get_object_or_404(Subject, id=request.POST.get('subject'))
    result = StudentResult.objects.filter(
        student=student,
        subject=subject,
        result_type=request.POST.get('result_type'),
        assessment_name=request.POST.get('assessment_name'),
    ).first()
    if result is None:
        return HttpResponse("False")
    return HttpResponse(json.dumps({'exam': result.exam, 'test': result.test}))
