from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Q
from .models import PasswordResetToken, MentorProfile, MenteeProfile, Skill, Session, hire_developer, ContactMessage
from .models import Category, Question, Option, TestAttempt, AttemptAnswer
from .forms import CategoryForm, QuestionForm, OptionFormSet
import hashlib
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
from decimal import Decimal
from main.forms import HireDeveloperForm, ContactForm,SkillForm

# Create your views here.

def home(request):
    return render(request,"home.html")

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'contact.html', { 'form': form })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                # Redirect staff to custom admin dashboard
                if user.is_staff:
                    return redirect('admin_dashboard')
                # If the user doesn't yet have a mentee profile, send them to create one
                if not hasattr(user, 'mentee_profile'):
                    return redirect('mentee_profile_view')

                return redirect('home')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
        else:
            messages.error(request, "Please fill in all fields.")
    
    return render(request, "login.html")

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        # Validation
        if not all([name, username, email, password, confirm_password]):
            messages.error(request, "Please fill in all fields.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email address already exists. Please use a different email.")
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name
                )
                user.save()
                messages.success(request, "Account created successfully! Please log in.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    
    return render(request, "signup.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        
        if email or username:
            try:
                # Find user by username or email
                user = None
                if username:
                    user = User.objects.get(username=username)
                elif email:
                    user = User.objects.get(email=email)
                
                if not user:
                    messages.error(request, "No user found with the provided information.")
                    return render(request, 'forgot_password.html')
                
                # Check if user has an email address
                if not user.email:
                    messages.error(request, f"User '{user.username}' does not have an email address registered. Please contact support for password reset assistance.")
                    return render(request, 'forgot_password.html')
                
                # Generate reset token
                token = get_random_string(50)
                
                # Create or update reset token
                reset_token, created = PasswordResetToken.objects.get_or_create(
                    user=user,
                    defaults={'token': token}
                )
                if not created:
                    reset_token.token = token
                    reset_token.used = False
                    reset_token.created_at = timezone.now()
                    reset_token.save()
                
                # Send email
                reset_url = f"{request.build_absolute_uri('/')}reset-password/{token}/"
                try:
                    send_mail(
                        'Password Reset Request - CodeMentorHub',
                        f'Hello {user.first_name or user.username},\n\n'
                        f'You requested a password reset for your CodeMentorHub account.\n\n'
                        f'Click the following link to reset your password:\n{reset_url}\n\n'
                        f'This link will expire in 1 hour.\n\n'
                        f'If you did not request this password reset, please ignore this email.\n\n'
                        f'Best regards,\nCodeMentorHub Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f"Password reset link has been sent to {user.email}. Please check your email.")
                except Exception as e:
                    # If email sending fails, show the link in the message for development
                    messages.success(request, f"Password reset link generated. Email sending failed, but you can use this link: {reset_url}")
                
                return redirect('login')
                
            except User.DoesNotExist:
                messages.error(request, "No user found with the provided information.")
        else:
            messages.error(request, "Please provide either username or email.")
    
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    try:
        reset_token = get_object_or_404(PasswordResetToken, token=token)
        
        if not reset_token.is_valid():
            messages.error(request, "This reset link has expired or been used. Please request a new one.")
            return redirect('forgot_password')
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password and confirm_password:
                if password == confirm_password:
                    if len(password) >= 8:
                        # Update user password
                        user = reset_token.user
                        user.set_password(password)
                        user.save()
                        
                        # Mark token as used
                        reset_token.used = True
                        reset_token.save()
                        
                        messages.success(request, "Your password has been reset successfully. Please log in with your new password.")
                        return redirect('login')
                    else:
                        messages.error(request, "Password must be at least 8 characters long.")
                else:
                    messages.error(request, "Passwords do not match.")
            else:
                messages.error(request, "Please fill in all fields.")
        
        return render(request, 'reset_password.html', {'token': token})
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid reset link.")
        return redirect('forgot_password')

# Mentor Views

@login_required
def mentor_profile(request):
    """View mentor profile (read-only)."""
    try:
        mentor_profile = request.user.mentor_profile
    except MentorProfile.DoesNotExist:
        messages.info(request, "You don't have a mentor profile. Please contact an admin to be appointed as a mentor.")
        return redirect('home')
    # Editing the live mentor profile by the user is disabled.
    if request.method == 'POST':
        messages.info(request, "Direct editing is disabled. Please contact an admin for changes.")
        return redirect('mentor_profile')

    skills = Skill.objects.all()
    return render(request, 'mentor_profile.html', {
        'mentor_profile': mentor_profile,
        'skills': skills
    })


@login_required
def mentor_profile_edit(request):
    """Allow the mentor (owner of the MentorProfile) to edit their profile, including uploading a profile picture.
    Access restricted to the linked user only.
    """
    try:
        mentor_profile = request.user.mentor_profile
    except MentorProfile.DoesNotExist:
        messages.error(request, "You don't have a mentor profile to edit.")
        return redirect('home')

    if request.method == 'POST':
        # Only allow the owner to update their profile
        mentor_profile.full_name = request.POST.get('full_name', mentor_profile.full_name)
        mentor_profile.headline = request.POST.get('headline', mentor_profile.headline)
        mentor_profile.bio = request.POST.get('bio', mentor_profile.bio)
        mentor_profile.location = request.POST.get('location', mentor_profile.location)
        mentor_profile.linkedin_url = request.POST.get('linkedin_url', mentor_profile.linkedin_url)
        mentor_profile.github_url = request.POST.get('github_url', mentor_profile.github_url)
        try:
            mentor_profile.years_of_experience = int(request.POST.get('years_of_experience') or mentor_profile.years_of_experience)
        except Exception:
            pass
        try:
            from decimal import Decimal
            mentor_profile.hourly_rate = Decimal(request.POST.get('hourly_rate') or mentor_profile.hourly_rate)
        except Exception:
            pass
        try:
            mentor_profile.session_duration = int(request.POST.get('session_duration') or mentor_profile.session_duration)
        except Exception:
            pass
        mentor_profile.available_for = request.POST.get('available_for', mentor_profile.available_for)

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            mentor_profile.profile_picture = request.FILES['profile_picture']

        mentor_profile.save()
        # Update skills if provided as comma-separated
        skills_input = request.POST.get('skills_input', '')
        if skills_input:
            raw_skills = [s.strip() for s in skills_input.split(',') if s.strip()]
            skill_objs = []
            for s in raw_skills:
                obj, _ = Skill.objects.get_or_create(name=s)
                skill_objs.append(obj)
            mentor_profile.skills.set(skill_objs)

        messages.success(request, 'Mentor profile updated successfully.')
        return redirect('mentor_profile')

    return render(request, 'mentor_edit.html', {'mentor_profile': mentor_profile, 'skills': Skill.objects.all()})

def find_mentors(request):
    """Public view to find approved mentors"""
    mentors = MentorProfile.objects.filter(is_approved=True, application_status='approved')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        mentors = mentors.filter(
            Q(full_name__icontains=search_query) |
            Q(headline__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(skills__name__icontains=search_query)
        ).distinct()
    
    # Filter by skills
    skill_filter = request.GET.get('skill')
    if skill_filter:
        mentors = mentors.filter(skills__name__icontains=skill_filter)
    
    # Pagination
    paginator = Paginator(mentors, 12)
    page_number = request.GET.get('page')
    mentors = paginator.get_page(page_number)
    
    skills = Skill.objects.all()
    
    return render(request, 'find_mentors.html', {
        'mentors': mentors,
        'skills': skills,
        'search_query': search_query,
        'selected_skill': skill_filter
    })

def mentor_detail(request, mentor_id):
    """View individual mentor profile"""
    mentor = get_object_or_404(MentorProfile, id=mentor_id, is_approved=True, application_status='approved')
    return render(request, 'mentor_detail.html', {'mentor': mentor})

# Mentee Views
@login_required
def mentee_profile_view(request):
    """Read-only view of the mentee profile. Shows profile picture, details,
    and links to edit profile and change password (only for the owner).
    """
    default_name = request.user.first_name or request.user.username
    mentee_profile, created = MenteeProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': default_name,
            'interests': '',
            'current_level': 'beginner',
            'goal': ''
        }
    )

    if created:
        messages.info(request, "A profile was created for you. You can edit it using the link below.")

    return render(request, 'mentee_profile_view.html', {'mentee_profile': mentee_profile})


@login_required
def mentee_profile_edit(request):
    """Edit (or create) the mentee profile. Only the owner can edit their profile.
    This reuses the existing template `mentee_profile.html` which contains the edit form.
    """
    default_name = request.user.first_name or request.user.username
    mentee_profile, created = MenteeProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': default_name,
            'interests': '',
            'current_level': 'beginner',
            'goal': ''
        }
    )

    if request.method == 'POST':
        # Update mentee profile
        mentee_profile.full_name = request.POST.get('full_name', mentee_profile.full_name)
        mentee_profile.interests = request.POST.get('interests', mentee_profile.interests)
        mentee_profile.current_level = request.POST.get('current_level', mentee_profile.current_level)
        mentee_profile.goal = request.POST.get('goal', mentee_profile.goal)

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            mentee_profile.profile_picture = request.FILES['profile_picture']

        mentee_profile.save()

        if created:
            messages.success(request, "Your mentee profile has been created!")
        else:
            messages.success(request, "Your mentee profile has been updated!")

        return redirect('mentee_profile_view')

    return render(request, 'mentee_profile.html', {'mentee_profile': mentee_profile})


@login_required
def change_password(request):
    """Allow a logged-in user to change their password. Only the account owner can change their password.
    Simple form with old_password, new_password, confirm_password.
    """
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not all([old_password, new_password, confirm_password]):
            messages.error(request, "Please fill in all password fields.")
            return render(request, 'change_password.html')

        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return render(request, 'change_password.html')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'change_password.html')

        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters long.")
            return render(request, 'change_password.html')

        # Set new password and keep the user logged in
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Your password has been changed successfully.")
        return redirect('mentee_profile_view')

    return render(request, 'change_password.html')

# -----------------------------
# Custom Admin (staff-only)
# -----------------------------

def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))

def superuser_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_superuser)(view_func))

@staff_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_mentors = MentorProfile.objects.count()
    pending_mentors = MentorProfile.objects.filter(application_status='pending').count()
    approved_mentors = MentorProfile.objects.filter(application_status='approved').count()
    total_skills = Skill.objects.count()
    return render(request, 'admin/dashboard.html', {
        'total_users': total_users,
        'total_mentors': total_mentors,
        'pending_mentors': pending_mentors,
        'approved_mentors': approved_mentors,
        'total_skills': total_skills,
    })

@staff_required
def admin_mentors(request):
    status_filter = request.GET.get('status')
    mentors = MentorProfile.objects.all()
    if status_filter in ['pending', 'approved', 'rejected']:
        mentors = mentors.filter(application_status=status_filter)
    search = request.GET.get('q', '')
    if search:
        mentors = mentors.filter(Q(full_name__icontains=search) | Q(headline__icontains=search) | Q(user__username__icontains=search))
    mentors = mentors.select_related('user').prefetch_related('skills').order_by('-created_at')
    paginator = Paginator(mentors, 20)
    page = request.GET.get('page')
    mentors_page = paginator.get_page(page)
    return render(request, 'admin/mentors.html', {'mentors': mentors_page, 'search': search, 'status_filter': status_filter})

@staff_required
def admin_mentor_approve(request, mentor_id):
    mentor = get_object_or_404(MentorProfile, id=mentor_id)
    mentor.application_status = 'approved'
    mentor.is_approved = True
    mentor.save()
    messages.success(request, f"Approved mentor: {mentor.full_name}")
    return redirect('admin_mentors')

@staff_required
def admin_mentor_reject(request, mentor_id):
    mentor = get_object_or_404(MentorProfile, id=mentor_id)
    mentor.application_status = 'rejected'
    mentor.is_approved = False
    mentor.save()
    messages.info(request, f"Rejected mentor: {mentor.full_name}")
    return redirect('admin_mentors')

@staff_required
def admin_skills(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Skill.objects.get_or_create(name=name)
            messages.success(request, f"Added skill: {name}")
            return redirect('admin_skills')
    skills = Skill.objects.all().order_by('name')
    return render(request, 'admin/skills.html', {'skills': skills})

@staff_required
def delete_skills(request,pk):
    skill=Skill.objects.get(pk=pk)
    skill.delete()
    messages.success(request, f"Deleted skill: {skill.name}")
    return redirect('admin_skills')

@staff_required
def edit_skills(request, pk):
    instance = Skill.objects.get(pk=pk)
    if request.method == 'POST':
        frm = SkillForm(request.POST, instance=instance)
        if frm.is_valid():
            frm.save()
            messages.success(request, f"Updated skill: {instance.name}")
            return redirect('admin_skills')
    else:
        frm = SkillForm(instance=instance)
    
    return render(request, 'admin/edit_skill.html', {'form': frm})

@staff_required
def mentor_view(request,pk):
    isinstance=MentorProfile.objects.get(pk=pk)
    return render(request,'admin/mentor_view.html',{'mentor':isinstance})


@staff_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users_page = paginator.get_page(page)
    return render(request, 'admin/users.html', {'users': users_page})

@staff_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username') or user.username
        email = request.POST.get('email') or ''
        first_name = request.POST.get('first_name') or ''
        is_staff_val = True if request.POST.get('is_staff') == 'on' else False
        if User.objects.exclude(id=user.id).filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.is_staff = is_staff_val
            user.save()
            messages.success(request, 'User updated successfully.')
            return redirect('admin_users')
    return render(request, 'admin/user_form.html', { 'user_obj': user })

@staff_required
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Deleted user {username}.")
        return redirect('admin_users')
    return render(request, 'admin/user_form.html', { 'user_obj': user, 'confirm_delete': True })

@superuser_required
def admin_mentor_add(request):
    skills = Skill.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Admin is adding mentor manually (no user account link)
        user = None

        full_name = request.POST.get('full_name')
        headline = request.POST.get('headline')
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        linkedin_url = request.POST.get('linkedin_url')
        github_url = request.POST.get('github_url')
        years_of_experience = int(request.POST.get('years_of_experience') or 0)

        hourly_rate_raw = request.POST.get('hourly_rate') or '0'
        try:
            hourly_rate = Decimal(hourly_rate_raw)
        except:
            hourly_rate = Decimal('0.00')

        session_duration = int(request.POST.get('session_duration') or 60)
        available_for = request.POST.get('available_for')

        mentor_profile = MentorProfile.objects.create(
            user=None,
            full_name=full_name,
            headline=headline,
            bio=bio,
            location=location,
            linkedin_url=linkedin_url,
            github_url=github_url,
            years_of_experience=years_of_experience,
            hourly_rate=hourly_rate,
            availability={},
            session_duration=session_duration,
            available_for=available_for,
            is_approved=True,
            application_status='approved',
        )

        # ✅ Save selected skills (checkbox values)
        selected_skill_ids = request.POST.getlist('skills')
        if selected_skill_ids:
            mentor_profile.skills.set(selected_skill_ids)

        messages.success(request, 'Mentor added successfully.')
        return redirect('admin_mentors')

    return render(request, 'admin/mentor_form.html', {'skills': skills})

@superuser_required
def admin_mentor_edit(request, mentor_id):
    mentor = get_object_or_404(MentorProfile, id=mentor_id)
    skills = Skill.objects.all().order_by('name')
    if request.method == 'POST':
        mentor.full_name = request.POST.get('full_name') or mentor.full_name
        mentor.headline = request.POST.get('headline') or mentor.headline
        mentor.bio = request.POST.get('bio') or mentor.bio
        mentor.location = request.POST.get('location') or mentor.location
        mentor.linkedin_url = request.POST.get('linkedin_url') or mentor.linkedin_url
        mentor.github_url = request.POST.get('github_url') or mentor.github_url
        try:
            mentor.years_of_experience = int(request.POST.get('years_of_experience') or mentor.years_of_experience)
        except Exception:
            pass
        try:
            mentor.hourly_rate = Decimal(request.POST.get('hourly_rate') or mentor.hourly_rate)
        except Exception:
            pass
        try:
            mentor.session_duration = int(request.POST.get('session_duration') or mentor.session_duration)
        except Exception:
            pass
        mentor.available_for = request.POST.get('available_for') or mentor.available_for
        mentor.is_approved = True
        mentor.application_status = 'approved'
        mentor.save()
        selected_skill_ids = request.POST.getlist('skills')
        mentor.skills.set(selected_skill_ids)
        mentor.save()


        # Skills are managed outside the dashboard; no skill assignment here

        messages.success(request, 'Mentor updated successfully.')
        return redirect('admin_mentors')

    return render(request, 'admin/mentor_form.html', { 'mentor': mentor, 'skills': skills })

@superuser_required
def admin_mentor_delete(request, mentor_id):
    mentor = get_object_or_404(MentorProfile, id=mentor_id)
    if request.method == 'POST':
        name = mentor.full_name
        mentor.delete()
        messages.success(request, f"Deleted mentor {name}.")
        return redirect('admin_mentors')
    return render(request, 'admin/mentor_form.html', { 'mentor': mentor, 'confirm_delete': True })

# -----------------------------
# Session Booking Views
# -----------------------------

class BookingForm(forms.Form):
    session_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    session_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    duration_minutes = forms.IntegerField(initial=60, min_value=30, max_value=180)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def clean(self):
        cleaned = super().clean()
        session_date = cleaned.get('session_date')
        session_time = cleaned.get('session_time')

        if session_date and session_time:
            # Combine date and time and ensure it's not in the past
            try:
                session_dt = datetime.combine(session_date, session_time)
            except Exception:
                raise forms.ValidationError('Invalid date or time.')

            # Make timezone-aware if settings use timezones
            if timezone.is_naive(session_dt):
                session_dt = timezone.make_aware(session_dt, timezone.get_current_timezone())

            now = timezone.now()
            if session_dt < now:
                raise forms.ValidationError('You cannot book a session in the past. Please choose a future date and time.')

        return cleaned

@login_required
def book_session(request, mentor_id):
    """Book a session with a mentor"""
    mentor = get_object_or_404(MentorProfile, id=mentor_id, is_approved=True, application_status='approved')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            session_date = form.cleaned_data['session_date']
            session_time = form.cleaned_data['session_time']
            duration_minutes = form.cleaned_data['duration_minutes']
            notes = form.cleaned_data['notes']
            
            # Check if mentor is available at this time
            existing_session = Session.objects.filter(
                mentor=mentor,
                session_date=session_date,
                session_time=session_time,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if existing_session:
                messages.error(request, "This time slot is already booked. Please choose another time.")
            else:
                # Create session
                session = Session.objects.create(
                    mentor=mentor,
                    mentee=request.user,
                    session_date=session_date,
                    session_time=session_time,
                    duration_minutes=duration_minutes,
                    meeting_notes=notes,
                    amount_paid=(mentor.hourly_rate * (Decimal(duration_minutes) / Decimal('60'))).quantize(Decimal('0.01')),
                    payment_status='pending'
                )
                
                # Store session ID in session for payment flow
                request.session['pending_session_id'] = session.id
                return redirect('payment_page', session_id=session.id)
    else:
        form = BookingForm()
    
    return render(request, 'booking/book_session.html', {
        'mentor': mentor,
        'form': form
    })

@login_required
def payment_page(request, session_id):
    """Dummy payment page"""
    session = get_object_or_404(Session, id=session_id, mentee=request.user, payment_status='pending')
    
    if request.method == 'POST':
        # Simulate payment success
        session.payment_status = 'completed'
        # Do NOT auto-confirm; wait for mentor acceptance
        # Keep status as 'pending' until mentor accepts
        session.save()
        
        messages.success(request, "Payment successful! Your session is awaiting mentor approval.")
        return redirect('session_confirmation', session_id=session.id)
    
    return render(request, 'booking/payment.html', {'session': session})

@login_required
def session_confirmation(request, session_id):
    """Session confirmation page"""
    session = get_object_or_404(Session, id=session_id, mentee=request.user)
    return render(request, 'booking/confirmation.html', {'session': session})

@login_required
def mentor_session_accept(request, session_id):
    """Allow mentor to accept a pending session (confirm it)."""
    try:
        mentor_profile = request.user.mentor_profile
    except MentorProfile.DoesNotExist:
        messages.error(request, "You don't have a mentor profile. Please contact an admin.")
        return redirect('home')

    session = get_object_or_404(Session, id=session_id, mentor=mentor_profile)

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('mentor_session_detail', session_id=session.id)

    if session.status != 'pending':
        messages.info(request, "This session is not pending.")
        return redirect('mentor_session_detail', session_id=session.id)

    session.status = 'confirmed'
    if not session.meeting_link:
        session.generate_meeting_link()
    session.save()

    # Notify both parties
    try:
        send_session_confirmation_emails(session)
    except Exception:
        pass

    messages.success(request, "Session accepted and confirmed. The mentee has been notified.")
    return redirect('mentor_session_detail', session_id=session.id)

@login_required
def mentee_dashboard(request):
    """Mentee dashboard showing upcoming sessions"""
    upcoming_sessions = Session.objects.filter(
        mentee=request.user,
        status__in=['confirmed', 'pending'],
        session_date__gte=timezone.now().date()
    ).order_by('session_date', 'session_time')
    
    past_sessions = Session.objects.filter(
        mentee=request.user,
        status='completed'
    ).order_by('-session_date', '-session_time')[:10]
    cancelled_sessions = Session.objects.filter(
        mentee=request.user,
        status='cancelled'
    ).order_by('-session_date', '-session_time')[:10]
    
    return render(request, 'dashboard/mentee_dashboard.html', {
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'sessions_cancelled': cancelled_sessions
    })

@login_required
def mentor_dashboard(request):
    """Mentor dashboard showing confirmed sessions"""
    try:
        mentor_profile = request.user.mentor_profile
    except MentorProfile.DoesNotExist:
        messages.info(request, "You don't have a mentor profile. Please contact an admin.")
        return redirect('home')
    
    upcoming_sessions = Session.objects.filter(
        mentor=mentor_profile,
        status__in=['confirmed', 'pending'],
        session_date__gte=timezone.now().date()
    ).order_by('session_date', 'session_time')
    
    past_sessions = Session.objects.filter(
        mentor=mentor_profile,
        status='completed'
    ).order_by('-session_date', '-session_time')
    
    return render(request, 'dashboard/mentor_dashboard.html', {
        'mentor_profile': mentor_profile,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions
    })


@login_required
def mentor_session_detail(request, session_id):
    """Show detailed view of a single session for the mentor."""
    try:
        mentor_profile = request.user.mentor_profile
    except MentorProfile.DoesNotExist:
        messages.info(request, "You don't have a mentor profile. Please contact an admin.")
        return redirect('home')

    session = get_object_or_404(Session, id=session_id, mentor=mentor_profile)

    return render(request, 'dashboard/mentor_session_detail.html', {
        'mentor_profile': mentor_profile,
        'session': session
    })


@login_required
def mentor_session_set_status(request, session_id):
    """Allow mentor to mark a session as completed or cancelled.

    Only the mentor who owns the session can change its status. This view expects a POST
    with 'action' equal to 'completed' or 'cancelled'. It updates the session, notifies
    the mentee by email, and redirects back to the mentor session detail page.
    """
    try:
        mentor_profile = request.user.mentor_profile
    except MentorProfile.DoesNotExist:
        messages.error(request, "You don't have a mentor profile. Please contact an admin.")
        return redirect('home')

    session = get_object_or_404(Session, id=session_id, mentor=mentor_profile)

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('mentor_session_detail', session_id=session.id)

    action = request.POST.get('action')
    if action not in ['completed', 'cancelled']:
        messages.error(request, "Invalid action.")
        return redirect('mentor_session_detail', session_id=session.id)

    old_status = session.status
    session.status = action
    # If cancelled, payment_status might remain as-is; for now we don't alter payment fields
    session.save()

    # Notify mentee and mentor
    try:
        subject = f'Session {session.get_status_display()} - CodeMentorHub'
        if session.status == 'cancelled':
            message = (
                f'Hello {session.mentee.first_name or session.mentee.username},\n\n'
                f'We’re sorry to inform you that your session with {session.mentor.full_name} on {session.session_date} at {session.session_time} was cancelled by the mentor.\n\n'
                f'A refund will be credited to your original payment method within 3 business days.\n\n'
                f'If you have any questions, please contact support.\n\n'
                f'Best,\nCodeMentorHub Team'
            )
        else:
            message = (
                f'Hello {session.mentee.first_name or session.mentee.username},\n\n'
                f'Your session with {session.mentor.full_name} scheduled on {session.session_date} at {session.session_time} has been marked as {session.get_status_display().lower()}.\n\n'
                f'If you have any questions, please contact the mentor or support.\n\n'
                f'Best,\nCodeMentorHub Team'
            )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [session.mentee.email],
            fail_silently=True,
        )
    except Exception:
        # Fail silently for email sending in development
        pass

    messages.success(request, f"Session marked as {session.get_status_display().lower()}.")
    return redirect('mentor_session_detail', session_id=session.id)

def send_session_confirmation_emails(session):
    """Send confirmation emails to both mentor and mentee"""
    try:
        # Email to mentee
        send_mail(
            'Session Booked Successfully - CodeMentorHub',
            f'Hello {session.mentee.first_name or session.mentee.username},\n\n'
            f'Your session with {session.mentor.full_name} has been confirmed!\n\n'
            f'Session Details:\n'
            f'Date: {session.session_date}\n'
            f'Time: {session.session_time}\n'
            f'Duration: {session.duration_minutes} minutes\n'
            f'Meeting Link: {session.meeting_link}\n\n'
            f'Please join the meeting 5 minutes before the scheduled time.\n\n'
            f'Best regards,\nCodeMentorHub Team',
            settings.DEFAULT_FROM_EMAIL,
            [session.mentee.email],
            fail_silently=False,
        )
        
        # Email to mentor (only if mentor has a linked user with email)
        if getattr(session.mentor, 'user', None) and session.mentor.user and session.mentor.user.email:
            send_mail(
                'New Session Booked - CodeMentorHub',
                f'Hello {session.mentor.full_name},\n\n'
                f'You have a new session booked with {session.mentee.first_name or session.mentee.username}!\n\n'
                f'Session Details:\n'
                f'Date: {session.session_date}\n'
                f'Time: {session.session_time}\n'
                f'Duration: {session.duration_minutes} minutes\n'
                f'Meeting Link: {session.meeting_link}\n\n'
                f'Please be ready 5 minutes before the scheduled time.\n\n'
                f'Best regards,\nCodeMentorHub Team',
                settings.DEFAULT_FROM_EMAIL,
                [session.mentor.user.email],
                fail_silently=False,
            )
    except Exception as e:
        print(f"Email sending failed: {e}")


# Admin Sessions Management

@staff_required
def admin_sessions(request):
    """Admin view to see all booked sessions with user details."""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')
    
    # Get all sessions
    sessions = Session.objects.select_related('mentor', 'mentor__user', 'mentee').order_by('-session_date', '-session_time')
    
    # Filter by status
    if status_filter in ['pending', 'confirmed', 'completed', 'cancelled']:
        sessions = sessions.filter(status=status_filter)
    
    # Search by mentor name, mentee username/email
    if search:
        sessions = sessions.filter(
            Q(mentor__full_name__icontains=search) |
            Q(mentee__username__icontains=search) |
            Q(mentee__email__icontains=search) |
            Q(mentee__first_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(sessions, 20)
    page = request.GET.get('page')
    sessions_page = paginator.get_page(page)
    
    return render(request, 'admin/sessions.html', {
        'sessions': sessions_page,
        'search': search,
        'status_filter': status_filter
    })


@staff_required
def admin_session_set_status(request, session_id):
    """Allow admin to mark a session as completed or change its status.
    Also handles manual Google Meet link submission when confirming a session.
    """
    session = get_object_or_404(Session, id=session_id)
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('admin_sessions')
    
    action = request.POST.get('action')
    meeting_link = request.POST.get('meeting_link', '').strip()
    
    if action not in ['completed', 'confirmed', 'pending', 'cancelled']:
        messages.error(request, "Invalid action.")
        return redirect('admin_sessions')
    
    old_status = session.status
    session.status = action
    
    # Handle meeting link submission when confirming
    if session.status == 'confirmed' and meeting_link:
        session.admin_provided_link = meeting_link
        session.link_provided_at = timezone.now()
    
    # Generate Google Meet link only if no link provided and status is confirmed
    if session.status == 'confirmed' and not session.admin_provided_link and not session.meeting_link:
        session.generate_meeting_link()
    
    session.save()
    
    # Notify mentee and mentor about status change via email
    try:
        if session.mentee.email:
            subject = f'Session {session.get_status_display()} - CodeMentorHub'
            
            if session.status == 'completed':
                message = (
                    f'Hello {session.mentee.first_name or session.mentee.username},\n\n'
                    f'Your session with {session.mentor.full_name} on {session.session_date} at {session.session_time} has been marked as completed.\n\n'
                    f'Thank you for using CodeMentorHub!\n\n'
                    f'Best regards,\nCodeMentorHub Team'
                )
            elif session.status == 'cancelled':
                message = (
                    f'Hello {session.mentee.first_name or session.mentee.username},\n\n'
                    f'Your session with {session.mentor.full_name} on {session.session_date} at {session.session_time} has been cancelled.\n\n'
                    f'If you have any questions, please contact support.\n\n'
                    f'Best regards,\nCodeMentorHub Team'
                )
            elif session.status == 'confirmed':
                # Get the meeting link (either admin-provided or auto-generated)
                display_link = session.get_meeting_link
                message = (
                    f'Hello {session.mentee.first_name or session.mentee.username},\n\n'
                    f'Your session with {session.mentor.full_name} has been confirmed!\n\n'
                    f'Session Details:\n'
                    f'Date: {session.session_date}\n'
                    f'Time: {session.session_time}\n'
                    f'Duration: {session.duration_minutes} minutes\n'
                    f'Meeting Link: {display_link}\n\n'
                    f'Please join the meeting 5 minutes before the scheduled time.\n\n'
                    f'Best regards,\nCodeMentorHub Team'
                )
            else:
                message = (
                    f'Hello {session.mentee.first_name or session.mentee.username},\n\n'
                    f'Your session with {session.mentor.full_name} on {session.session_date} at {session.session_time} status has been updated to {session.get_status_display()}.\n\n'
                    f'Best regards,\nCodeMentorHub Team'
                )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [session.mentee.email],
                fail_silently=True,
            )
        
        # Send email to mentor as well if confirmed
        if session.status == 'confirmed' and getattr(session.mentor, 'user', None) and session.mentor.user and session.mentor.user.email:
            display_link = session.get_meeting_link
            mentor_message = (
                f'Hello {session.mentor.full_name},\n\n'
                f'Your session with {session.mentee.first_name or session.mentee.username} has been confirmed!\n\n'
                f'Session Details:\n'
                f'Date: {session.session_date}\n'
                f'Time: {session.session_time}\n'
                f'Duration: {session.duration_minutes} minutes\n'
                f'Meeting Link: {display_link}\n\n'
                f'Please join the meeting 5 minutes before the scheduled time.\n\n'
                f'Best regards,\nCodeMentorHub Team'
            )
            send_mail(
                'Session Confirmed - CodeMentorHub',
                mentor_message,
                settings.DEFAULT_FROM_EMAIL,
                [session.mentor.user.email],
                fail_silently=True,
            )
    except Exception:
        pass
    
    messages.success(request, f"Session marked as {session.get_status_display()}. All parties have been notified.")
    return redirect('admin_sessions')


@login_required
def hire_developer_view(request):
    """View for the 'Hire a Developer' page."""
    if request.method == 'POST':
        form = HireDeveloperForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your request to hire a developer has been submitted successfully!")
            return redirect('home')
    else:
        form = HireDeveloperForm()

    return render(request, 'hire_developer.html', { 'form': form })


@staff_required
def hire_developer_data_view(request):
    data=hire_developer.objects.all()
    return render(request, 'admin/hire_developer_data.html',{'data':data})

@staff_required
def contact_messages_view(request):
    messages = ContactMessage.objects.all()
    return render(request, 'admin/contact_messages.html', {'messages': messages})


@staff_required
def admin_quiz_manage(request):
    """List quiz categories and provide links to add/manage them."""
    categories = Category.objects.all().order_by('name')
    return render(request, 'admin/quiz_list.html', {'categories': categories})


@staff_required
def admin_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('admin_quiz_manage')
    else:
        form = CategoryForm()
    return render(request, 'admin/quiz_add_category.html', {'form': form})


@staff_required
def admin_category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    questions = category.questions.all()
    return render(request, 'admin/quiz_category_detail.html', {'category': category, 'questions': questions})


@staff_required
def admin_add_question(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    else:
        category = None

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            formset = OptionFormSet(request.POST, instance=question)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Question and options saved.')
                return redirect('admin_category_detail', category_id=question.category.id)
            else:
                # If options invalid, delete question to avoid orphan
                question.delete()
        else:
            formset = OptionFormSet(request.POST)
    else:
        initial = {}
        if category:
            initial['category'] = category
        form = QuestionForm(initial=initial)
        formset = OptionFormSet()

    return render(request, 'admin/quiz_add_question.html', {
        'form': form,
        'formset': formset,
        'category': category
    })


@login_required
def quiz_categories(request):
    """List available quiz categories for users to take."""
    categories = Category.objects.all().order_by('name')
    return render(request, 'quiz/categories.html', {'categories': categories})


@login_required
def take_test(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    questions = category.questions.prefetch_related('options').all()

    if request.method == 'POST':
        # Create attempt record
        total_marks = sum(q.marks for q in questions)
        attempt = TestAttempt.objects.create(user=request.user, category=category, total_marks=total_marks)
        score = 0

        for q in questions:
            field_name = f"q_{q.id}"
            selected_option_id = request.POST.get(field_name)
            selected_option = None
            marks_awarded = 0
            is_correct = False
            if selected_option_id:
                try:
                    selected_option = Option.objects.get(id=int(selected_option_id), question=q)
                    if selected_option.is_correct:
                        marks_awarded = q.marks
                        is_correct = True
                except Option.DoesNotExist:
                    selected_option = None

            AttemptAnswer.objects.create(
                attempt=attempt,
                question=q,
                selected_option=selected_option,
                is_correct=is_correct,
                marks_awarded=marks_awarded
            )
            score += marks_awarded

        attempt.score = score
        attempt.completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        return redirect('test_result', attempt_id=attempt.id)

    return render(request, 'quiz/take_test.html', {'category': category, 'questions': questions})


@login_required
def test_result(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    answers = attempt.answers.select_related('question', 'selected_option').all()
    return render(request, 'quiz/result.html', {'attempt': attempt, 'answers': answers})


# Delete Category View
@staff_required
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
        return redirect('admin_quiz_manage')
    return render(request, 'admin/quiz_delete_category.html', {'category': category})


# Edit Category View
@staff_required
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_category_detail', category_id=category.id)
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/quiz_edit_category.html', {'form': form, 'category': category})


# Edit Question View
@staff_required
def admin_edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            formset = OptionFormSet(request.POST, instance=question)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Question updated successfully.')
                return redirect('admin_category_detail', category_id=question.category.id)
        else:
            formset = OptionFormSet(request.POST, instance=question)
    else:
        form = QuestionForm(instance=question)
        formset = OptionFormSet(instance=question)

    return render(request, 'admin/quiz_edit_question.html', {
        'form': form,
        'formset': formset,
        'question': question,
        'category': question.category
    })


# Delete Question View
@staff_required
def admin_delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    category_id = question.category.id
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully.')
        return redirect('admin_category_detail', category_id=category_id)
    return render(request, 'admin/quiz_delete_question.html', {'question': question})