
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentorhub.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import MentorProfile, Skill
from decimal import Decimal

# Create Skills
skill_python, _ = Skill.objects.get_or_create(name="Python")
skill_django, _ = Skill.objects.get_or_create(name="Django")

# Create Mentor User
username = "mentor_dave"
if not User.objects.filter(username=username).exists():
    user = User.objects.create_user(username=username, email="dave@example.com", password="password123", first_name="Dave")
    
    # Create Profile
    MentorProfile.objects.create(
        user=user,
        full_name="Dave The Mentor",
        headline="Expert Django Backend Dev",
        bio="I helps you build things.",
        years_of_experience=10,
        hourly_rate=Decimal("50.00"),
        session_duration=60,
        is_approved=True,
        application_status='approved'
    )
    
    print("Mentor 'Dave' created successfully.")
    
    # Add skills
    mentor = MentorProfile.objects.get(user=user)
    mentor.skills.add(skill_python, skill_django)
    mentor.save()
else:
    print("Mentor 'Dave' already exists.")
