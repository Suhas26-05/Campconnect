from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        if user.is_authenticated and user.user_type == '3' and hasattr(user, 'student') and user.student.is_suspended:
            logout(request)
            return redirect(reverse('login_page'))

        if user.is_authenticated:
            if user.user_type == '1':
                if modulename in ['main_app.student_views', 'main_app.parent_views']:
                    return redirect(reverse('admin_home'))
            elif user.user_type == '2':
                if modulename in ['main_app.student_views', 'main_app.hod_views', 'main_app.parent_views']:
                    return redirect(reverse('staff_home'))
            elif user.user_type == '3':
                if modulename in ['main_app.hod_views', 'main_app.staff_views', 'main_app.parent_views']:
                    return redirect(reverse('student_home'))
            elif user.user_type == '4':
                if modulename in ['main_app.hod_views', 'main_app.staff_views', 'main_app.student_views']:
                    return redirect(reverse('parent_home'))
            else:
                return redirect(reverse('login_page'))
            return None

        allowed_paths = {
            reverse('login_page'),
            reverse('user_login'),
        }
        if request.path in allowed_paths or modulename == 'django.contrib.auth.views':
            return None
        return redirect(reverse('login_page'))
