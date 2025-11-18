from django.contrib import admin
from django import forms
from .models import PasswordResetToken, Skill, MentorProfile, MenteeProfile, Session
from .models import Category, Question, Option

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'headline', 'application_status', 'is_approved', 'years_of_experience', 'hourly_rate', 'created_at']
    list_filter = ['application_status', 'is_approved', 'years_of_experience', 'created_at']
    search_fields = ['full_name', 'headline', 'bio', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'full_name', 'profile_picture', 'bio', 'headline', 'location', 'linkedin_url', 'github_url')
        }),
        ('Professional Details', {
            'fields': ('skills', 'years_of_experience', 'hourly_rate', 'session_duration', 'available_for', 'availability')
        }),
        ('Application Status', {
            'fields': ('application_status', 'is_approved', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['skills']

    # Use a custom form so the admin doesn't treat availability as required
    class MentorProfileForm(forms.ModelForm):
        availability = forms.JSONField(required=False, help_text="JSON schedule, e.g. {'mon': ['09:00','14:00']}" )

        class Meta:
            model = MentorProfile
            fields = '__all__'

    form = MentorProfileForm

    actions = ['approve_mentors', 'reject_mentors']

    def _default_availability(self):
        # Simple default availability: Mon-Fri with three time slots
        return {
            'mon': ['09:00', '11:00', '14:00'],
            'tue': ['09:00', '11:00', '14:00'],
            'wed': ['09:00', '11:00', '14:00'],
            'thu': ['09:00', '11:00', '14:00'],
            'fri': ['09:00', '11:00', '14:00'],
        }

    def approve_mentors(self, request, queryset):
        # Iterate so we can auto-fill availability when missing
        approved_count = 0
        for mentor in queryset:
            if not mentor.availability:
                mentor.availability = self._default_availability()
            mentor.application_status = 'approved'
            mentor.is_approved = True
            mentor.save()
            approved_count += 1
        self.message_user(request, f'{approved_count} mentor(s) approved successfully.')
    approve_mentors.short_description = "Approve selected mentors"
    
    def reject_mentors(self, request, queryset):
        updated = queryset.update(application_status='rejected', is_approved=False)
        self.message_user(request, f'{updated} mentor(s) rejected.')
    reject_mentors.short_description = "Reject selected mentors"

    def save_model(self, request, obj, form, change):
        """When saving a single MentorProfile in admin, ensure availability exists if admin approves.

        This allows admins to approve a mentor without manually entering availability; the system
        will populate a sensible default schedule when missing.
        """
        if obj.is_approved and not obj.availability:
            obj.availability = self._default_availability()
        super().save_model(request, obj, form, change)

@admin.register(MenteeProfile)
class MenteeProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'current_level', 'user', 'created_at']
    list_filter = ['current_level', 'created_at']
    search_fields = ['full_name', 'interests', 'goal', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'full_name', 'profile_picture', 'interests', 'current_level', 'goal')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'used']
    list_filter = ['used', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'created_at']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['mentor', 'mentee', 'session_date', 'session_time', 'status', 'amount_paid']
    list_filter = ['status', 'session_date', 'created_at']
    search_fields = ['mentor__full_name', 'mentee__username', 'mentee__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Session Details', {
            'fields': ('mentor', 'mentee', 'session_date', 'session_time', 'duration_minutes', 'status')
        }),
        ('Meeting Info', {
            'fields': ('meeting_link', 'meeting_notes')
        }),
        ('Payment', {
            'fields': ('amount_paid', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'category', 'marks', 'created_at']
    list_filter = ['category']
    search_fields = ['text']
    inlines = [OptionInline]
