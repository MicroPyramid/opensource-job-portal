# Generated migration for adding EM user type and job_title field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peeldb', '0062_add_savedjobs_model'),
    ]

    operations = [
        # Add job_title field to User model
        migrations.AddField(
            model_name='user',
            name='job_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                help_text="Job title/role (e.g., 'Senior Recruiter', 'HR Manager', 'Talent Acquisition Lead')"
            ),
        ),

        # Modify user_type choices to include EM (keeping old types temporarily for migration)
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(
                choices=[
                    ('JS', 'Job Seeker'),
                    ('RR', 'Recruiter'),
                    ('RA', 'Recruiter Admin'),
                    ('AA', 'Agency Admin'),
                    ('AR', 'Agency Recruiter'),
                    ('EM', 'Employer'),  # NEW TYPE
                ],
                max_length=10
            ),
        ),
    ]
