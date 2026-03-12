from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject


def redirect_user_by_role(user):
    if user.user_type == '1':
        return redirect(reverse("admin_home"))
    if user.user_type == '2':
        return redirect(reverse("staff_home"))
    if user.user_type == '3':
        return redirect(reverse("student_home"))
    if user.user_type == '4':
        return redirect(reverse("parent_home"))
    return redirect(reverse("login_page"))


def login_page(request):
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")

    try:
        num1 = int(request.POST.get('num1', 0))
        num2 = int(request.POST.get('num2', 0))
        user_answer = int(request.POST.get('captcha-answer', 0))
    except (TypeError, ValueError):
        messages.error(request, "Invalid CAPTCHA input.")
        return redirect('/')

    if user_answer != num1 + num2:
        messages.error(request, "Incorrect CAPTCHA. Try again.")
        return redirect('/')

    user = EmailBackend().authenticate(
        request,
        username=request.POST.get('email'),
        password=request.POST.get('password'),
    )
    if user is None:
        messages.error(request, "Invalid login details")
        return redirect('/')

    if user.user_type == '3' and hasattr(user, 'student') and user.student.is_suspended:
        messages.error(request, "Your account is suspended. Please contact the HOD.")
        return redirect('/')

    login(request, user)
    return redirect_user_by_role(user)


def logout_user(request):
    if request.user is not None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    subject = get_object_or_404(Subject, id=subject_id)
    session = get_object_or_404(Session, id=session_id)
    attendance = Attendance.objects.filter(subject=subject, session=session)
    attendance_list = [
        {
            "id": attd.id,
            "attendance_date": str(attd.date),
            "session": attd.session.id,
        }
        for attd in attendance
    ]
    return JsonResponse(attendance_list, safe=False)
