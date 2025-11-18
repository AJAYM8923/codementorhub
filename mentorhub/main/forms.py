from .models import hire_developer, ContactMessage,Skill, Category, Question, Option
from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django.forms import ModelForm
from django.forms import inlineformset_factory

PROJECT_TYPE_CHOICES = [
    ("web_development", "Web Development"),
    ("mobile_app", "Mobile App"),
    ("data_science", "Data Science"),
    ("other", "Other"),
]

class HireDeveloperForm(ModelForm):
    project_type = forms.ChoiceField(choices=PROJECT_TYPE_CHOICES)

    class Meta:
        model = hire_developer
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'you@example.com',
                'required': 'required'
            }),
            'number': forms.TextInput(attrs={
                'inputmode': 'tel',
                'pattern': r'^\+?[0-9\-\s]{7,15}$',
                'placeholder': '+1 555-123-4567',
                'required': 'required'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'required': 'required'
            }),
            'name': forms.TextInput(attrs={'required': 'required'}),
            'project_heading': forms.TextInput(attrs={'required': 'required'}),
            'project_details': forms.Textarea(attrs={'rows': 4, 'required': 'required'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now().date():
            raise forms.ValidationError('Deadline must be in the future.')
        return deadline


class ContactForm(ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'email': forms.EmailInput(attrs={'required': 'required'}),
            'name': forms.TextInput(attrs={'required': 'required'}),
            'subject': forms.TextInput(attrs={'required': 'required'}),
            'message': forms.Textarea(attrs={'rows': 4, 'required': 'required'}),
        }

class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = ['name']


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'text', 'marks']


class OptionForm(ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']


OptionFormSet = inlineformset_factory(Question, Option, form=OptionForm, extra=4, can_delete=True)