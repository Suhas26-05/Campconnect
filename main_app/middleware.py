from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Current user
        if user.is_authenticated:
            if user.user_type == '1':  # HOD/Admin
                if modulename == 'main_app.student_views' or modulename == 'main_app.parent_views':
                    return redirect(reverse('admin_home'))
            elif user.user_type == '2':  # Staff
                if modulename in ['main_app.student_views', 'main_app.hod_views', 'main_app.parent_views']:
                    return redirect(reverse('staff_home'))
            elif user.user_type == '3':  # Student
                if modulename in ['main_app.hod_views', 'main_app.staff_views', 'main_app.parent_views']:
                    return redirect(reverse('student_home'))
            elif user.user_type == '4':  # Parent
                if modulename in ['main_app.hod_views', 'main_app.staff_views', 'main_app.student_views']:
                    return redirect(reverse('parent_home'))  # Ensure 'parent_home' is defined in your URLs
            else:
                return redirect(reverse('login_page'))  # Fallback for unidentified user types
        else:
            # Allow access to login and authentication-related paths
            if request.path in [reverse('login_page'), reverse('user_login')] or modulename == 'django.contrib.auth.views':
                pass
            else:
                return redirect(reverse('login_page'))
