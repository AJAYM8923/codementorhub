from django.core.management.base import BaseCommand
from main.models import Skill

class Command(BaseCommand):
    help = 'Add sample skills to the database'

    def handle(self, *args, **options):
        sample_skills = [
            'Python', 'Django', 'JavaScript', 'React', 'Node.js', 'Vue.js',
            'HTML', 'CSS', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB',
            'Git', 'Docker', 'AWS', 'Linux', 'API Development', 'REST APIs',
            'GraphQL', 'Machine Learning', 'Data Science', 'Web Scraping',
            'Testing', 'CI/CD', 'DevOps', 'Frontend Development', 'Backend Development',
            'Full Stack Development', 'Mobile Development', 'iOS', 'Android',
            'Flutter', 'React Native', 'C++', 'Java', 'C#', 'PHP', 'Ruby',
            'Go', 'Rust', 'TypeScript', 'Angular', 'Express.js', 'FastAPI',
            'Flask', 'Spring Boot', 'Laravel', 'Rails', 'Firebase', 'Redis'
        ]
        
        created_count = 0
        for skill_name in sample_skills:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            if created:
                created_count += 1
                self.stdout.write(f'Created skill: {skill_name}')
            else:
                self.stdout.write(f'Skill already exists: {skill_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(sample_skills)} skills. Created {created_count} new skills.')
        )
