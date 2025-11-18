from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Add email addresses to existing users who don\'t have one'

    def add_arguments(self, parser):
        parser.add_argument('--interactive', action='store_true', help='Interactively add emails to users')

    def handle(self, *args, **options):
        users_without_email = User.objects.filter(email='')
        
        if not users_without_email.exists():
            self.stdout.write(self.style.SUCCESS('All users already have email addresses!'))
            return
        
        self.stdout.write(f'Found {users_without_email.count()} users without email addresses:')
        
        for user in users_without_email:
            self.stdout.write(f'- {user.username} (Full name: {user.first_name or "Not set"})')
        
        if options['interactive']:
            self.stdout.write('\nYou can add email addresses to these users through the Django admin panel or by updating them programmatically.')
            self.stdout.write('For security reasons, we recommend users add their own email addresses through a profile update feature.')
        
        self.stdout.write('\nTo add emails, you can:')
        self.stdout.write('1. Use Django admin panel')
        self.stdout.write('2. Create a profile update feature in your app')
        self.stdout.write('3. Manually update users via Python shell')
