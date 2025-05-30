from django.shortcuts import render, get_object_or_404
from .models import Parent, NotificationParent
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from .forms import ParentEditForm
from .models import Parent
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import ParentFeedback, Parent
from .forms import FeedbackParentForm

def parent_home(request):
    return render(request, 'parent_template/home_content.html')

def parent_view_notification(request):
    parent = get_object_or_404(Parent, admin=request.user)
    notifications = NotificationParent.objects.filter(parent=parent)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "parent_template/parent_view_notification.html", context)


def parent_view_profile(request):
    parent = get_object_or_404(Parent, admin=request.user)
    form = ParentEditForm(request.POST or None, request.FILES or None, instance=parent)
    context = {
        'form': form,
        'page_title': 'View/Edit Profile'
    }

    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None

                admin = parent.admin
                if password:
                    admin.set_password(password)
                if passport:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url

                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                parent.save()

                messages.success(request, "Profile Updated!")
                return redirect(reverse('parent_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, f"Error Occurred While Updating Profile: {e}")

    return render(request, "parent_template/parent_view_profile.html", context)


def parent_feedback(request):
    # Check if the parent exists
    parent = get_object_or_404(Parent, admin_id=request.user.id)
    
    # Create the form and pass it to the template
    form = FeedbackParentForm(request.POST or None)
    
    # Display the feedbacks sent by this parent (optional)
    context = {
        'form': form,
        'feedbacks': ParentFeedback.objects.filter(parent=parent),  # Show feedback submitted by the parent
        'page_title': 'Parent Feedback'
    }
    
    # Handle POST request to save feedback
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)  # Don't save yet, we want to set the parent manually
                obj.parent = parent  # Set the parent field
                obj.save()  # Save the feedback
                messages.success(request, "Feedback submitted for review.")
                return redirect(reverse('parent_feedback'))  # Redirect after successful submission
            except Exception:
                messages.error(request, "Could not submit feedback!")
        else:
            messages.error(request, "Form has errors!")
    
    return render(request, "parent_template/parent_feedback.html", context)
