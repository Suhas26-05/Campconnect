from django import forms
from django.forms.widgets import DateInput

from .models import (
    Admin,
    Course,
    CustomUser,
    FeedbackStaff,
    FeedbackStudent,
    LeaveReportStaff,
    LeaveReportStudent,
    Parent,
    ParentFeedback,
    Session,
    Staff,
    Student,
    StudentResult,
    Subject,
)


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=CustomUser.GENDER)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    profile_pic = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance is not None and hasattr(instance, 'admin'):
            admin_user = instance.admin
            self.fields['first_name'].initial = admin_user.first_name
            self.fields['last_name'].initial = admin_user.last_name
            self.fields['email'].initial = admin_user.email
            self.fields['gender'].initial = admin_user.gender
            self.fields['address'].initial = admin_user.address
            self.fields['profile_pic'].required = False
            self.fields['password'].widget.attrs['placeholder'] = (
                "Fill this only if you wish to update password"
            )
        else:
            self.fields['password'].required = True
            self.fields['profile_pic'].required = True

    def clean_email(self):
        form_email = self.cleaned_data['email'].lower()
        if self.instance.pk is None:
            if CustomUser.objects.filter(email=form_email).exists():
                raise forms.ValidationError("The given email is already registered")
            return form_email

        existing_email = self.instance.admin.email.lower()
        if existing_email != form_email and CustomUser.objects.filter(email=form_email).exists():
            raise forms.ValidationError("The given email is already registered")
        return form_email

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'password', 'profile_pic', 'address']


class StudentForm(CustomUserForm):
    roll_number = forms.CharField(
        label='Student Roll Number',
        help_text='Use a unique academic roll number for linking results, attendance, and parent records.',
    )

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + ['roll_number', 'course', 'session']
        labels = {
            'course': 'Degree Course',
            'session': 'Class Section',
        }
        help_texts = {
            'course': 'Choose the degree course, such as CSE, EEE, or ECE.',
            'session': 'Choose the section for this class, such as A or B.',
        }


class AdminForm(CustomUserForm):
    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class ParentForm(CustomUserForm):
    student_roll_number = forms.CharField(required=True, label='Student Roll Number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and getattr(self.instance, 'student', None):
            self.fields['student_roll_number'].initial = self.instance.student.roll_number

    def clean_student_roll_number(self):
        roll_number = self.cleaned_data['student_roll_number'].strip()
        if not Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("No student found with this roll number")
        return roll_number

    class Meta(CustomUserForm.Meta):
        model = Parent
        fields = CustomUserForm.Meta.fields + ['student_roll_number']


class StaffForm(CustomUserForm):
    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + ['course']
        labels = {
            'course': 'Degree Course',
        }
        help_texts = {
            'course': 'Assign the staff member to the degree course they teach, such as CSE or EEE.',
        }


class CourseForm(FormSettings):
    class Meta:
        model = Course
        fields = ['name']
        labels = {
            'name': 'Degree Course Code',
        }
        help_texts = {
            'name': 'Add a degree course such as CSE, EEE, ECE, or MECH.',
        }


class SubjectForm(FormSettings):
    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']
        labels = {
            'name': 'Subject Name',
            'staff': 'Assigned Staff',
            'course': 'Degree Course',
        }
        help_texts = {
            'name': 'Add a subject that belongs to a degree course, such as AI, ML, DBMS, or Networks.',
            'staff': 'Choose the lecturer responsible for this subject.',
            'course': 'Choose the degree course this subject belongs to.',
        }


class SessionForm(FormSettings):
    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        queryset = Session.objects.filter(name__iexact=name)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("A section with this name already exists")
        return name

    class Meta:
        model = Session
        fields = ['name', 'start_year', 'end_year']
        labels = {
            'name': 'Section Name',
            'start_year': 'Section Start Date',
            'end_year': 'Section End Date',
        }
        help_texts = {
            'name': 'Use a class section label such as A, B, or 21CSE-A.',
            'start_year': 'Academic start date for this section.',
            'end_year': 'Academic end date for this section.',
        }
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    substitute_staff = forms.ModelChoiceField(
        queryset=Staff.objects.none(),
        required=True,
        label='Substitute Teacher',
        empty_label='Select substitute teacher',
        help_text='Choose the staff member who will handle your classes on the leave day.',
    )

    def __init__(self, *args, **kwargs):
        staff = kwargs.pop('staff', None)
        super().__init__(*args, **kwargs)
        queryset = Staff.objects.select_related('admin').order_by('admin__last_name', 'admin__first_name')
        if staff is not None:
            queryset = queryset.exclude(pk=staff.pk)
        self.fields['substitute_staff'].queryset = queryset

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'substitute_staff', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStudentForm(FormSettings):
    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):
    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class FeedbackStudentForm(FormSettings):
    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class FeedbackParentForm(FormSettings):
    class Meta:
        model = ParentFeedback
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Enter your feedback', 'rows': 5}
            ),
        }


class StudentEditForm(StudentForm):
    class Meta(StudentForm.Meta):
        fields = StudentForm.Meta.fields


class StaffEditForm(StaffForm):
    class Meta(StaffForm.Meta):
        fields = CustomUserForm.Meta.fields


class ParentEditForm(ParentForm):
    student_roll_number = forms.CharField(required=False, label='Student Roll Number')

    class Meta(ParentForm.Meta):
        fields = CustomUserForm.Meta.fields + ['student_roll_number']


class EditResultForm(FormSettings):
    result_type = forms.ChoiceField(
        choices=[('unit', 'Unit Test'), ('mid', 'Mid Term')],
        required=True,
        label='Assessment Type',
    )
    assessment_name = forms.CharField(
        required=True,
        label='Assessment Name',
        help_text='Example: Unit 1 or Mid 1',
    )
    session_year = forms.ModelChoiceField(
        label="Section",
        queryset=Session.objects.all(),
        required=True,
    )

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'result_type', 'assessment_name', 'test', 'exam']
