from django.contrib import admin

from .models import (
    Course,
    CustomUser,
    NotificationParent,
    NotificationStaff,
    NotificationStudent,
    Parent,
    ParentFeedback,
    Session,
    Staff,
    Student,
    StudentResult,
    Subject,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_active')


admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Session)
admin.site.register(StudentResult)
admin.site.register(NotificationStudent)
admin.site.register(NotificationStaff)
admin.site.register(NotificationParent)
admin.site.register(ParentFeedback)
