from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Create your models here.

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    def is_valid(self):
        # Token is valid for 1 hour
        return not self.used and (timezone.now() - self.created_at) < timedelta(hours=1)
    
    def __str__(self):
        return f"Reset token for {self.user.username}"

class Skill(models.Model):
    name = models.CharField(max_length=35, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class MentorProfile(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    SESSION_DURATION_CHOICES = [
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '60 minutes'),
        (90, '90 minutes'),
        (120, '120 minutes'),
    ]
    
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='mentor_profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, help_text="Short intro about your journey")
    headline = models.CharField(max_length=100, help_text="Short tagline like 'Senior Django Developer'")
    location = models.CharField(max_length=100, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    
    # Professional Details
    skills = models.ManyToManyField(Skill, related_name='mentors')
    years_of_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Years of professional experience"
    )
    hourly_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Rate per session/hour"
    )
    availability = models.JSONField(
        default=dict,
        help_text="JSON format: {'mon': ['10:00', '15:00'], 'wed': ['14:00']}"
    )
    session_duration = models.IntegerField(
        choices=SESSION_DURATION_CHOICES,
        default=60,
        help_text="Default session duration in minutes"
    )
    available_for = models.TextField(
        help_text="e.g., 'Career Guidance, Code Review, Debugging Help'"
    )
    
    # Application & Approval Fields
    is_approved = models.BooleanField(default=False)
    application_status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.headline}"
    
    @property
    def is_available(self):
        """Check if mentor is available for booking"""
        return self.is_approved and self.application_status == 'approved'
    
    def get_skills_display(self):
        """Return comma-separated skills"""
        return ", ".join([skill.name for skill in self.skills.all()])


class MenteeProfile(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    # Personal Info
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentee_profile')
    full_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='mentee_profiles/', blank=True, null=True)
    interests = models.TextField(
        help_text="e.g., 'Web Development, APIs, Django'"
    )
    current_level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='beginner'
    )
    goal = models.TextField(
        help_text="e.g., 'Get a backend job', 'Build my own project'"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.get_current_level_display()}"


class Session(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Core booking info
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='sessions')
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_sessions')
    
    # Session details
    session_date = models.DateField()
    session_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Meeting details
    meeting_link = models.URLField(blank=True, null=True)
    meeting_notes = models.TextField(blank=True, null=True)
    
    # Admin-provided meeting link (manual)
    admin_provided_link = models.URLField(blank=True, null=True, help_text="Link provided by admin when confirming session")
    link_provided_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when admin provided the link")
    
    # Payment info
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['session_date', 'session_time']
        unique_together = ['mentor', 'session_date', 'session_time']
    
    def __str__(self):
        return f"{self.mentor.full_name} - {self.mentee.username} on {self.session_date} at {self.session_time}"
    
    @property
    def get_meeting_link(self):
        """Return admin-provided link if available, otherwise return auto-generated link"""
        return self.admin_provided_link or self.meeting_link
    
    @property
    def session_datetime(self):
        """Combine date and time into a datetime object"""
        from django.utils import timezone
        from datetime import datetime
        return timezone.make_aware(
            datetime.combine(self.session_date, self.session_time)
        )
    
    @property
    def is_upcoming(self):
        """Check if session is in the future"""
        from django.utils import timezone
        return self.session_datetime > timezone.now()
    
    def generate_meeting_link(self):
        """
        Generate an actual working Google Meet link for the session
        Method 2 (Google Calendar API) is primary method
        Method 1 (SHA256 hashing) is fallback
        """
        try:
            # Try Method 2: Google Calendar API (Primary)
            from main.google_meet_helper import create_meet_link
            self.meeting_link = create_meet_link(self)
            print(f"✅ Using Google Calendar API - Meeting link: {self.meeting_link}")
        except Exception as e:
            # Fallback to Method 1: SHA256 hashing
            print(f"⚠️ Google Calendar API failed: {e}. Using fallback method.")
            import hashlib
            meeting_seed = f"codementor-{self.mentor.id}-{self.mentee.id}-{self.session_date}-{self.session_time}"
            meeting_hash = hashlib.sha256(meeting_seed.encode()).hexdigest()[:16]
            meeting_id = f"codementor-{self.id}-{meeting_hash}"
            self.meeting_link = f"https://meet.google.com/{meeting_id}"
            print(f"⚠️ Using fallback method - Meeting link: {self.meeting_link}")
        
        self.save()
        return self.meeting_link

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"

class hire_developer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.IntegerField()
    message = models.TextField()
    project_type = models.CharField(max_length=100)
    project_heading = models.CharField(max_length=200)
    project_details = models.TextField()
    deadline = models.DateField()
    

    def __str__(self):
        return f"Hire Request from {self.name} - {self.email}"


# Quiz / Test models
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name}: {self.text[:50]}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} - {self.text[:50]}{' (correct)' if self.is_correct else ''}"


class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def performance_percent(self):
        if not self.total_marks:
            return 0
        return round((self.score / self.total_marks) * 100, 2)

    def performance_text(self):
        p = self.performance_percent()
        if p >= 90:
            return 'Excellent'
        if p >= 75:
            return 'Good'
        if p >= 50:
            return 'Average'
        return 'Needs Improvement'

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.score}/{self.total_marks}"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Attempt {self.attempt.id} - Q{self.question.id} - {self.marks_awarded}"