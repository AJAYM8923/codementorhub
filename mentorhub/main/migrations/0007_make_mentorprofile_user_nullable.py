from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_contactmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentorprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentor_profile', to='auth.user'),
        ),
    ]


