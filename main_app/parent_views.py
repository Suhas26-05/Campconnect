from itertools import groupby

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import FeedbackParentForm, ParentEditForm
from .models import AttendanceReport, NotificationParent, Parent, ParentFeedback, Student, StudentResult


def _save_profile_picture(uploaded_file):
    if not uploaded_file:
        return None
    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)
    return fs.url(filename)


def parent_home(request):
    parent = get_object_or_404(Parent, admin=request.user)
    student = parent.student
    non_semester_results = StudentResult.objects.filter(student=student).exclude(
        result_type='semester'
    ).order_by('result_type', 'assessment_name', 'subject__name') if student else []
    semester_results = StudentResult.objects.filter(student=student, result_type='semester').order_by(
        'assessment_name', 'subject__name'
    ) if student else []
    semester_groups = [
        {'semester_name': semester_name, 'results': list(results)}
        for semester_name, results in groupby(semester_results, key=lambda result: result.assessment_name)
    ] if student else []
    context = {
        'page_title': 'Parent Homepage',
        'parent': parent,
        'student': student,
        'results': non_semester_results,
        'semester_groups': semester_groups,
        'attendance_count': AttendanceReport.objects.filter(student=student).count() if student else 0,
        'present_count': AttendanceReport.objects.filter(student=student, status=True).count() if student else 0,
        'absent_count': AttendanceReport.objects.filter(student=student, status=False).count() if student else 0,
        'recent_notifications': NotificationParent.objects.filter(
            parent=parent,
            hide_from_dashboard=False,
        ).order_by('-created_at')[:5],
    }
    return render(request, 'parent_template/home_content.html', context)


def parent_view_notification(request):
    parent = get_object_or_404(Parent, admin=request.user)
    context = {
        'notifications': NotificationParent.objects.filter(parent=parent),
        'page_title': "View Notifications",
    }
    return render(request, "parent_template/parent_view_notification.html", context)


def parent_clear_notifications(request):
    if request.method == 'POST':
        parent = get_object_or_404(Parent, admin=request.user)
        NotificationParent.objects.filter(parent=parent, hide_from_dashboard=False).update(hide_from_dashboard=True)
        messages.success(request, "Parent dashboard notifications cleared.")
    return redirect(reverse('parent_home'))


def parent_view_profile(request):
    parent = get_object_or_404(Parent, admin=request.user)
    form = ParentEditForm(request.POST or None, request.FILES or None, instance=parent)
    context = {'form': form, 'page_title': 'View/Edit Profile'}

    if request.method == 'POST':
        if form.is_valid():
            try:
                admin = parent.admin
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
                roll_number = form.cleaned_data.get('student_roll_number')
                if roll_number:
                    parent.student = Student.objects.get(roll_number=roll_number)
                admin.save()
                parent.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('parent_view_profile'))
            except Exception as e:
                messages.error(request, f"Error Occurred While Updating Profile: {e}")
        else:
            messages.error(request, "Invalid Data Provided")

    return render(request, "parent_template/parent_view_profile.html", context)


def parent_feedback(request):
    parent = get_object_or_404(Parent, admin_id=request.user.id)
    form = FeedbackParentForm(request.POST or None)
    context = {
        'form': form,
        'feedbacks': ParentFeedback.objects.filter(parent=parent),
        'page_title': 'Parent Feedback',
    }

    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.parent = parent
                obj.save()
                messages.success(request, "Feedback submitted for review.")
                return redirect(reverse('parent_feedback'))
            except Exception:
                messages.error(request, "Could not submit feedback!")
        else:
            messages.error(request, "Form has errors!")

    return render(request, "parent_template/parent_feedback.html", context)
